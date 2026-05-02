"""TP-Link Deco API client wrapper."""

from __future__ import annotations

from tplink_deco_api import ClientDevice, DecoClient, Device
from tplink_deco_api.exceptions import ApiError, AuthenticationError, DecoError, TransportError

from .errors import (
    TpLinkDecoApiClientAuthenticationError,
    TpLinkDecoApiClientCommunicationError,
    TpLinkDecoApiClientError,
)


class TpLinkDecoApiClient:
    """TP-Link Deco API client."""

    def __init__(self, host: str, username: str, password: str) -> None:
        self._host = host
        self._username = username
        self._password = password

    def get_snapshot(self) -> tuple[list[ClientDevice], list[Device]]:
        """Fetch clients and nodes in a single authenticated session."""
        try:
            with DecoClient(self._host, self._username, self._password) as deco:
                clients = deco.get_client_list()
                nodes = deco.get_device_list()
            return clients, nodes
        except AuthenticationError as exception:
            msg = "Invalid credentials"
            raise TpLinkDecoApiClientAuthenticationError(msg) from exception
        except (TransportError, ApiError) as exception:
            msg = f"Error communicating with the router - {exception}"
            raise TpLinkDecoApiClientCommunicationError(msg) from exception
        except DecoError as exception:
            msg = f"Unexpected error - {exception}"
            raise TpLinkDecoApiClientError(msg) from exception
