"""Coordinator data snapshot for the TP-Link Deco integration."""

from __future__ import annotations

from dataclasses import dataclass

from tplink_deco_api import ClientDevice, Device
from tplink_deco_api import Performance


@dataclass
class TpLinkDecoSnapshot:
    """Combined data fetched in a single router session."""

    clients: list[ClientDevice]
    nodes: list[Device]
    performance: Performance | None
