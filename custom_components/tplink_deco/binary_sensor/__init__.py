"""Binary sensor platform for TP-Link Deco clients and nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.tplink_deco.const import LOGGER

from .client_connected import TpLinkDecoClientConnectedBinarySensor
from .deco_internet import TpLinkDecoDecoInternetBinarySensor

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from custom_components.tplink_deco.data import TpLinkDecoConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: TpLinkDecoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors for clients and nodes, including new ones."""
    coordinator = entry.runtime_data.coordinator
    known_client_macs: set[str] = set()
    known_node_macs: set[str] = set()

    def _add_new_entities() -> None:
        snapshot = coordinator.data

        new_clients = [
            c
            for c in (snapshot.clients if snapshot else [])
            if c.mac not in known_client_macs
        ]
        if new_clients:
            known_client_macs.update(c.mac for c in new_clients)
            LOGGER.debug(
                "Adding connected binary_sensor for %d new client(s)", len(new_clients)
            )
            async_add_entities(
                TpLinkDecoClientConnectedBinarySensor(coordinator, client)
                for client in new_clients
            )

        new_nodes = [
            n
            for n in (snapshot.nodes if snapshot else [])
            if n.mac not in known_node_macs
        ]
        if new_nodes:
            known_node_macs.update(n.mac for n in new_nodes)
            LOGGER.debug(
                "Adding internet binary_sensor for %d new Deco node(s)",
                len(new_nodes),
            )
            async_add_entities(
                TpLinkDecoDecoInternetBinarySensor(coordinator, node)
                for node in new_nodes
            )

    _add_new_entities()
    entry.async_on_unload(coordinator.async_add_listener(_add_new_entities))
