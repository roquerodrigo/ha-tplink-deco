"""Device tracker for a TP-Link Deco client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.device_tracker import ScannerEntity, SourceType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from tplink_deco_api import ClientDevice

from ..entity import TpLinkDecoClientEntity

if TYPE_CHECKING:
    from ..coordinator import TpLinkDecoDataUpdateCoordinator


class TpLinkDecoClientTracker(TpLinkDecoClientEntity, ScannerEntity):
    """Device tracker for a client connected to the TP-Link Deco network."""

    _attr_translation_key = "client_tracker"
    source_type = SourceType.ROUTER

    def __init__(
        self,
        coordinator: TpLinkDecoDataUpdateCoordinator,
        client: ClientDevice,
    ) -> None:
        super().__init__(coordinator, client)
        self._attr_unique_id = f"{client.mac}_tracker"

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
