"""Base entity for TP-Link Deco nodes."""

from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from tplink_deco_api import Device

from .const import ATTRIBUTION, DOMAIN, MANUFACTURER
from .coordinator import TpLinkDecoDataUpdateCoordinator


class TpLinkDecoNodeEntity(CoordinatorEntity[TpLinkDecoDataUpdateCoordinator]):
    """Entity representing a TP-Link Deco mesh node."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TpLinkDecoDataUpdateCoordinator,
        node: Device,
    ) -> None:
        super().__init__(coordinator)
        self._node_mac = node.mac

    @property
    def device_info(self) -> DeviceInfo | None:
        node = self.node
        return DeviceInfo(
            identifiers={(DOMAIN, self._node_mac)},
            connections={(CONNECTION_NETWORK_MAC, self._node_mac)},
            name=node.custom_nickname or node.nickname if node else None,
            model=node.device_model if node else None,
            sw_version=node.software_ver if node else None,
            hw_version=node.hardware_ver if node else None,
            manufacturer=MANUFACTURER,
        )

    @property
    def available(self) -> bool:
        return super().available and self.node is not None

    @property
    def node(self) -> Device | None:
        return next(
            (d for d in self.coordinator.data.nodes if d.mac == self._node_mac),
            None,
        )
