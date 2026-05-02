"""Internet connectivity binary sensor for a TP-Link Deco node."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from custom_components.tplink_deco.entity import TpLinkDecoDecoEntity

_INET_STATUS_CONNECTED = "online"


class TpLinkDecoDecoInternetBinarySensor(TpLinkDecoDecoEntity, BinarySensorEntity):
    """Binary sensor for the internet connectivity of a TP-Link Deco node."""

    entity_description = BinarySensorEntityDescription(
        key="internet",
        translation_key="internet",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    )

    @property
    def unique_id(self) -> str:
        """Return the unique entity ID."""
        return f"{self._node_mac}_internet"

    @property
    def is_on(self) -> bool | None:
        """Return whether the Deco node has internet connectivity."""
        node = self.node
        return node.inet_status == _INET_STATUS_CONNECTED if node else None
