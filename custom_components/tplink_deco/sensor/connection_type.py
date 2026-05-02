"""Connection type sensor for a TP-Link Deco client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from tplink_deco_api import ClientDevice

from ..entity import TpLinkDecoClientEntity

if TYPE_CHECKING:
    from ..coordinator import TpLinkDecoDataUpdateCoordinator


class TpLinkDecoConnectionTypeSensor(TpLinkDecoClientEntity, SensorEntity):
    """Sensor for the connection type of a TP-Link Deco client."""

    entity_description = SensorEntityDescription(
        key="connection_type",
        translation_key="connection_type",
        device_class=SensorDeviceClass.ENUM,
        options=["band2_4", "band5", "band6", "wired"],
        icon="mdi:wifi",
    )

    def __init__(
        self,
        coordinator: TpLinkDecoDataUpdateCoordinator,
        client: ClientDevice,
    ) -> None:
        super().__init__(coordinator, client)
        self._attr_unique_id = f"{client.mac}_connection_type"

    @property
    def native_value(self) -> str | None:
        client = self.client
        return client.connection_type if client else None
