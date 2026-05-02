"""Base entities for the TP-Link Deco integration."""

from .client import TpLinkDecoClientEntity
from .deco import TpLinkDecoDecoEntity

__all__ = ["TpLinkDecoClientEntity", "TpLinkDecoDecoEntity"]
