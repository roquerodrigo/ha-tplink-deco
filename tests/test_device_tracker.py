"""Tests for the TP-Link Deco client tracker."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.components.device_tracker import SourceType

from custom_components.tplink_deco.api import TpLinkDecoSnapshot
from custom_components.tplink_deco.device_tracker.client import TpLinkDecoClientTracker

from .factories import make_client


def _coord(snapshot: TpLinkDecoSnapshot) -> MagicMock:
    mock = MagicMock()
    mock.data = snapshot
    mock.last_update_success = True
    return mock


def test_tracker_connected_when_client_present() -> None:
    """Tracker reports connected when client is in the snapshot."""
    client = make_client(mac="AA:BB:CC:DD:EE:99", ip="10.0.0.42")
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    tracker = TpLinkDecoClientTracker(_coord(snapshot), client)
    assert tracker.is_connected is True
    assert tracker.ip_address == "10.0.0.42"
    assert tracker.mac_address == "AA:BB:CC:DD:EE:99"
    assert tracker.unique_id == "AA:BB:CC:DD:EE:99_tracker"


def test_tracker_disconnected_when_client_absent() -> None:
    """Tracker reports disconnected when the client is not in the snapshot."""
    client = make_client()
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[], performance=None)
    tracker = TpLinkDecoClientTracker(_coord(snapshot), client)
    assert tracker.is_connected is False
    assert tracker.ip_address is None
    assert tracker.available is True


def test_tracker_source_type_is_router() -> None:
    """The tracker is always a router source."""
    client = make_client()
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    tracker = TpLinkDecoClientTracker(_coord(snapshot), client)
    assert tracker.source_type == SourceType.ROUTER
