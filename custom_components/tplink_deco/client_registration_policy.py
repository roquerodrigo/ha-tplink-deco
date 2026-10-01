"""Policy deciding which reported clients get entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers import device_registry as dr

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from tplink_deco_api import ClientDevice

    from .data import TpLinkDecoConfigEntry


class TpLinkDecoClientRegistrationPolicy:
    """
    Select the clients a platform still has to create entities for.

    The router keeps reporting clients long after they disconnect, so a device
    the user removed while offline must not be re-created from that list; it
    only comes back once the client connects again. Clients that already have
    a device keep their entities whether online or not.
    """

    def __init__(self, hass: HomeAssistant, entry: TpLinkDecoConfigEntry) -> None:
        """Initialize the policy for one config entry."""
        self._hass = hass
        self._entry = entry

    def select_new(
        self,
        clients: list[ClientDevice],
        known_macs: set[str],
    ) -> list[ClientDevice]:
        """Return the clients whose entities are missing from the platform."""
        registry = dr.async_get(self._hass)
        return [
            client
            for client in clients
            if self._needs_entities(registry, client, known_macs)
        ]

    def _needs_entities(
        self,
        registry: dr.DeviceRegistry,
        client: ClientDevice,
        known_macs: set[str],
    ) -> bool:
        registered = (
            registry.async_get_device_by_identifier(
                (DOMAIN, client.mac),
                self._entry.entry_id,
            )
            is not None
        )
        if registered:
            return client.mac not in known_macs
        return client.online
