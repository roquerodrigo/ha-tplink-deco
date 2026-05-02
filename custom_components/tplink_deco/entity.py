"""Base entity for TP-Link Deco client devices."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
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
        """Initialize the entity."""
        super().__init__(coordinator)
        self._client_mac = client.mac
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, client.mac)},
            name=client.name,
        )

    @property
    def client(self) -> ClientDevice | None:
        """Return the current client data from the coordinator."""
        return next(
            (c for c in self.coordinator.data if c.mac == self._client_mac),
            None,
        )
