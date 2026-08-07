"""Tests for binary sensor entities."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.tplink_deco.api import TpLinkDecoSnapshot
from custom_components.tplink_deco.binary_sensor.client_connected import (
    TpLinkDecoClientConnectedBinarySensor,
)
from custom_components.tplink_deco.binary_sensor.deco_internet import (
    TpLinkDecoDecoInternetBinarySensor,
)

from .factories import make_client, make_node


def _coord(snapshot: TpLinkDecoSnapshot) -> MagicMock:
    mock = MagicMock()
    mock.data = snapshot
    mock.last_update_success = True
    return mock


def test_client_connected_when_present() -> None:
    """Client is on when present in the snapshot."""
    client = make_client(mac="AA:BB:CC:DD:EE:90")
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    sensor = TpLinkDecoClientConnectedBinarySensor(_coord(snapshot), client)
    assert sensor.is_on is True
    assert sensor.available is True
    assert sensor.unique_id == "AA:BB:CC:DD:EE:90_connected"


def test_client_disconnected_when_absent() -> None:
    """Client is off but the entity remains available when offline."""
    client = make_client()
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[], performance=None)
    sensor = TpLinkDecoClientConnectedBinarySensor(_coord(snapshot), client)
    assert sensor.is_on is False
    assert sensor.available is True


def test_deco_internet_online() -> None:
    """Internet binary sensor is on when inet_status is online."""
    node = make_node(mac="DE:CO:00:00:00:91", inet_status="online")
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None)
    sensor = TpLinkDecoDecoInternetBinarySensor(_coord(snapshot), node)
    assert sensor.is_on is True
    assert sensor.unique_id == "DE:CO:00:00:00:91_internet"


def test_deco_internet_offline() -> None:
    """Internet binary sensor is off for any other status."""
    node = make_node(inet_status="offline")
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None)
    sensor = TpLinkDecoDecoInternetBinarySensor(_coord(snapshot), node)
    assert sensor.is_on is False


def test_deco_internet_none_when_node_missing() -> None:
    """Returns None if the node disappears from the snapshot."""
    node = make_node()
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[], performance=None)
    sensor = TpLinkDecoDecoInternetBinarySensor(_coord(snapshot), node)
    assert sensor.is_on is None


def test_client_disconnected_when_reported_offline() -> None:
    """A client the router lists with online=False reports off."""
    client = make_client(online=False)
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    sensor = TpLinkDecoClientConnectedBinarySensor(_coord(snapshot), client)
    assert sensor.is_on is False
    assert sensor.available is True
