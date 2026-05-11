"""Total upload speed sensor for the TP-Link Deco network."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfDataRate
from tplink_deco_api import NetworkTotals

from custom_components.tplink_deco.device import TpLinkDecoDecoDevice


class TpLinkDecoDecoUploadSensor(TpLinkDecoDecoDevice, SensorEntity):
    """Sensor for the total upload speed across all clients."""

    entity_description = SensorEntityDescription(
        key="total_upload",
        translation_key="total_upload",
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement=UnitOfDataRate.KILOBITS_PER_SECOND,
        suggested_unit_of_measurement=UnitOfDataRate.KILOBITS_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:upload-network",
    )

    @property
    def unique_id(self) -> str:
        """Return the unique entity ID."""
        return f"{self._node_mac}_total_upload"

    @property
    def native_value(self) -> int:
        """Return the total upload speed in kbps, summed across clients."""
        return NetworkTotals.from_clients(self.coordinator.data.clients).up_speed
