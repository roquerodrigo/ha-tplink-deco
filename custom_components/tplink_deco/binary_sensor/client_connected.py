"""Connected status binary sensor for a TP-Link Deco client."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from custom_components.tplink_deco.device import TpLinkDecoClientDevice


class TpLinkDecoClientConnectedBinarySensor(TpLinkDecoClientDevice, BinarySensorEntity):
    """Binary sensor for the connected status of a TP-Link Deco client."""

    entity_description = BinarySensorEntityDescription(
        key="connected",
        translation_key="connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    )

    @property
    def unique_id(self) -> str:
        """Return the unique entity ID."""
        return f"{self._client_mac}_connected"

    @property
    def available(self) -> bool:
        """Return True as long as the coordinator is working, even when offline."""
        return self.coordinator.last_update_success

    @property
    def is_on(self) -> bool:
        """Return whether the client is connected."""
        return self.client is not None
