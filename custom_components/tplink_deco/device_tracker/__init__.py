"""Device tracker platform for TP-Link Deco clients."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.tplink_deco.client_registration_policy import (
    TpLinkDecoClientRegistrationPolicy,
)
from custom_components.tplink_deco.const import LOGGER

from .client import TpLinkDecoClientTracker

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from custom_components.tplink_deco.data import TpLinkDecoConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TpLinkDecoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up device trackers for all clients, including devices that connect later."""
    coordinator = entry.runtime_data.coordinator
    client_registration_policy = TpLinkDecoClientRegistrationPolicy(hass, entry)
    known_macs: set[str] = set()

    def _add_new_entities() -> None:
        new_clients = client_registration_policy.select_new(
            coordinator.data.clients if coordinator.data else [],
            known_macs,
        )
        if not new_clients:
            return
        known_macs.update(c.mac for c in new_clients)
        LOGGER.debug("Adding device_tracker for %d new client(s)", len(new_clients))
        async_add_entities(
            TpLinkDecoClientTracker(coordinator, client) for client in new_clients
        )

    _add_new_entities()
    entry.async_on_unload(coordinator.async_add_listener(_add_new_entities))
