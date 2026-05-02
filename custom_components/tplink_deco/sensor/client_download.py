"""Download speed sensor for a TP-Link Deco client."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfDataRate

from ..client_entity import TpLinkDecoClientEntity


class TpLinkDecoClientDownloadSensor(TpLinkDecoClientEntity, SensorEntity):
    """Sensor for the download speed of a TP-Link Deco client."""

    entity_description = SensorEntityDescription(
        key="download",
        translation_key="download",
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement=UnitOfDataRate.KILOBITS_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:download",
    )

    @property
    def unique_id(self) -> str:
        return f"{self._client_mac}_download"

    @property
    def native_value(self) -> int | None:
        client = self.client
        return client.down_speed if client else None
