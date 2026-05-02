"""Custom types for tplink_deco."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import TpLinkDecoApiClient
    from .coordinator import TpLinkDecoDataUpdateCoordinator
    from .node_coordinator import TpLinkDecoNodeCoordinator


type TpLinkDecoConfigEntry = ConfigEntry[TpLinkDecoData]


@dataclass
class TpLinkDecoData:
    """Data for the TP-Link Deco integration."""

    client: TpLinkDecoApiClient
    coordinator: TpLinkDecoDataUpdateCoordinator
    node_coordinator: TpLinkDecoNodeCoordinator
    integration: Integration
