"""Synchronization of device registry metadata with the router."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceEntry
    from tplink_deco_api import ClientDevice, Device

    from .api import TpLinkDecoSnapshot
    from .data import TpLinkDecoConfigEntry


class TpLinkDecoDeviceRegistrySync:
    """
    Keep registered devices in line with what the router reports.

    Home Assistant reads ``device_info`` only when an entity is added, so a
    client or node renamed in the Deco app, or a node whose firmware was
    updated, would otherwise keep stale metadata until the entry is reloaded.
    Only the integration-provided ``name`` is touched; a name set by the user
    in Home Assistant (``name_by_user``) keeps taking precedence.
    """

    def __init__(self, hass: HomeAssistant, entry: TpLinkDecoConfigEntry) -> None:
        """Initialize the synchronization for one config entry."""
        self._hass = hass
        self._entry = entry

    def sync(self, snapshot: TpLinkDecoSnapshot | None) -> None:
        """Update the registry entries of every client and node in the snapshot."""
        if snapshot is None:
            return
        registry = dr.async_get(self._hass)
        for client in snapshot.clients:
            self._sync_client(registry, client)
        for node in snapshot.nodes:
            self._sync_node(registry, node)

    def _sync_client(
        self,
        registry: dr.DeviceRegistry,
        client: ClientDevice,
    ) -> None:
        device = self._registered_device(registry, client.mac)
        if device is None or not client.name or device.name == client.name:
            return
        LOGGER.debug(
            "Renaming client %s from %s to %s", client.mac, device.name, client.name
        )
        registry.async_update_device(device.id, name=client.name)

    def _sync_node(self, registry: dr.DeviceRegistry, node: Device) -> None:
        device = self._registered_device(registry, node.mac)
        if device is None:
            return
        name = node.custom_nickname or node.nickname or device.name
        if (
            device.name == name
            and device.model == node.device_model
            and device.sw_version == node.software_ver
            and device.hw_version == node.hardware_ver
        ):
            return
        LOGGER.debug("Updating node %s metadata from the router", node.mac)
        registry.async_update_device(
            device.id,
            name=name,
            model=node.device_model,
            sw_version=node.software_ver,
            hw_version=node.hardware_ver,
        )

    def _registered_device(
        self,
        registry: dr.DeviceRegistry,
        mac: str,
    ) -> DeviceEntry | None:
        return registry.async_get_device_by_identifier(
            (DOMAIN, mac),
            self._entry.entry_id,
        )
