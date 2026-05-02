"""Authentication error for the TP-Link Deco API client."""

from __future__ import annotations

from .base import TpLinkDecoApiClientError


class TpLinkDecoApiClientAuthenticationError(TpLinkDecoApiClientError):
    """Exception to indicate an authentication error."""
