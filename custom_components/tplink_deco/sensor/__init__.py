"""Sensor platform for TP-Link Deco clients."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .download import TpLinkDecoDownloadSensor
from .ip import TpLinkDecoIpSensor
from .mac import TpLinkDecoMacSensor
from .upload import TpLinkDecoUploadSensor

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ..data import TpLinkDecoConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: TpLinkDecoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for all connected clients, including devices that connect later."""
    coordinator = entry.runtime_data.coordinator
    known_macs: set[str] = set()

    def _add_new_entities() -> None:
        new_clients = [c for c in (coordinator.data or []) if c.mac not in known_macs]
        if not new_clients:
            return
        known_macs.update(c.mac for c in new_clients)
        async_add_entities(
            entity
            for client in new_clients
            for entity in (
                TpLinkDecoMacSensor(coordinator, client),
                TpLinkDecoIpSensor(coordinator, client),
                TpLinkDecoDownloadSensor(coordinator, client),
                TpLinkDecoUploadSensor(coordinator, client),
            )
        )

    _add_new_entities()
    entry.async_on_unload(coordinator.async_add_listener(_add_new_entities))
