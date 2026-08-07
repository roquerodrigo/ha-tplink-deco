"""MAC address sensor for a TP-Link Deco node."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import EntityCategory

from custom_components.tplink_deco.device import TpLinkDecoDecoDevice


class TpLinkDecoDecoMacSensor(TpLinkDecoDecoDevice, SensorEntity):
    """Sensor for the MAC address of a TP-Link Deco node."""

    entity_description = SensorEntityDescription(
        key="mac",
        translation_key="mac",
        icon="mdi:identifier",
        entity_category=EntityCategory.DIAGNOSTIC,
    )

    @property
    def unique_id(self) -> str:
        """Return the unique entity ID."""
        return f"{self._node_mac}_mac"

    @property
    def native_value(self) -> str | None:
        """Return the MAC address."""
        node = self.node
        return node.mac if node else None
