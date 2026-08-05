"""TP-Link Deco integration for Home Assistant."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.loader import async_get_loaded_integration

from .api import TpLinkDecoApiClient
from .card_registration import TpLinkDecoCardRegistration
from .const import (
    CONF_LINK_DEVICES_BY_MAC,
    DEFAULT_LINK_DEVICES_BY_MAC,
    DOMAIN,
    LOGGER,
)
from .coordinator import TpLinkDecoDataUpdateCoordinator
from .data import TpLinkDecoData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceEntry

    from .data import TpLinkDecoConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
    Platform.SENSOR,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TpLinkDecoConfigEntry,
) -> bool:
    """Set up TP-Link Deco from a config entry."""
    integration = async_get_loaded_integration(hass, entry.domain)

    await TpLinkDecoCardRegistration(hass, str(integration.version)).async_register()

    coordinator = TpLinkDecoDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(seconds=20),
    )
    entry.runtime_data = TpLinkDecoData(
        client=TpLinkDecoApiClient(
            host=entry.data[CONF_HOST],
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
        ),
        integration=integration,
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()

    if not entry.data.get(CONF_LINK_DEVICES_BY_MAC, DEFAULT_LINK_DEVICES_BY_MAC):
        _unmerge_devices(hass, entry)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


def _unmerge_devices(
    hass: HomeAssistant,
    entry: TpLinkDecoConfigEntry,
) -> None:
    """Detach tplink_deco from merged devices so platforms create fresh ones."""
    registry = dr.async_get(hass)
    for device in list(dr.async_entries_for_config_entry(registry, entry.entry_id)):
        has_other = any(ce for ce in device.config_entries if ce != entry.entry_id)
        if not has_other:
            # Device belongs only to tplink_deco — just strip MAC connections.
            mac_conns = {
                c for c in device.connections if c[0] == CONNECTION_NETWORK_MAC
            }
            if mac_conns:
                registry.async_update_device(
                    device.id, new_connections=device.connections - mac_conns
                )
            continue
        # Device is shared with other integrations — detach tplink_deco from it
        # so the platform setup creates a new, separate device.
        registry.async_update_device(
            device.id,
            remove_config_entry_id=entry.entry_id,
        )
        # Also strip the tplink_deco identifier from the old merged device.
        deco_ids = {i for i in device.identifiers if i[0] == DOMAIN}
        if deco_ids:
            registry.async_update_device(
                device.id, new_identifiers=device.identifiers - deco_ids
            )


async def async_unload_entry(
    hass: HomeAssistant,
    entry: TpLinkDecoConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(
    hass: HomeAssistant,
    entry: TpLinkDecoConfigEntry,
) -> None:
    """Clean up the card registration when the last entry is removed."""
    if hass.config_entries.async_entries(DOMAIN):
        return
    integration = async_get_loaded_integration(hass, entry.domain)
    await TpLinkDecoCardRegistration(hass, str(integration.version)).async_remove()


async def async_reload_entry(
    hass: HomeAssistant,
    entry: TpLinkDecoConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_config_entry_device(
    hass: HomeAssistant,  # noqa: ARG001 -- HA device-removal contract requires this parameter
    entry: TpLinkDecoConfigEntry,
    device_entry: DeviceEntry,
) -> bool:
    """
    Allow removing a device that is not currently connected.

    Clients the router still reports as online and mesh nodes are refused,
    since the next update would immediately re-create them. Any other device —
    an offline client, including one the router still remembers but that is no
    longer connected — can be removed. A device that reconnects later is simply
    registered again.
    """
    snapshot = entry.runtime_data.coordinator.data
    device_macs = {
        identifier[1]
        for identifier in device_entry.identifiers
        if identifier[0] == DOMAIN
    }
    if snapshot is None or not device_macs:
        return True
    active_macs = {client.mac for client in snapshot.clients if client.online} | {
        node.mac for node in snapshot.nodes
    }
    return device_macs.isdisjoint(active_macs)
