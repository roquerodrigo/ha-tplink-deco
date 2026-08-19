"""Tests for the TpLinkDecoApiClient wrapper."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from tplink_deco_api.exceptions import (
    ApiError,
    AuthenticationError,
    DecoError,
    TransportError,
)

from custom_components.tplink_deco.api import TpLinkDecoApiClient
from custom_components.tplink_deco.api.errors import (
    TpLinkDecoApiClientAuthenticationError,
    TpLinkDecoApiClientCommunicationError,
    TpLinkDecoApiClientError,
)

from .factories import make_client, make_node, make_performance


def _session() -> MagicMock:
    """Return a mock DecoClient session answering every read call."""
    session = MagicMock()
    session.get_client_list.return_value = [make_client()]
    session.get_device_list.return_value = [make_node()]
    session.get_performance.return_value = make_performance()
    return session


def _factory(*sessions: MagicMock) -> MagicMock:
    """Return a DecoClient factory handing out the given sessions in order."""
    return MagicMock(side_effect=list(sessions) or [_session()])


def _patch(factory: MagicMock) -> object:
    """Patch the DecoClient used by the API client wrapper."""
    return patch("custom_components.tplink_deco.api.client.DecoClient", factory)


def test_get_snapshot_returns_dataclass() -> None:
    """A successful snapshot returns a TpLinkDecoSnapshot."""
    with _patch(_factory()):
        client = TpLinkDecoApiClient("host", "user", "pass")
        snapshot = client.get_snapshot()
    assert len(snapshot.clients) == 1
    assert len(snapshot.nodes) == 1
    assert snapshot.performance is not None


def test_session_is_reused_across_polls() -> None:
    """Consecutive polls share one session instead of logging in again."""
    session = _session()
    factory = _factory(session)
    with _patch(factory):
        client = TpLinkDecoApiClient("host", "user", "pass")
        client.get_snapshot()
        client.get_snapshot()
    assert factory.call_count == 1
    assert session.login.call_count == 1
    assert session.get_client_list.call_count == 2


def test_request_timeout_is_handed_to_the_sdk() -> None:
    """The configured timeout reaches the underlying DecoClient."""
    factory = _factory()
    with _patch(factory):
        TpLinkDecoApiClient("host", "user", "pass", timeout=45).get_snapshot()
    assert factory.call_args.kwargs["timeout"] == 45


def test_rejected_session_is_renewed_once() -> None:
    """A session the router dropped is replaced and the poll retried."""
    dropped = _session()
    dropped.get_client_list.side_effect = [[make_client()], ApiError(-40401)]
    renewed = _session()
    factory = _factory(dropped, renewed)
    with _patch(factory):
        client = TpLinkDecoApiClient("host", "user", "pass")
        client.get_snapshot()
        snapshot = client.get_snapshot()
    assert factory.call_count == 2
    assert len(snapshot.clients) == 1


@pytest.mark.parametrize(
    "exception",
    [AuthenticationError("expired"), TransportError("denied", status_code=401)],
    ids=["authentication", "http-401"],
)
def test_session_rejection_flavours_are_retried(exception: DecoError) -> None:
    """Every way the router can reject a session leads to a new login."""
    dropped = _session()
    dropped.get_device_list.side_effect = [[make_node()], exception]
    factory = _factory(dropped, _session())
    with _patch(factory):
        client = TpLinkDecoApiClient("host", "user", "pass")
        client.get_snapshot()
        client.get_snapshot()
    assert factory.call_count == 2


def test_server_error_on_a_reused_session_is_not_retried() -> None:
    """A failure unrelated to the session is reported without logging in again."""
    session = _session()
    session.get_client_list.side_effect = [
        [make_client()],
        TransportError("boom", status_code=500),
    ]
    factory = _factory(session)
    with _patch(factory):
        client = TpLinkDecoApiClient("host", "user", "pass")
        client.get_snapshot()
        with pytest.raises(TpLinkDecoApiClientCommunicationError):
            client.get_snapshot()
    assert factory.call_count == 1


def test_failed_poll_forces_a_new_login() -> None:
    """A broken session is dropped so the next poll starts a fresh one."""
    broken = _session()
    broken.get_performance.side_effect = TransportError("boom", status_code=500)
    factory = _factory(broken, _session())
    with _patch(factory):
        client = TpLinkDecoApiClient("host", "user", "pass")
        with pytest.raises(TpLinkDecoApiClientCommunicationError):
            client.get_snapshot()
        client.get_snapshot()
    assert factory.call_count == 2


def test_get_snapshot_authentication_error() -> None:
    """Authentication errors are wrapped."""
    session = _session()
    session.login.side_effect = AuthenticationError("bad creds")
    with _patch(_factory(session)):
        client = TpLinkDecoApiClient("host", "user", "pass")
        with pytest.raises(TpLinkDecoApiClientAuthenticationError):
            client.get_snapshot()


def test_get_snapshot_transport_error() -> None:
    """Transport errors are wrapped as communication errors."""
    session = _session()
    session.login.side_effect = TransportError("network")
    with _patch(_factory(session)):
        client = TpLinkDecoApiClient("host", "user", "pass")
        with pytest.raises(TpLinkDecoApiClientCommunicationError):
            client.get_snapshot()


def test_get_snapshot_api_error() -> None:
    """API errors are wrapped as communication errors."""
    session = _session()
    session.get_client_list.side_effect = ApiError(-1)
    with _patch(_factory(session)):
        client = TpLinkDecoApiClient("host", "user", "pass")
        with pytest.raises(TpLinkDecoApiClientCommunicationError):
            client.get_snapshot()


def test_get_snapshot_socket_timeout() -> None:
    """A socket timeout leaking from the SDK becomes a communication error."""
    session = _session()
    session.get_client_list.side_effect = TimeoutError("timed out")
    with _patch(_factory(session)):
        client = TpLinkDecoApiClient("host", "user", "pass", timeout=30)
        with pytest.raises(TpLinkDecoApiClientCommunicationError, match="within 30s"):
            client.get_snapshot()


def test_get_snapshot_generic_deco_error() -> None:
    """Other DecoError subclasses are wrapped as the base error."""
    session = _session()
    session.get_client_list.side_effect = DecoError("oops")
    with _patch(_factory(session)):
        client = TpLinkDecoApiClient("host", "user", "pass")
        with pytest.raises(TpLinkDecoApiClientError):
            client.get_snapshot()
