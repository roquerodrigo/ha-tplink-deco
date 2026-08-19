"""Tests for the integration package entry points (``__init__``)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_USERNAME,
)
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.tplink_deco import (
    _unmerge_devices,
    async_remove_config_entry_device,
)
from custom_components.tplink_deco.api import TpLinkDecoSnapshot
from custom_components.tplink_deco.const import DOMAIN

from .factories import make_client, make_node

if TYPE_CHECKING:
    import pytest
    from homeassistant.core import HomeAssistant

ENTRY_ID = "tplink_deco_entry"
OTHER_ENTRY_ID = "other_integration_entry"


@dataclass
class _FakeDevice:
    """Minimal stand-in for a Home Assistant ``DeviceEntry``."""

    id: str
    config_entries: set[str]
    connections: set[tuple[str, str]] = field(default_factory=set)
    identifiers: set[tuple[str, str]] = field(default_factory=set)


def _run(
    monkeypatch: pytest.MonkeyPatch,
    devices: list[_FakeDevice],
) -> MagicMock:
    """Run ``_unmerge_devices`` against the given devices and return the registry."""
    registry = MagicMock()
    registry.async_update_device = MagicMock()
    monkeypatch.setattr(
        "custom_components.tplink_deco.dr.async_get",
        lambda _hass: registry,
    )
    monkeypatch.setattr(
        "custom_components.tplink_deco.dr.async_entries_for_config_entry",
        lambda _registry, _entry_id: list(devices),
    )
    entry = MagicMock()
    entry.entry_id = ENTRY_ID
    _unmerge_devices(MagicMock(), entry)
    return registry


def test_unmerge_strips_mac_connections_from_owned_device(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A device owned only by tplink_deco loses its MAC connections."""
    mac_conn = (CONNECTION_NETWORK_MAC, "aa:bb:cc:dd:ee:ff")
    other_conn = ("zigbee", "1234")
    device = _FakeDevice(
        id="dev1",
        config_entries={ENTRY_ID},
        connections={mac_conn, other_conn},
    )
    registry = _run(monkeypatch, [device])

    registry.async_update_device.assert_called_once_with(
        "dev1", new_connections={other_conn}
    )


def test_unmerge_skips_owned_device_without_mac_connections(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An owned device with no MAC connections is left untouched."""
    device = _FakeDevice(
        id="dev1",
        config_entries={ENTRY_ID},
        connections={("zigbee", "1234")},
    )
    registry = _run(monkeypatch, [device])

    registry.async_update_device.assert_not_called()


def test_unmerge_detaches_shared_device_and_strips_identifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A shared device is detached and loses its tplink_deco identifier."""
    deco_id = (DOMAIN, "deco-mac")
    other_id = ("other", "node-1")
    device = _FakeDevice(
        id="dev1",
        config_entries={ENTRY_ID, OTHER_ENTRY_ID},
        identifiers={deco_id, other_id},
    )
    registry = _run(monkeypatch, [device])

    registry.async_update_device.assert_any_call(
        "dev1", remove_config_entry_id=ENTRY_ID
    )
    registry.async_update_device.assert_any_call("dev1", new_identifiers={other_id})
    assert registry.async_update_device.call_count == 2


def test_unmerge_detaches_shared_device_without_deco_identifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A shared device without a tplink_deco identifier is only detached."""
    device = _FakeDevice(
        id="dev1",
        config_entries={ENTRY_ID, OTHER_ENTRY_ID},
        identifiers={("other", "node-1")},
    )
    registry = _run(monkeypatch, [device])

    registry.async_update_device.assert_called_once_with(
        "dev1", remove_config_entry_id=ENTRY_ID
    )


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
