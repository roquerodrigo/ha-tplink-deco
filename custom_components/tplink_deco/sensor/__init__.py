"""Sensor platform for TP-Link Deco clients and nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .client_connection_type import TpLinkDecoClientConnectionTypeSensor
from .client_download import TpLinkDecoClientDownloadSensor
from .client_interface import TpLinkDecoClientInterfaceSensor
from .client_ip import TpLinkDecoClientIpSensor
from .client_mac import TpLinkDecoClientMacSensor
from .client_upload import TpLinkDecoClientUploadSensor
from .deco_clients import TpLinkDecoDecoClientsSensor
from .deco_cpu import TpLinkDecoDecoCpuSensor
from .deco_ip import TpLinkDecoDecoIpSensor
from .deco_mac import TpLinkDecoDecoMacSensor
from .deco_memory import TpLinkDecoDecoMemorySensor

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from custom_components.tplink_deco.data import TpLinkDecoConfigEntry


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

        new_clients = [
            c
            for c in (snapshot.clients if snapshot else [])
            if c.mac not in known_client_macs
        ]
        if new_clients:
            known_client_macs.update(c.mac for c in new_clients)
            async_add_entities(
                entity
                for client in new_clients
                for entity in (
                    TpLinkDecoClientMacSensor(coordinator, client),
                    TpLinkDecoClientIpSensor(coordinator, client),
                    TpLinkDecoClientDownloadSensor(coordinator, client),
                    TpLinkDecoClientUploadSensor(coordinator, client),
                    TpLinkDecoClientConnectionTypeSensor(coordinator, client),
                    TpLinkDecoClientInterfaceSensor(coordinator, client),
                )
            )

        new_nodes = [
            n
            for n in (snapshot.nodes if snapshot else [])
            if n.mac not in known_node_macs
        ]
        if new_nodes:
            known_node_macs.update(n.mac for n in new_nodes)
            entities = []
            for node in new_nodes:
                entities.extend(
                    [
                        TpLinkDecoDecoMacSensor(coordinator, node),
                        TpLinkDecoDecoIpSensor(coordinator, node),
                    ]
                )
                if node.role == "master":
                    entities.extend(
                        [
                            TpLinkDecoDecoCpuSensor(coordinator, node),
                            TpLinkDecoDecoMemorySensor(coordinator, node),
                            TpLinkDecoDecoClientsSensor(coordinator, node),
                        ]
                    )
            async_add_entities(entities)

    _add_new_entities()
    entry.async_on_unload(coordinator.async_add_listener(_add_new_entities))
