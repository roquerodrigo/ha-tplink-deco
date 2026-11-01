"""TP-Link Deco integration for Home Assistant."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_USERNAME,
    Platform,
)
from homeassistant.loader import async_get_loaded_integration

from .api import TpLinkDecoApiClient
from .card_registration import TpLinkDecoCardRegistration
from .const import (
    DEFAULT_SCAN_INTERVAL_SECONDS,
    DEFAULT_TIMEOUT_SECONDS,
    DOMAIN,
    LOGGER,
)
from .coordinator import TpLinkDecoDataUpdateCoordinator
from .data import TpLinkDecoData
from .device_registry_sync import TpLinkDecoDeviceRegistrySync
from .node_registration import TpLinkDecoNodeRegistration

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import AnyDeviceEntry

    from .data import TpLinkDecoConfigEntry

MINOR_VERSION_WITHOUT_LINK_DEVICES_BY_MAC = 2

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

    scan_interval = int(
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_SECONDS)
    )
    coordinator = TpLinkDecoDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(seconds=scan_interval),
    )
    entry.runtime_data = TpLinkDecoData(
        client=TpLinkDecoApiClient(
            host=entry.data[CONF_HOST],
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            timeout=float(entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT_SECONDS)),
        ),
        integration=integration,
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()

    TpLinkDecoNodeRegistration(hass, entry).register(coordinator.data.nodes)
    device_registry_sync = TpLinkDecoDeviceRegistrySync(hass, entry)
    entry.async_on_unload(
        coordinator.async_add_listener(
            lambda: device_registry_sync.sync(coordinator.data)
        )
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_migrate_entry(
    hass: HomeAssistant,
    entry: TpLinkDecoConfigEntry,
) -> bool:
    """Drop the data of the options removed from the config flow."""
    if entry.minor_version < MINOR_VERSION_WITHOUT_LINK_DEVICES_BY_MAC:
        hass.config_entries.async_update_entry(
            entry,
            data={
                key: value
                for key, value in entry.data.items()
                if key != "link_devices_by_mac"
            },
            minor_version=MINOR_VERSION_WITHOUT_LINK_DEVICES_BY_MAC,
        )
    return True


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
    device_entry: AnyDeviceEntry,
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
