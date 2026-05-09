"""Interface sensor for a TP-Link Deco client."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)

from custom_components.tplink_deco.device import TpLinkDecoClientDevice

INTERFACE_OPTIONS = ("iot", "mlo", "main")


class TpLinkDecoClientInterfaceSensor(TpLinkDecoClientDevice, SensorEntity):
    """Sensor for the network interface of a TP-Link Deco client."""

    entity_description = SensorEntityDescription(
        key="interface",
        translation_key="interface",
        device_class=SensorDeviceClass.ENUM,
        options=list(INTERFACE_OPTIONS),
        icon="mdi:lan",
    )

    @property
    def unique_id(self) -> str:
        """Return the unique entity ID."""
        return f"{self._client_mac}_interface"

    @property
    def native_value(self) -> str | None:
        """Return the network interface, or None if not in the known options."""
        client = self.client
        if client is None:
            return None
        value = client.interface
        return value if value in INTERFACE_OPTIONS else None
