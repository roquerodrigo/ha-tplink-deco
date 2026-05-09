"""Connection type sensor for a TP-Link Deco client."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)

from custom_components.tplink_deco.device import TpLinkDecoClientDevice

CONNECTION_TYPE_OPTIONS = ("band2_4", "band5", "band6", "wired")


class TpLinkDecoClientConnectionTypeSensor(TpLinkDecoClientDevice, SensorEntity):
    """Sensor for the connection type of a TP-Link Deco client."""

    entity_description = SensorEntityDescription(
        key="connection_type",
        translation_key="connection_type",
        device_class=SensorDeviceClass.ENUM,
        options=list(CONNECTION_TYPE_OPTIONS),
        icon="mdi:wifi",
    )

    @property
    def unique_id(self) -> str:
        """Return the unique entity ID."""
        return f"{self._client_mac}_connection_type"

    @property
    def native_value(self) -> str | None:
        """Return the connection type, or None if not in the known options."""
        client = self.client
        if client is None:
            return None
        value = client.connection_type
        return value if value in CONNECTION_TYPE_OPTIONS else None
