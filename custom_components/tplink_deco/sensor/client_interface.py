"""Interface sensor for a TP-Link Deco client."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)

from custom_components.tplink_deco.entity import TpLinkDecoClientEntity


class TpLinkDecoClientInterfaceSensor(TpLinkDecoClientEntity, SensorEntity):
    """Sensor for the network interface of a TP-Link Deco client."""

    entity_description = SensorEntityDescription(
        key="interface",
        translation_key="interface",
        device_class=SensorDeviceClass.ENUM,
        options=["iot", "mlo", "main"],
        icon="mdi:lan",
    )

    @property
    def unique_id(self) -> str:
        """Return the unique entity ID."""
        return f"{self._client_mac}_interface"

    @property
    def native_value(self) -> str | None:
        """Return the network interface."""
        client = self.client
        return client.interface if client else None
