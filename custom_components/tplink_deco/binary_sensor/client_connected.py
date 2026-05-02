"""Connected status binary sensor for a TP-Link Deco client."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..entity import TpLinkDecoClientEntity


class TpLinkDecoClientConnectedBinarySensor(TpLinkDecoClientEntity, BinarySensorEntity):
    """Binary sensor for the connected status of a TP-Link Deco client."""

    entity_description = BinarySensorEntityDescription(
        key="connected",
        translation_key="connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    )

    @property
    def unique_id(self) -> str:
        return f"{self._client_mac}_connected"

    @property
    def available(self) -> bool:
        # Always available as long as the coordinator is working, even when
        # the device is absent from the API response (i.e. offline).
        return CoordinatorEntity.available.fget(self)

    @property
    def is_on(self) -> bool:
        return self.client is not None
