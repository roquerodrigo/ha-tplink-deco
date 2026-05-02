"""TP-Link Deco API client wrapper."""

from __future__ import annotations

from tplink_deco_api import DecoClient
from tplink_deco_api.exceptions import (
    ApiError,
    AuthenticationError,
    DecoError,
    TransportError,
)

from .errors import (
    TpLinkDecoApiClientAuthenticationError,
    TpLinkDecoApiClientCommunicationError,
    TpLinkDecoApiClientError,
)
from .snapshot import TpLinkDecoSnapshot


class TpLinkDecoApiClient:
    """TP-Link Deco API client."""

    def __init__(self, host: str, username: str, password: str) -> None:
        self._host = host
        self._username = username
        self._password = password

    def get_snapshot(self) -> TpLinkDecoSnapshot:
        """Fetch clients, nodes and performance in a single authenticated session."""
        try:
            with DecoClient(self._host, self._username, self._password) as deco:
                clients = deco.get_client_list()
                nodes = deco.get_device_list()
                performance = deco.get_performance()
            return TpLinkDecoSnapshot(
                clients=clients, nodes=nodes, performance=performance
            )
        except AuthenticationError as exception:
            msg = "Invalid credentials"
            raise TpLinkDecoApiClientAuthenticationError(msg) from exception
        except (TransportError, ApiError) as exception:
            msg = f"Error communicating with the router - {exception}"
            raise TpLinkDecoApiClientCommunicationError(msg) from exception
        except DecoError as exception:
            msg = f"Unexpected error - {exception}"
            raise TpLinkDecoApiClientError(msg) from exception
