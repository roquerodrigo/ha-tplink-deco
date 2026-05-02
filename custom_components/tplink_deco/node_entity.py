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
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, node.mac)},
            connections={(CONNECTION_NETWORK_MAC, node.mac)},
            name=node.custom_nickname or node.nickname,
            model=node.device_model,
            sw_version=node.software_ver,
            hw_version=node.hardware_ver,
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
