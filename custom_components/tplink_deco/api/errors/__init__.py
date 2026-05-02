"""Exceptions for the TP-Link Deco API client."""

from .authentication import TpLinkDecoApiClientAuthenticationError
from .base import TpLinkDecoApiClientError
from .communication import TpLinkDecoApiClientCommunicationError

__all__ = [
    "TpLinkDecoApiClientAuthenticationError",
    "TpLinkDecoApiClientCommunicationError",
    "TpLinkDecoApiClientError",
]
