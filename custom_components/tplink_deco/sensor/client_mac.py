"""MAC address sensor for a TP-Link Deco client."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from custom_components.tplink_deco.device import TpLinkDecoClientDevice


class TpLinkDecoClientMacSensor(TpLinkDecoClientDevice, SensorEntity):
    """Sensor for the MAC address of a TP-Link Deco client."""

    entity_description = SensorEntityDescription(
        key="mac",
        translation_key="mac",
        icon="mdi:identifier",
    )

    @property
    def unique_id(self) -> str:
        """Return the unique entity ID."""
        return f"{self._client_mac}_mac"

    @property
    def native_value(self) -> str | None:
        """Return the MAC address."""
        client = self.client
        return client.mac if client else None
