"""IP address sensor for a TP-Link Deco node."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from ..node_entity import TpLinkDecoNodeEntity


class TpLinkDecoNodeIpSensor(TpLinkDecoNodeEntity, SensorEntity):
    """Sensor for the IP address of a TP-Link Deco node."""

    entity_description = SensorEntityDescription(
        key="ip",
        translation_key="ip",
        icon="mdi:ip-network",
    )

    @property
    def unique_id(self) -> str:
        return f"{self._node_mac}_node_ip"

    @property
    def native_value(self) -> str | None:
        node = self.node
        return node.device_ip if node else None
