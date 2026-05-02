"""Communication error for the TP-Link Deco API client."""

from __future__ import annotations

from .base import TpLinkDecoApiClientError


class TpLinkDecoApiClientCommunicationError(TpLinkDecoApiClientError):
    """Exception to indicate a communication error."""
