"""Connection type sensor for a TP-Link Deco client."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)

from custom_components.tplink_deco.entity import TpLinkDecoClientEntity


class TpLinkDecoClientConnectionTypeSensor(TpLinkDecoClientEntity, SensorEntity):
    """Sensor for the connection type of a TP-Link Deco client."""

    entity_description = SensorEntityDescription(
        key="connection_type",
        translation_key="connection_type",
        device_class=SensorDeviceClass.ENUM,
        options=["band2_4", "band5", "band6", "wired"],
        icon="mdi:wifi",
    )

    @property
    def unique_id(self) -> str:
        """Return the unique entity ID."""
        return f"{self._client_mac}_connection_type"

    @property
    def native_value(self) -> str | None:
        """Return the connection type."""
        client = self.client
        return client.connection_type if client else None
