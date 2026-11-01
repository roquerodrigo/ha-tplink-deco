"""Tests for the integration package entry points (``__init__``)."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from datetime import timedelta
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_USERNAME,
)
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    mock_device_registry,
)

from custom_components.tplink_deco import (
    async_remove_config_entry_device,
)
from custom_components.tplink_deco.api import TpLinkDecoSnapshot
from custom_components.tplink_deco.const import DOMAIN

from .factories import make_client, make_node

if TYPE_CHECKING:
    import pytest
    from homeassistant.core import HomeAssistant

ENTRY_ID = "tplink_deco_entry"


@dataclass
class _FakeDevice:
    """Minimal stand-in for a Home Assistant ``DeviceEntry``."""

    id: str
    config_entries: set[str]
    connections: set[tuple[str, str]] = field(default_factory=set)
    identifiers: set[tuple[str, str]] = field(default_factory=set)


async def _can_remove(
    snapshot: TpLinkDecoSnapshot | None,
    identifiers: set[tuple[str, str]],
) -> bool:
    """Run ``async_remove_config_entry_device`` for a device with ``identifiers``."""
    entry = MagicMock()
    entry.runtime_data.coordinator.data = snapshot
    device = _FakeDevice(id="dev", config_entries={ENTRY_ID}, identifiers=identifiers)
    return await async_remove_config_entry_device(MagicMock(), entry, device)


async def test_remove_rejected_for_online_client() -> None:
    """A currently connected client cannot be removed."""
    client = make_client(online=True)
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)

    assert await _can_remove(snapshot, {(DOMAIN, client.mac)}) is False


async def test_remove_allowed_for_offline_client() -> None:
    """A client the router still remembers but is offline can be removed."""
    client = make_client(online=False)
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)

    assert await _can_remove(snapshot, {(DOMAIN, client.mac)}) is True


async def test_remove_rejected_for_mesh_node() -> None:
    """A mesh node reported by the router cannot be removed."""
    node = make_node()
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None)

    assert await _can_remove(snapshot, {(DOMAIN, node.mac)}) is False


async def test_remove_allowed_for_absent_device() -> None:
    """A device no longer present in the snapshot can be removed."""
    snapshot = TpLinkDecoSnapshot(
        clients=[make_client(online=True)], nodes=[], performance=None
    )

    assert await _can_remove(snapshot, {(DOMAIN, "FF:FF:FF:FF:FF:FF")}) is True


async def test_remove_allowed_without_snapshot() -> None:
    """With no coordinator data yet, removal is permitted."""
    assert await _can_remove(None, {(DOMAIN, "AA:BB:CC:DD:EE:01")}) is True


async def test_remove_allowed_for_device_without_deco_identifier() -> None:
    """A device carrying no tplink_deco identifier can always be removed."""
    snapshot = TpLinkDecoSnapshot(
        clients=[make_client(online=True)], nodes=[], performance=None
    )

    assert await _can_remove(snapshot, {("other", "node-1")}) is True


def _setup_entry() -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "192.168.0.1",
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "secret",
        },
        unique_id="192.168.0.1",
    )


async def test_setup_applies_the_configured_polling_fields(
    hass: HomeAssistant,
    snapshot: TpLinkDecoSnapshot,
) -> None:
    """The stored update interval and request timeout reach coordinator and client."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "192.168.0.1",
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "secret",
            CONF_SCAN_INTERVAL: 90,
            CONF_TIMEOUT: 45,
        },
        unique_id="192.168.0.1",
    )
    entry.add_to_hass(hass)

    with patch("custom_components.tplink_deco.TpLinkDecoApiClient") as client_class:
        client_class.return_value.get_snapshot.return_value = snapshot
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert client_class.call_args.kwargs[CONF_TIMEOUT] == 45
        assert entry.runtime_data.coordinator.update_interval == timedelta(seconds=90)

        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()


async def test_setup_registers_nodes_before_client_devices(
    hass: HomeAssistant,
    snapshot: TpLinkDecoSnapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A client never references a node device that does not exist yet."""
    entry = _setup_entry()
    entry.add_to_hass(hass)

    with patch("custom_components.tplink_deco.TpLinkDecoApiClient") as client_class:
        client_class.return_value.get_snapshot.return_value = snapshot
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        registry = dr.async_get(hass)
        node = registry.async_get_device_by_identifier(
            (DOMAIN, snapshot.nodes[0].mac), entry.entry_id
        )
        client = registry.async_get_child_device_by_identifier(
            (DOMAIN, snapshot.clients[0].mac), entry.entry_id
        )
        assert node is not None
        assert client is not None
        assert client.parent_device_id == node.id
        assert "Not adding entity" not in caplog.text

        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()


async def test_setup_converts_existing_client_device_in_place(
    hass: HomeAssistant,
    snapshot: TpLinkDecoSnapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A client registered before child devices keeps its id, name and entities."""
    entry = _setup_entry()
    entry.add_to_hass(hass)
    node = dr.DeviceEntry(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, snapshot.nodes[0].mac)},
        name="Living Room",
    )
    client_mac = snapshot.clients[0].mac
    client = dr.DeviceEntry(
        area_id="office",
        config_entry_id=entry.entry_id,
        connections={(CONNECTION_NETWORK_MAC, client_mac.lower())},
        identifiers={(DOMAIN, client_mac)},
        name="Phone",
        name_by_user="My Phone",
        via_device_id=node.id,
    )
    registry = mock_device_registry(hass, {node.id: node, client.id: client})
    entities = er.async_get(hass)
    tracker = entities.async_get_or_create(
        "device_tracker",
        DOMAIN,
        f"{client_mac}_tracker",
        config_entry=entry,
        device_id=client.id,
    )

    with patch("custom_components.tplink_deco.TpLinkDecoApiClient") as client_class:
        client_class.return_value.get_snapshot.return_value = snapshot
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        converted = registry.async_get_child_device_by_identifier(
            (DOMAIN, client_mac), entry.entry_id
        )
        assert converted is not None
        assert converted.id == client.id
        assert converted.parent_device_id == node.id
        assert converted.name_by_user == "My Phone"
        assert converted.area_id == "office"
        tracker_after = entities.async_get(tracker.entity_id)
        assert tracker_after is not None
        assert tracker_after.device_id == client.id
        assert "Not adding entity" not in caplog.text

        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()


async def test_setup_keeps_offline_child_clients_after_reload(
    hass: HomeAssistant,
    snapshot: TpLinkDecoSnapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A reload finds the child device of an offline client and keeps its entities."""
    entry = _setup_entry()
    entry.add_to_hass(hass)
    offline_snapshot = TpLinkDecoSnapshot(
        clients=[dataclasses.replace(snapshot.clients[0], online=False)],
        nodes=snapshot.nodes,
        performance=snapshot.performance,
    )

    with patch("custom_components.tplink_deco.TpLinkDecoApiClient") as client_class:
        client_class.return_value.get_snapshot.return_value = snapshot
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        client_entity_ids = {
            registered.entity_id
            for registered in er.async_entries_for_config_entry(
                er.async_get(hass), entry.entry_id
            )
            if registered.unique_id.startswith(snapshot.clients[0].mac)
        }
        assert client_entity_ids

        client_class.return_value.get_snapshot.return_value = offline_snapshot
        assert await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()

        states = [hass.states.get(entity_id) for entity_id in client_entity_ids]
        assert all(state and not state.attributes.get("restored") for state in states)
        assert "Not adding entity" not in caplog.text

        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()


async def test_setup_turns_child_client_into_node_when_it_joins_the_mesh(
    hass: HomeAssistant,
    snapshot: TpLinkDecoSnapshot,
) -> None:
    """A client that became a mesh node stops being a child device, without errors."""
    entry = _setup_entry()
    entry.add_to_hass(hass)
    registry = dr.async_get(hass)
    master_mac = snapshot.nodes[0].mac
    new_node_mac = "11:22:33:44:55:77"
    master_device = registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, master_mac)},
    )
    registry.async_get_or_create_child(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, new_node_mac)},
        parent_device_id=master_device.id,
    )
    grown_snapshot = TpLinkDecoSnapshot(
        clients=snapshot.clients,
        nodes=[*snapshot.nodes, make_node(mac=new_node_mac, role="slave")],
        performance=snapshot.performance,
    )

    with patch("custom_components.tplink_deco.TpLinkDecoApiClient") as client_class:
        client_class.return_value.get_snapshot.return_value = grown_snapshot
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert entry.state is ConfigEntryState.LOADED
        assert (
            registry.async_get_child_device_by_identifier(
                (DOMAIN, new_node_mac), entry.entry_id
            )
            is None
        )
        assert (
            registry.async_get_device_by_identifier(
                (DOMAIN, new_node_mac), entry.entry_id
            )
            is not None
        )

        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()


async def test_client_absent_at_startup_is_converted_when_it_returns(
    hass: HomeAssistant,
    snapshot: TpLinkDecoSnapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A stored client the router stopped listing is nested once it reconnects."""
    entry = _setup_entry()
    entry.add_to_hass(hass)
    node = dr.DeviceEntry(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, snapshot.nodes[0].mac)},
    )
    client_mac = snapshot.clients[0].mac
    client = dr.DeviceEntry(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, client_mac)},
        via_device_id=node.id,
    )
    registry = mock_device_registry(hass, {node.id: node, client.id: client})
    empty_snapshot = TpLinkDecoSnapshot(
        clients=[],
        nodes=snapshot.nodes,
        performance=snapshot.performance,
    )

    with patch("custom_components.tplink_deco.TpLinkDecoApiClient") as client_class:
        client_class.return_value.get_snapshot.return_value = empty_snapshot
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        assert (
            registry.async_get_device_by_identifier(
                (DOMAIN, client_mac), entry.entry_id
            )
            is not None
        )

        entry.runtime_data.coordinator.async_set_updated_data(snapshot)
        await hass.async_block_till_done()

        converted = registry.async_get_child_device_by_identifier(
            (DOMAIN, client_mac), entry.entry_id
        )
        assert converted is not None
        assert converted.id == client.id
        assert converted.parent_device_id == node.id
        assert "Not adding entity" not in caplog.text

        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()


async def test_setup_drops_the_removed_link_devices_option(
    hass: HomeAssistant,
    snapshot: TpLinkDecoSnapshot,
) -> None:
    """An entry that disabled the removed option migrates and links its nodes."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={**_setup_entry().data, "link_devices_by_mac": False},
        minor_version=1,
        unique_id="192.168.0.1",
        version=1,
    )
    entry.add_to_hass(hass)

    with patch("custom_components.tplink_deco.TpLinkDecoApiClient") as client_class:
        client_class.return_value.get_snapshot.return_value = snapshot
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert entry.state is ConfigEntryState.LOADED
        assert entry.minor_version == 2
        assert "link_devices_by_mac" not in entry.data
        node_mac = snapshot.nodes[0].mac
        node = dr.async_get(hass).async_get_device_by_identifier(
            (DOMAIN, node_mac), entry.entry_id
        )
        assert node is not None
        assert (CONNECTION_NETWORK_MAC, node_mac.lower()) in node.connections

        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
