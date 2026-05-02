"""Coordinator data snapshot for the TP-Link Deco integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tplink_deco_api import ClientDevice, Device, Performance


@dataclass
class TpLinkDecoSnapshot:
    """Combined data fetched in a single router session."""

    clients: list[ClientDevice]
    nodes: list[Device]
    performance: Performance | None
