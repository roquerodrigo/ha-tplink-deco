"""Tests for the device registry synchronization."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.tplink_deco.api import TpLinkDecoSnapshot
from custom_components.tplink_deco.const import DOMAIN
from custom_components.tplink_deco.device_registry_sync import (
    TpLinkDecoDeviceRegistrySync,
)

from .factories import make_client, make_node

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

CLIENT_MAC = "AA:BB:CC:DD:EE:01"
NODE_MAC = "11:22:33:44:55:66"


def _entry(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    return entry


def _register(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mac: str,
    name: str,
    **attributes: str,
) -> dr.DeviceEntry:
    return dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, mac)},
        name=name,
        **attributes,
    )


def _sync(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    snapshot: TpLinkDecoSnapshot | None,
) -> None:
    TpLinkDecoDeviceRegistrySync(hass, entry).sync(snapshot)


def _device(hass: HomeAssistant, device_id: str) -> dr.DeviceEntry:
    device = dr.async_get(hass).async_get(device_id)
    assert device is not None
    return device


async def test_sync_renames_client_renamed_on_router(hass: HomeAssistant) -> None:
    """A client renamed in the Deco app gets the new name in the registry."""
    entry = _entry(hass)
    device = _register(hass, entry, CLIENT_MAC, "Phone")

    _sync(
        hass,
        entry,
        TpLinkDecoSnapshot(
            clients=[make_client(mac=CLIENT_MAC, name="Work Phone")],
            nodes=[],
            performance=None,
        ),
    )

    assert _device(hass, device.id).name == "Work Phone"


async def test_sync_keeps_name_set_by_user(hass: HomeAssistant) -> None:
    """A name chosen in Home Assistant keeps taking precedence."""
    entry = _entry(hass)
    device = _register(hass, entry, CLIENT_MAC, "Phone")
    dr.async_get(hass).async_update_device(device.id, name_by_user="My Phone")

    _sync(
        hass,
        entry,
        TpLinkDecoSnapshot(
            clients=[make_client(mac=CLIENT_MAC, name="Work Phone")],
            nodes=[],
            performance=None,
        ),
    )

    updated = _device(hass, device.id)
    assert updated.name == "Work Phone"
    assert updated.name_by_user == "My Phone"


async def test_sync_ignores_client_without_name(hass: HomeAssistant) -> None:
    """An empty name reported by the router does not erase the current one."""
    entry = _entry(hass)
    device = _register(hass, entry, CLIENT_MAC, "Phone")

    _sync(
        hass,
        entry,
        TpLinkDecoSnapshot(
            clients=[make_client(mac=CLIENT_MAC, name="")],
            nodes=[],
            performance=None,
        ),
    )

    assert _device(hass, device.id).name == "Phone"


async def test_sync_skips_unregistered_devices(hass: HomeAssistant) -> None:
    """Clients and nodes without a registry entry are left to the platforms."""
    entry = _entry(hass)

    _sync(
        hass,
        entry,
        TpLinkDecoSnapshot(
            clients=[make_client(mac=CLIENT_MAC)],
            nodes=[make_node(mac=NODE_MAC)],
            performance=None,
        ),
    )

    assert dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id) == []


async def test_sync_ignores_devices_of_other_entries(hass: HomeAssistant) -> None:
    """Only devices belonging to the synchronized entry are updated."""
    entry = _entry(hass)
    other_entry = _entry(hass)
    device = _register(hass, other_entry, CLIENT_MAC, "Phone")

    _sync(
        hass,
        entry,
        TpLinkDecoSnapshot(
            clients=[make_client(mac=CLIENT_MAC, name="Work Phone")],
            nodes=[],
            performance=None,
        ),
    )

    assert _device(hass, device.id).name == "Phone"


async def test_sync_updates_node_metadata(hass: HomeAssistant) -> None:
    """A node picks up its new nickname and firmware version."""
    entry = _entry(hass)
    device = _register(
        hass,
        entry,
        NODE_MAC,
        "Living Room",
        model="X20",
        sw_version="1.5.10",
        hw_version="1.0",
    )

    _sync(
        hass,
        entry,
        TpLinkDecoSnapshot(
            clients=[],
            nodes=[
                make_node(
                    mac=NODE_MAC,
                    custom_nickname="Office",
                    software_ver="1.6.0",
                )
            ],
            performance=None,
        ),
    )

    updated = _device(hass, device.id)
    assert updated.name == "Office"
    assert updated.sw_version == "1.6.0"
    assert updated.model == "X20"
    assert updated.hw_version == "1.0"


async def test_sync_leaves_unchanged_node_untouched(hass: HomeAssistant) -> None:
    """A node whose metadata did not change is not rewritten."""
    entry = _entry(hass)
    device = _register(
        hass,
        entry,
        NODE_MAC,
        "Living Room",
        model="X20",
        sw_version="1.5.10",
        hw_version="1.0",
    )

    _sync(
        hass,
        entry,
        TpLinkDecoSnapshot(
            clients=[],
            nodes=[make_node(mac=NODE_MAC)],
            performance=None,
        ),
    )

    assert _device(hass, device.id).modified_at == device.modified_at


async def test_sync_without_snapshot_is_noop(hass: HomeAssistant) -> None:
    """A coordinator without data leaves the registry alone."""
    entry = _entry(hass)
    device = _register(hass, entry, CLIENT_MAC, "Phone")

    _sync(hass, entry, None)

    assert _device(hass, device.id).name == "Phone"
