"""Upload speed sensor for a TP-Link Deco client."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfDataRate

from custom_components.tplink_deco.device import TpLinkDecoClientDevice


class TpLinkDecoClientUploadSensor(TpLinkDecoClientDevice, SensorEntity):
    """Sensor for the upload speed of a TP-Link Deco client."""

    entity_description = SensorEntityDescription(
        key="upload",
        translation_key="upload",
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement=UnitOfDataRate.KILOBITS_PER_SECOND,
        suggested_unit_of_measurement=UnitOfDataRate.KILOBITS_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:upload",
    )

    @property
    def unique_id(self) -> str:
        """Return the unique entity ID."""
        return f"{self._client_mac}_upload"

    @property
    def native_value(self) -> int | None:
        """Return the upload speed in kbps."""
        client = self.client
        return client.up_speed if client else None
