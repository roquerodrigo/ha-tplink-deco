"""IP address sensor for a TP-Link Deco client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from tplink_deco_api import ClientDevice

from ..entity import TpLinkDecoClientEntity

if TYPE_CHECKING:
    from ..coordinator import TpLinkDecoDataUpdateCoordinator


class TpLinkDecoIpSensor(TpLinkDecoClientEntity, SensorEntity):
    """Sensor for the IP address of a TP-Link Deco client."""

    entity_description = SensorEntityDescription(
        key="ip",
        translation_key="ip",
        icon="mdi:ip-network",
    )

    def __init__(
        self,
        coordinator: TpLinkDecoDataUpdateCoordinator,
        client: ClientDevice,
    ) -> None:
        super().__init__(coordinator, client)
        self._attr_unique_id = f"{client.mac}_ip"

    @property
    def native_value(self) -> str | None:
        client = self.client
        return client.ip if client else None
