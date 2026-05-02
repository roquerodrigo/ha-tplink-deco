"""Online status binary sensor for a TP-Link Deco client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from tplink_deco_api import ClientDevice

from ..entity import TpLinkDecoClientEntity

if TYPE_CHECKING:
    from ..coordinator import TpLinkDecoDataUpdateCoordinator


class TpLinkDecoOnlineBinarySensor(TpLinkDecoClientEntity, BinarySensorEntity):
    """Binary sensor for the online status of a TP-Link Deco client."""

    entity_description = BinarySensorEntityDescription(
        key="online",
        translation_key="online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    )

    def __init__(
        self,
        coordinator: TpLinkDecoDataUpdateCoordinator,
        client: ClientDevice,
    ) -> None:
        super().__init__(coordinator, client)
        self._attr_unique_id = f"{client.mac}_online"

    @property
    def available(self) -> bool:
        # Always available as long as the coordinator is working, even when
        # the device is absent from the API response (i.e. offline).
        return CoordinatorEntity.available.fget(self)

    @property
    def is_on(self) -> bool:
        return self.client is not None
