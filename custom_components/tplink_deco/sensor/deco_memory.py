"""Memory usage sensor for a TP-Link Deco node."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE

from ..deco_entity import TpLinkDecoDecoEntity


class TpLinkDecoDecoMemorySensor(TpLinkDecoDecoEntity, SensorEntity):
    """Sensor for the memory usage of a TP-Link Deco node."""

    entity_description = SensorEntityDescription(
        key="mem_usage",
        translation_key="mem_usage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:memory",
    )

    @property
    def unique_id(self) -> str:
        return f"{self._node_mac}_mem_usage"

    @property
    def native_value(self) -> float | None:
        performance = self.coordinator.data.performance
        return round(performance.mem_usage * 100, 1) if performance else None
