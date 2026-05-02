"""MAC address sensor for a TP-Link Deco node."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from tplink_deco_api import Device

from ..node_entity import TpLinkDecoNodeEntity

if TYPE_CHECKING:
    from ..node_coordinator import TpLinkDecoNodeCoordinator


class TpLinkDecoNodeMacSensor(TpLinkDecoNodeEntity, SensorEntity):
    """Sensor for the MAC address of a TP-Link Deco node."""

    entity_description = SensorEntityDescription(
        key="mac",
        translation_key="mac",
        icon="mdi:identifier",
    )

    def __init__(
        self,
        coordinator: TpLinkDecoNodeCoordinator,
        node: Device,
    ) -> None:
        super().__init__(coordinator, node)
        self._attr_unique_id = f"{node.mac}_node_mac"

    @property
    def native_value(self) -> str | None:
        node = self.node
        return node.mac if node else None
