"""Internet connectivity binary sensor for a TP-Link Deco node."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from ..node_entity import TpLinkDecoNodeEntity

_INET_STATUS_CONNECTED = "online"


class TpLinkDecoNodeInternetBinarySensor(TpLinkDecoNodeEntity, BinarySensorEntity):
    """Binary sensor for the internet connectivity of a TP-Link Deco node."""

    entity_description = BinarySensorEntityDescription(
        key="internet",
        translation_key="internet",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    )

    @property
    def unique_id(self) -> str:
        return f"{self._node_mac}_internet"

    @property
    def is_on(self) -> bool | None:
        node = self.node
        return node.inet_status == _INET_STATUS_CONNECTED if node else None
