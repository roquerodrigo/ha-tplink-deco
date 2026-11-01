"""Base device for TP-Link Deco clients."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import ChildDeviceInfo, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.tplink_deco.const import ATTRIBUTION, DOMAIN
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
    def device_info(self) -> ChildDeviceInfo | DeviceInfo | None:
        """Return this client as a child device of the master Deco node."""
        name = self.client.name if self.client else None
        identifiers = {(DOMAIN, self._client_mac)}
        parent_device_id = self._parent_device_id
        if parent_device_id is None:
            return DeviceInfo(identifiers=identifiers, name=name)
        return ChildDeviceInfo(
            identifiers=identifiers,
            parent_device_id=parent_device_id,
            name=name,
        )

    @property
    def _parent_device_id(self) -> str | None:
        """
        Return the registry id of the device this client nests under.

        The device registry refuses to reparent a child device, so a client
        stays under the node it was first nested under when the mesh elects
        another master.
        """
        registry = dr.async_get(self.hass)
        entry_id = self.coordinator.config_entry.entry_id
        child = registry.async_get_child_device_by_identifier(
            (DOMAIN, self._client_mac),
            entry_id,
        )
        if child is not None:
            return child.parent_device_id
        snapshot: TpLinkDecoSnapshot | None = self.coordinator.data
        if snapshot is None:
            return None
        if any(node.mac == self._client_mac for node in snapshot.nodes):
            return None
        master = next((n for n in snapshot.nodes if n.role == "master"), None)
        if master is None:
            return None
        device = registry.async_get_device_by_identifier(
            (DOMAIN, master.mac),
            entry_id,
        )
        return device.id if device else None

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
