"""Upload speed sensor for a TP-Link Deco client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfDataRate
from tplink_deco_api import ClientDevice

from ..entity import TpLinkDecoClientEntity

if TYPE_CHECKING:
    from ..coordinator import TpLinkDecoDataUpdateCoordinator


class TpLinkDecoUploadSensor(TpLinkDecoClientEntity, SensorEntity):
    """Sensor for the upload speed of a TP-Link Deco client."""

    entity_description = SensorEntityDescription(
        key="upload",
        translation_key="upload",
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement=UnitOfDataRate.KILOBITS_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:upload",
    )

    def __init__(
        self,
        coordinator: TpLinkDecoDataUpdateCoordinator,
        client: ClientDevice,
    ) -> None:
        super().__init__(coordinator, client)
        self._attr_unique_id = f"{client.mac}_upload"

    @property
    def native_value(self) -> int | None:
        client = self.client
        return client.up_speed if client else None
