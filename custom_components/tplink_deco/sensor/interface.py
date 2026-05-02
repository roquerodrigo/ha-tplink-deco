"""Interface sensor for a TP-Link Deco client."""

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


class TpLinkDecoInterfaceSensor(TpLinkDecoClientEntity, SensorEntity):
    """Sensor for the network interface of a TP-Link Deco client."""

    entity_description = SensorEntityDescription(
        key="interface",
        translation_key="interface",
        device_class=SensorDeviceClass.ENUM,
        options=["iot", "mlo", "main"],
        icon="mdi:lan",
    )

    def __init__(
        self,
        coordinator: TpLinkDecoDataUpdateCoordinator,
        client: ClientDevice,
    ) -> None:
        super().__init__(coordinator, client)
        self._attr_unique_id = f"{client.mac}_interface"

    @property
    def native_value(self) -> str | None:
        client = self.client
        return client.interface if client else None
