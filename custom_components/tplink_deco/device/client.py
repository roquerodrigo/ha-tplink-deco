"""Base device for TP-Link Deco clients."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.tplink_deco.const import (
    ATTRIBUTION,
    DOMAIN,
    UNAVAILABLE_GRACE_PERIOD_SECONDS,
)
from custom_components.tplink_deco.coordinator import TpLinkDecoDataUpdateCoordinator

if TYPE_CHECKING:
    from tplink_deco_api import ClientDevice


class TpLinkDecoClientDevice(CoordinatorEntity[TpLinkDecoDataUpdateCoordinator]):
    """Device representing a client connected to the TP-Link Deco network."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TpLinkDecoDataUpdateCoordinator,
        client: ClientDevice,
    ) -> None:
        """Initialize the client device with the coordinator and client."""
        super().__init__(coordinator)
        self._client_mac = client.mac
        self._cached_client: ClientDevice | None = None
        self._last_seen_at: float | None = None

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info linking this client to the master Deco node."""
        snapshot = self.coordinator.data
        master = (
            next(
                (n for n in snapshot.nodes if n.role == "master"),
                None,
            )
            if snapshot
            else None
        )
        info = DeviceInfo(
            identifiers={(DOMAIN, self._client_mac)},
            connections={(CONNECTION_NETWORK_MAC, self._client_mac)},
            name=self.client.name if self.client else None,
        )
        if master:
            info["via_device"] = (DOMAIN, master.mac)
        return info

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""
        return super().available and self.client is not None

    @property
    def client(self) -> ClientDevice | None:
        """Return the current client, or the last seen one within the grace period."""
        snapshot = self.coordinator.data
        current = (
            next((c for c in snapshot.clients if c.mac == self._client_mac), None)
            if snapshot
            else None
        )
        if current is not None:
            self._cached_client = current
            self._last_seen_at = time.monotonic()
            return current
        if (
            self._cached_client is not None
            and self._last_seen_at is not None
            and time.monotonic() - self._last_seen_at < UNAVAILABLE_GRACE_PERIOD_SECONDS
        ):
            return self._cached_client
        return None
