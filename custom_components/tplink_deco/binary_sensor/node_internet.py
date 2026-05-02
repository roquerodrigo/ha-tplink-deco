"""Internet connectivity binary sensor for a TP-Link Deco node."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from tplink_deco_api import Device

from ..node_entity import TpLinkDecoNodeEntity

if TYPE_CHECKING:
    from ..coordinator import TpLinkDecoDataUpdateCoordinator

_INET_STATUS_CONNECTED = "online"


class TpLinkDecoNodeInternetBinarySensor(TpLinkDecoNodeEntity, BinarySensorEntity):
    """Binary sensor for the internet connectivity of a TP-Link Deco node."""

    entity_description = BinarySensorEntityDescription(
        key="internet",
        translation_key="internet",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    )

    def __init__(
        self,
        coordinator: TpLinkDecoDataUpdateCoordinator,
        node: Device,
    ) -> None:
        super().__init__(coordinator, node)
        self._attr_unique_id = f"{node.mac}_internet"

    @property
    def is_on(self) -> bool | None:
        node = self.node
        return node.inet_status == _INET_STATUS_CONNECTED if node else None
