"""Base entity for TP-Link Deco client devices."""

from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from tplink_deco_api import ClientDevice

from .const import ATTRIBUTION, DOMAIN
from .coordinator import TpLinkDecoDataUpdateCoordinator


class TpLinkDecoClientEntity(CoordinatorEntity[TpLinkDecoDataUpdateCoordinator]):
    """Entity representing a client connected to the TP-Link Deco network."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TpLinkDecoDataUpdateCoordinator,
        client: ClientDevice,
    ) -> None:
        super().__init__(coordinator)
        self._client_mac = client.mac

    @property
    def device_info(self) -> DeviceInfo | None:
        snapshot = self.coordinator.data
        master = next(
            (n for n in snapshot.nodes if n.role == "master"),
            None,
        ) if snapshot else None
        return DeviceInfo(
            identifiers={(DOMAIN, self._client_mac)},
            connections={(CONNECTION_NETWORK_MAC, self._client_mac)},
            name=self.client.name if self.client else None,
            via_device=(DOMAIN, master.mac) if master else None,
        )

    @property
    def available(self) -> bool:
        return super().available and self.client is not None

    @property
    def client(self) -> ClientDevice | None:
        return next(
            (c for c in self.coordinator.data.clients if c.mac == self._client_mac),
            None,
        )
