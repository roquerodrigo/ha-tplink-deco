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


def _patch_deco(side_effect: object | None = None) -> MagicMock:
    """Patch DecoClient and configure it as a context manager."""
    deco = MagicMock()
    deco.get_client_list.return_value = [make_client()]
    deco.get_device_list.return_value = [make_node()]
    deco.get_performance.return_value = make_performance()

    cm = MagicMock()
    cm.__enter__.return_value = deco
    cm.__exit__.return_value = False

    factory = MagicMock(return_value=cm)
    if side_effect is not None:
        factory.side_effect = side_effect
    return factory


def test_get_snapshot_returns_dataclass() -> None:
    """A successful snapshot returns a TpLinkDecoSnapshot."""
    factory = _patch_deco()
    with patch("custom_components.tplink_deco.api.client.DecoClient", factory):
        client = TpLinkDecoApiClient("host", "user", "pass")
        snapshot = client.get_snapshot()
    assert len(snapshot.clients) == 1
    assert len(snapshot.nodes) == 1
    assert snapshot.performance is not None


def test_get_snapshot_authentication_error() -> None:
    """Authentication errors are wrapped."""
    factory = _patch_deco(side_effect=AuthenticationError("bad creds"))
    with patch("custom_components.tplink_deco.api.client.DecoClient", factory):
        client = TpLinkDecoApiClient("host", "user", "pass")
        with pytest.raises(TpLinkDecoApiClientAuthenticationError):
            client.get_snapshot()


def test_get_snapshot_transport_error() -> None:
    """Transport errors are wrapped as communication errors."""
    factory = _patch_deco(side_effect=TransportError("network"))
    with patch("custom_components.tplink_deco.api.client.DecoClient", factory):
        client = TpLinkDecoApiClient("host", "user", "pass")
        with pytest.raises(TpLinkDecoApiClientCommunicationError):
            client.get_snapshot()


def test_get_snapshot_api_error() -> None:
    """API errors are wrapped as communication errors."""
    factory = _patch_deco(side_effect=ApiError("api"))
    with patch("custom_components.tplink_deco.api.client.DecoClient", factory):
        client = TpLinkDecoApiClient("host", "user", "pass")
        with pytest.raises(TpLinkDecoApiClientCommunicationError):
            client.get_snapshot()


def test_get_snapshot_generic_deco_error() -> None:
    """Other DecoError subclasses are wrapped as the base error."""
    factory = _patch_deco(side_effect=DecoError("oops"))
    with patch("custom_components.tplink_deco.api.client.DecoClient", factory):
        client = TpLinkDecoApiClient("host", "user", "pass")
        with pytest.raises(TpLinkDecoApiClientError):
            client.get_snapshot()
