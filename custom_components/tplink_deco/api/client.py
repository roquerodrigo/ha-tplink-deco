"""TP-Link Deco API client wrapper."""

from __future__ import annotations

from threading import Lock

from tplink_deco_api import DecoClient
from tplink_deco_api.exceptions import (
    ApiError,
    AuthenticationError,
    DecoError,
    TransportError,
)

from custom_components.tplink_deco.const import DEFAULT_TIMEOUT_SECONDS, LOGGER

from .errors import (
    TpLinkDecoApiClientAuthenticationError,
    TpLinkDecoApiClientCommunicationError,
    TpLinkDecoApiClientError,
)
from .snapshot import TpLinkDecoSnapshot

SESSION_REJECTED_STATUS_CODES = frozenset({401, 403})


class TpLinkDecoApiClient:
    """TP-Link Deco API client."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        """Store credentials and the timeout applied to each router request."""
        self._host = host
        self._username = username
        self._password = password
        self._timeout = timeout
        self._session: DecoClient | None = None
        self._lock = Lock()

    def get_snapshot(self) -> TpLinkDecoSnapshot:
        """
        Fetch clients, nodes and performance over a single reused session.

        The router only keeps one session per account, so logging in on every
        poll both costs a full handshake and kicks the user out of the Deco
        app. The session is kept open across polls and only renewed once the
        router rejects it.
        """
        with self._lock:
            try:
                return self._fetch_reusing_session()
            except (DecoError, OSError) as exception:
                self._session = None
                raise self._wrap(exception) from exception

    def _fetch_reusing_session(self) -> TpLinkDecoSnapshot:
        """Fetch over the open session, logging in again if it was rejected."""
        session = self._session
        if session is None:
            return self._fetch(self._login())
        try:
            return self._fetch(session)
        except DecoError as exception:
            if not _is_session_rejected(exception):
                raise
            LOGGER.debug("Router rejected the open session, logging in again")
            return self._fetch(self._login())

    def _login(self) -> DecoClient:
        """Open a router session and keep it for the following fetches."""
        session = DecoClient(
            self._host,
            self._username,
            self._password,
            timeout=self._timeout,
        )
        session.login()
        self._session = session
        return session

    @staticmethod
    def _fetch(session: DecoClient) -> TpLinkDecoSnapshot:
        """Read clients, nodes and performance through an open session."""
        return TpLinkDecoSnapshot(
            clients=session.get_client_list(),
            nodes=session.get_device_list(),
            performance=session.get_performance(),
        )

    def _wrap(self, exception: DecoError | OSError) -> TpLinkDecoApiClientError:
        """Map an SDK or socket failure onto this integration's hierarchy."""
        if isinstance(exception, AuthenticationError):
            return TpLinkDecoApiClientAuthenticationError(
                "Failed to authenticate with the router: invalid credentials"
            )
        if isinstance(exception, TimeoutError):
            return TpLinkDecoApiClientCommunicationError(
                f"Failed to reach the router: no response within {self._timeout:g}s"
            )
        if isinstance(exception, TransportError | ApiError | OSError):
            return TpLinkDecoApiClientCommunicationError(
                f"Failed to communicate with the router: {exception}"
            )
        return TpLinkDecoApiClientError(f"Failed to query the router: {exception}")


def _is_session_rejected(exception: DecoError) -> bool:
    """Tell a router-side session drop apart from a genuine failure."""
    if isinstance(exception, TransportError):
        return exception.status_code in SESSION_REJECTED_STATUS_CODES
    return isinstance(exception, AuthenticationError | ApiError)
