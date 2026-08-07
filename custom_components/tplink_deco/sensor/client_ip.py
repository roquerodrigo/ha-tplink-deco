"""IP address sensor for a TP-Link Deco client."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import EntityCategory

from custom_components.tplink_deco.device import TpLinkDecoClientDevice


class TpLinkDecoClientIpSensor(TpLinkDecoClientDevice, SensorEntity):
    """Sensor for the IP address of a TP-Link Deco client."""

    entity_description = SensorEntityDescription(
        key="ip",
        translation_key="ip",
        icon="mdi:ip-network",
        entity_category=EntityCategory.DIAGNOSTIC,
    )

    @property
    def unique_id(self) -> str:
        """Return the unique entity ID."""
        return f"{self._client_mac}_ip"

    @property
    def native_value(self) -> str | None:
        """Return the IP address."""
        client = self.client
        return client.ip if client else None
