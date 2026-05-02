"""Device tracker for a TP-Link Deco client."""

from __future__ import annotations

from homeassistant.components.device_tracker import ScannerEntity, SourceType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..client_entity import TpLinkDecoClientEntity


class TpLinkDecoClientTracker(TpLinkDecoClientEntity, ScannerEntity):
    """Device tracker for a client connected to the TP-Link Deco network."""

    _attr_name = None
    source_type = SourceType.ROUTER

    @property
    def unique_id(self) -> str:
        return f"{self._client_mac}_tracker"

    @property
    def available(self) -> bool:
        return CoordinatorEntity.available.fget(self)

    @property
    def is_connected(self) -> bool:
        return self.client is not None

    @property
    def ip_address(self) -> str | None:
        client = self.client
        return client.ip if client else None

    @property
    def mac_address(self) -> str:
        return self._client_mac
