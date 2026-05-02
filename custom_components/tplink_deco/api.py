"""TP-Link Deco API client wrapper."""

from __future__ import annotations

from tplink_deco_api import ClientDevice, DecoClient
from tplink_deco_api.exceptions import ApiError, AuthenticationError, DecoError, TransportError


class TpLinkDecoApiClientError(Exception):
    """Exception to indicate a general API error."""


class TpLinkDecoApiClientCommunicationError(TpLinkDecoApiClientError):
    """Exception to indicate a communication error."""


class TpLinkDecoApiClientAuthenticationError(TpLinkDecoApiClientError):
    """Exception to indicate an authentication error."""


class TpLinkDecoApiClient:
    """TP-Link Deco API client."""

    def __init__(self, host: str, username: str, password: str) -> None:
        """Initialize the client."""
        self._host = host
        self._username = username
        self._password = password

    def get_clients(self) -> list[ClientDevice]:
        """Get all connected clients from the TP-Link Deco router."""
        try:
            with DecoClient(self._host, self._username, self._password) as deco:
                return deco.get_client_list()
        except AuthenticationError as exception:
            msg = "Invalid credentials"
            raise TpLinkDecoApiClientAuthenticationError(msg) from exception
        except (TransportError, ApiError) as exception:
            msg = f"Error communicating with the router - {exception}"
            raise TpLinkDecoApiClientCommunicationError(msg) from exception
        except DecoError as exception:
            msg = f"Unexpected error - {exception}"
            raise TpLinkDecoApiClientError(msg) from exception
