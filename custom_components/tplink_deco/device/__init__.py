"""Base devices for the TP-Link Deco integration."""

from .client import TpLinkDecoClientDevice
from .deco import TpLinkDecoDecoDevice

__all__ = ["TpLinkDecoClientDevice", "TpLinkDecoDecoDevice"]
