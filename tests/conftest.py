"""Common fixtures for the TP-Link Deco tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.tplink_deco.api import TpLinkDecoSnapshot

from .factories import make_client, make_node, make_performance


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> None:
    """Enable custom integrations for every test."""


@pytest.fixture
def snapshot() -> TpLinkDecoSnapshot:
    """Return a snapshot with one client and one master node."""
    return TpLinkDecoSnapshot(
        clients=[make_client()],
        nodes=[make_node()],
        performance=make_performance(),
    )


@pytest.fixture
def coordinator(snapshot: TpLinkDecoSnapshot) -> MagicMock:
    """Return a mock coordinator exposing the snapshot as data."""
    mock = MagicMock()
    mock.data = snapshot
    mock.last_update_success = True
    return mock
