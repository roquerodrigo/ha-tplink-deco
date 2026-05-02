"""Sensor platform for TP-Link Deco clients and nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .connection_type import TpLinkDecoConnectionTypeSensor
from .download import TpLinkDecoDownloadSensor
from .interface import TpLinkDecoInterfaceSensor
from .ip import TpLinkDecoIpSensor
from .mac import TpLinkDecoMacSensor
from .node_ip import TpLinkDecoNodeIpSensor
from .node_mac import TpLinkDecoNodeMacSensor
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
    """Set up sensors for all connected clients and nodes, including new ones."""
    coordinator = entry.runtime_data.coordinator
    node_coordinator = entry.runtime_data.node_coordinator
    known_client_macs: set[str] = set()
    known_node_macs: set[str] = set()

    def _add_new_client_entities() -> None:
        new_clients = [c for c in (coordinator.data or []) if c.mac not in known_client_macs]
        if not new_clients:
            return
        known_client_macs.update(c.mac for c in new_clients)
        async_add_entities(
            entity
            for client in new_clients
            for entity in (
                TpLinkDecoMacSensor(coordinator, client),
                TpLinkDecoIpSensor(coordinator, client),
                TpLinkDecoDownloadSensor(coordinator, client),
                TpLinkDecoUploadSensor(coordinator, client),
                TpLinkDecoConnectionTypeSensor(coordinator, client),
                TpLinkDecoInterfaceSensor(coordinator, client),
            )
        )

    def _add_new_node_entities() -> None:
        new_nodes = [n for n in (node_coordinator.data or []) if n.mac not in known_node_macs]
        if not new_nodes:
            return
        known_node_macs.update(n.mac for n in new_nodes)
        async_add_entities(
            entity
            for node in new_nodes
            for entity in (
                TpLinkDecoNodeMacSensor(node_coordinator, node),
                TpLinkDecoNodeIpSensor(node_coordinator, node),
            )
        )

    _add_new_client_entities()
    _add_new_node_entities()
    entry.async_on_unload(coordinator.async_add_listener(_add_new_client_entities))
    entry.async_on_unload(node_coordinator.async_add_listener(_add_new_node_entities))
