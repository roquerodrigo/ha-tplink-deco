"""IP address sensor for a TP-Link Deco node."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from tplink_deco_api import Device

from ..node_entity import TpLinkDecoNodeEntity

if TYPE_CHECKING:
    from ..coordinator import TpLinkDecoDataUpdateCoordinator


class TpLinkDecoNodeIpSensor(TpLinkDecoNodeEntity, SensorEntity):
    """Sensor for the IP address of a TP-Link Deco node."""

    entity_description = SensorEntityDescription(
        key="ip",
        translation_key="ip",
        icon="mdi:ip-network",
    )

    def __init__(
        self,
        coordinator: TpLinkDecoDataUpdateCoordinator,
        node: Device,
    ) -> None:
        super().__init__(coordinator, node)
        self._attr_unique_id = f"{node.mac}_node_ip"

    @property
    def native_value(self) -> str | None:
        node = self.node
        return node.device_ip if node else None
