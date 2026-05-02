"""CPU usage sensor for a TP-Link Deco node."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE

from ..deco_entity import TpLinkDecoDecoEntity


class TpLinkDecoDecoCpuSensor(TpLinkDecoDecoEntity, SensorEntity):
    """Sensor for the CPU usage of a TP-Link Deco node."""

    entity_description = SensorEntityDescription(
        key="cpu_usage",
        translation_key="cpu_usage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cpu-64-bit",
    )

    @property
    def unique_id(self) -> str:
        return f"{self._node_mac}_cpu_usage"

    @property
    def native_value(self) -> float | None:
        performance = self.coordinator.data.performance
        return round(performance.cpu_usage * 100, 1) if performance else None
