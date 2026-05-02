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
    known_client_macs: set[str] = set()
    known_node_macs: set[str] = set()

    def _add_new_entities() -> None:
        snapshot = coordinator.data

        new_clients = [c for c in (snapshot.clients if snapshot else []) if c.mac not in known_client_macs]
        if new_clients:
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

        new_nodes = [n for n in (snapshot.nodes if snapshot else []) if n.mac not in known_node_macs]
        if new_nodes:
            known_node_macs.update(n.mac for n in new_nodes)
            async_add_entities(
                entity
                for node in new_nodes
                for entity in (
                    TpLinkDecoNodeMacSensor(coordinator, node),
                    TpLinkDecoNodeIpSensor(coordinator, node),
                )
            )

    _add_new_entities()
    entry.async_on_unload(coordinator.async_add_listener(_add_new_entities))
