"""Base device for TP-Link Deco clients."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.tplink_deco.const import (
    ATTRIBUTION,
    CONF_LINK_DEVICES_BY_MAC,
    DEFAULT_LINK_DEVICES_BY_MAC,
    DOMAIN,
)
from custom_components.tplink_deco.coordinator import TpLinkDecoDataUpdateCoordinator

if TYPE_CHECKING:
    from tplink_deco_api import ClientDevice

    from custom_components.tplink_deco.api import TpLinkDecoSnapshot


class TpLinkDecoClientDevice(CoordinatorEntity[TpLinkDecoDataUpdateCoordinator]):
    """Device representing a client connected to the TP-Link Deco network."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TpLinkDecoDataUpdateCoordinator,
        client: ClientDevice,
    ) -> None:
        """Initialize the client device with the coordinator and client."""
        super().__init__(coordinator)
        self._client_mac = client.mac

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info linking this client to the master Deco node."""
        info = DeviceInfo(
            identifiers={(DOMAIN, self._client_mac)},
            name=self.client.name if self.client else None,
        )
        if self._link_devices_by_mac:
            info["connections"] = {(CONNECTION_NETWORK_MAC, self._client_mac)}
        master_device_id = self._master_node_device_id
        if master_device_id:
            info["via_device_id"] = master_device_id
        return info

    @property
    def _master_node_device_id(self) -> str | None:
        """Return the registry id of the master node device, if registered."""
        snapshot: TpLinkDecoSnapshot | None = self.coordinator.data
        if snapshot is None:
            return None
        master = next((n for n in snapshot.nodes if n.role == "master"), None)
        if master is None:
            return None
        device = dr.async_get(self.hass).async_get_device_by_identifier(
            (DOMAIN, master.mac),
            self.coordinator.config_entry.entry_id,
        )
        return device.id if device else None

    @property
    def _link_devices_by_mac(self) -> bool:
        """Return whether device entries should advertise their MAC connection."""
        entry = self.coordinator.config_entry
        return entry.data.get(CONF_LINK_DEVICES_BY_MAC, DEFAULT_LINK_DEVICES_BY_MAC)

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""
        return super().available and self.client is not None

    @property
    def client(self) -> ClientDevice | None:
        """Return the current client from the (grace-augmented) snapshot."""
        snapshot: TpLinkDecoSnapshot | None = self.coordinator.data
        if snapshot is None:
            return None
        return next((c for c in snapshot.clients if c.mac == self._client_mac), None)
