"""MAC address sensor for a TP-Link Deco node."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from ..entity import TpLinkDecoDecoEntity


class TpLinkDecoDecoMacSensor(TpLinkDecoDecoEntity, SensorEntity):
    """Sensor for the MAC address of a TP-Link Deco node."""

    entity_description = SensorEntityDescription(
        key="mac",
        translation_key="mac",
        icon="mdi:identifier",
    )

    @property
    def unique_id(self) -> str:
        return f"{self._node_mac}_node_mac"

    @property
    def native_value(self) -> str | None:
        node = self.node
        return node.mac if node else None
