"""Tests for the base device classes."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.tplink_deco.api import TpLinkDecoSnapshot
from custom_components.tplink_deco.const import (
    CONF_LINK_DEVICES_BY_MAC,
    DOMAIN,
    MANUFACTURER,
)
from custom_components.tplink_deco.device import (
    TpLinkDecoClientDevice,
    TpLinkDecoDecoDevice,
)

from .factories import make_client, make_node, make_performance

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from tplink_deco_api import ClientDevice


def _coordinator(
    snapshot: TpLinkDecoSnapshot | None,
    *,
    link_devices_by_mac: bool = True,
    entry_id: str = "entry",
) -> MagicMock:
    mock = MagicMock()
    mock.data = snapshot
    mock.last_update_success = True
    mock.config_entry.data = {CONF_LINK_DEVICES_BY_MAC: link_devices_by_mac}
    mock.config_entry.entry_id = entry_id
    return mock


def _client_device_in_hass(
    hass: HomeAssistant,
    snapshot: TpLinkDecoSnapshot,
    client: ClientDevice,
    entry: MockConfigEntry,
) -> TpLinkDecoClientDevice:
    device = TpLinkDecoClientDevice(
        _coordinator(snapshot, entry_id=entry.entry_id),
        client,
    )
    device.hass = hass
    return device


async def test_client_device_info_links_to_master(hass: HomeAssistant) -> None:
    """The client device_info points to the registered master node device."""
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    client = make_client(mac="AA:11:22:33:44:55", name="Phone")
    master = make_node(mac="DD:EE:FF:00:11:22", role="master")
    master_device = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, master.mac)},
    )
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[master], performance=None)
    device = _client_device_in_hass(hass, snapshot, client, entry)

    info = device.device_info
    assert info["identifiers"] == {(DOMAIN, client.mac)}
    assert (CONNECTION_NETWORK_MAC, client.mac) in info["connections"]
    assert info["via_device_id"] == master_device.id
    assert "via_device" not in info
    assert info["name"] == "Phone"


async def test_client_device_info_without_master_node(hass: HomeAssistant) -> None:
    """device_info returns no via_device_id when no master is present."""
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    client = make_client()
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    device = _client_device_in_hass(hass, snapshot, client, entry)
    assert "via_device_id" not in device.device_info


async def test_client_device_info_without_registered_master(
    hass: HomeAssistant,
) -> None:
    """device_info drops the link when the master node has no registry entry."""
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    client = make_client()
    master = make_node(role="master")
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[master], performance=None)
    device = _client_device_in_hass(hass, snapshot, client, entry)
    assert "via_device_id" not in device.device_info


def test_client_device_info_without_snapshot() -> None:
    """device_info has no link before the first successful refresh."""
    client = make_client()
    device = TpLinkDecoClientDevice(_coordinator(None), client)
    assert "via_device_id" not in device.device_info


def test_client_available_when_present() -> None:
    """Available is true when the client appears in the snapshot."""
    client = make_client()
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    device = TpLinkDecoClientDevice(_coordinator(snapshot), client)
    assert device.available is True


def test_client_unavailable_when_absent_from_snapshot() -> None:
    """Available is false when the client isn't in the (grace-augmented) snapshot."""
    client = make_client()
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[], performance=None)
    device = TpLinkDecoClientDevice(_coordinator(snapshot), client)
    assert device.available is False
    assert device.client is None


def test_deco_device_info_includes_all_bssids() -> None:
    """Deco device_info exposes main MAC plus every populated BSSID."""
    node = make_node(
        mac="AA:BB:CC:00:00:01",
        bssid_2g="AA:BB:CC:00:00:02",
        bssid_5g="AA:BB:CC:00:00:03",
        bssid_sta_2g="AA:BB:CC:00:00:04",
        bssid_sta_5g="",
    )
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None)
    device = TpLinkDecoDecoDevice(_coordinator(snapshot), node)

    info = device.device_info
    macs = {mac for kind, mac in info["connections"] if kind == CONNECTION_NETWORK_MAC}
    assert macs == {
        "AA:BB:CC:00:00:01",
        "AA:BB:CC:00:00:02",
        "AA:BB:CC:00:00:03",
        "AA:BB:CC:00:00:04",
    }
    assert info["manufacturer"] == MANUFACTURER
    assert info["model"] == node.device_model
    assert info["sw_version"] == node.software_ver


def test_deco_device_uses_custom_nickname_when_present() -> None:
    """Custom nickname overrides the default nickname."""
    node = make_node(nickname="Default", custom_nickname="Office")
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None)
    device = TpLinkDecoDecoDevice(_coordinator(snapshot), node)
    assert device.device_info["name"] == "Office"


def test_deco_unavailable_when_node_missing() -> None:
    """The Deco device is unavailable when removed from the snapshot."""
    node = make_node()
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[], performance=make_performance())
    device = TpLinkDecoDecoDevice(_coordinator(snapshot), node)
    assert device.available is False
    assert device.node is None


async def test_client_device_info_omits_mac_connection_when_disabled(
    hass: HomeAssistant,
) -> None:
    """device_info drops MAC connection when link_devices_by_mac is False."""
    client = make_client()
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    device = TpLinkDecoClientDevice(
        _coordinator(snapshot, link_devices_by_mac=False),
        client,
    )
    device.hass = hass
    assert "connections" not in device.device_info


def test_deco_device_info_omits_mac_connections_when_disabled() -> None:
    """device_info drops MAC connections when link_devices_by_mac is False."""
    node = make_node(
        bssid_2g="AA:BB:CC:00:00:02",
        bssid_5g="AA:BB:CC:00:00:03",
    )
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None)
    device = TpLinkDecoDecoDevice(
        _coordinator(snapshot, link_devices_by_mac=False),
        node,
    )
    assert "connections" not in device.device_info


def test_client_property_none_before_first_refresh() -> None:
    """The client property returns None while the coordinator has no data."""
    client = make_client()
    coordinator = _coordinator(
        TpLinkDecoSnapshot(clients=[], nodes=[], performance=None)
    )
    coordinator.data = None
    device = TpLinkDecoClientDevice(coordinator, client)
    assert device.client is None
    assert device.available is False


def test_node_property_none_before_first_refresh() -> None:
    """The node property returns None while the coordinator has no data."""
    node = make_node()
    coordinator = _coordinator(
        TpLinkDecoSnapshot(clients=[], nodes=[], performance=None)
    )
    coordinator.data = None
    device = TpLinkDecoDecoDevice(coordinator, node)
    assert device.node is None
    assert device.available is False
