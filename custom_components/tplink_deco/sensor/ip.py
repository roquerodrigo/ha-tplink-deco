"""IP address sensor for a TP-Link Deco client."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from ..entity import TpLinkDecoClientEntity


class TpLinkDecoIpSensor(TpLinkDecoClientEntity, SensorEntity):
    """Sensor for the IP address of a TP-Link Deco client."""

    entity_description = SensorEntityDescription(
        key="ip",
        translation_key="ip",
        icon="mdi:ip-network",
    )

    @property
    def unique_id(self) -> str:
        return f"{self._client_mac}_ip"

    @property
    def native_value(self) -> str | None:
        client = self.client
        return client.ip if client else None
