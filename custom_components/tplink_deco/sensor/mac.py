"""MAC address sensor for a TP-Link Deco client."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from ..entity import TpLinkDecoClientEntity


class TpLinkDecoMacSensor(TpLinkDecoClientEntity, SensorEntity):
    """Sensor for the MAC address of a TP-Link Deco client."""

    entity_description = SensorEntityDescription(
        key="mac",
        translation_key="mac",
        icon="mdi:identifier",
    )

    @property
    def unique_id(self) -> str:
        return f"{self._client_mac}_mac"

    @property
    def native_value(self) -> str | None:
        client = self.client
        return client.mac if client else None
