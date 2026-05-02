"""Custom types for the TP-Link Deco integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import TpLinkDecoApiClient
    from .coordinator import TpLinkDecoDataUpdateCoordinator


type TpLinkDecoConfigEntry = ConfigEntry[TpLinkDecoData]


@dataclass
class TpLinkDecoData:
    """Data for the TP-Link Deco integration."""

    client: TpLinkDecoApiClient
    coordinator: TpLinkDecoDataUpdateCoordinator
    integration: Integration
