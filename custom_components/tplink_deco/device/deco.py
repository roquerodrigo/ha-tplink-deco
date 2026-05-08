"""Base device for TP-Link Deco nodes."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.tplink_deco.const import (
    ATTRIBUTION,
    DOMAIN,
    MANUFACTURER,
    UNAVAILABLE_GRACE_PERIOD_SECONDS,
)
from custom_components.tplink_deco.coordinator import TpLinkDecoDataUpdateCoordinator

if TYPE_CHECKING:
    from tplink_deco_api import Device


class TpLinkDecoDecoDevice(CoordinatorEntity[TpLinkDecoDataUpdateCoordinator]):
    """Device representing a TP-Link Deco mesh node."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TpLinkDecoDataUpdateCoordinator,
        node: Device,
    ) -> None:
        """Initialize the Deco node device with the coordinator and node."""
        super().__init__(coordinator)
        self._node_mac = node.mac
        self._cached_node: Device | None = None
        self._last_seen_at: float | None = None

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info for this Deco mesh node."""
        node = self.node
        connections = {(CONNECTION_NETWORK_MAC, self._node_mac)}
        if node:
            for bssid in (
                node.bssid_2g,
                node.bssid_5g,
                node.bssid_sta_2g,
                node.bssid_sta_5g,
            ):
                if bssid:
                    connections.add((CONNECTION_NETWORK_MAC, bssid))
        return DeviceInfo(
            identifiers={(DOMAIN, self._node_mac)},
            connections=connections,
            name=node.custom_nickname or node.nickname if node else None,
            model=node.device_model if node else None,
            sw_version=node.software_ver if node else None,
            hw_version=node.hardware_ver if node else None,
            manufacturer=MANUFACTURER,
        )

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""
        return super().available and self.node is not None

    @property
    def node(self) -> Device | None:
        """Return the current node, or the last seen one within the grace period."""
        snapshot = self.coordinator.data
        current = (
            next((d for d in snapshot.nodes if d.mac == self._node_mac), None)
            if snapshot
            else None
        )
        if current is not None:
            self._cached_node = current
            self._last_seen_at = time.monotonic()
            return current
        if (
            self._cached_node is not None
            and self._last_seen_at is not None
            and time.monotonic() - self._last_seen_at < UNAVAILABLE_GRACE_PERIOD_SECONDS
        ):
            return self._cached_node
        return None
