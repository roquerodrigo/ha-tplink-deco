"""Memory usage sensor for a TP-Link Deco node."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE
from tplink_deco_api import Device

from ..node_entity import TpLinkDecoNodeEntity

if TYPE_CHECKING:
    from ..coordinator import TpLinkDecoDataUpdateCoordinator


class TpLinkDecoNodeMemorySensor(TpLinkDecoNodeEntity, SensorEntity):
    """Sensor for the memory usage of a TP-Link Deco node."""

    entity_description = SensorEntityDescription(
        key="mem_usage",
        translation_key="mem_usage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:memory",
    )

    def __init__(
        self,
        coordinator: TpLinkDecoDataUpdateCoordinator,
        node: Device,
    ) -> None:
        super().__init__(coordinator, node)
        self._attr_unique_id = f"{node.mac}_mem_usage"

    @property
    def native_value(self) -> float | None:
        performance = self.coordinator.data.performance
        return round(performance.mem_usage * 100, 1) if performance else None
