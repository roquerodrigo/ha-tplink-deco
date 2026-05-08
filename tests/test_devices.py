"""Tests for the base device classes."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC

from custom_components.tplink_deco.api import TpLinkDecoSnapshot
from custom_components.tplink_deco.const import DOMAIN, MANUFACTURER
from custom_components.tplink_deco.device import (
    TpLinkDecoClientDevice,
    TpLinkDecoDecoDevice,
)

from .factories import make_client, make_node, make_performance

if TYPE_CHECKING:
    import pytest


def _coordinator(snapshot: TpLinkDecoSnapshot) -> MagicMock:
    mock = MagicMock()
    mock.data = snapshot
    mock.last_update_success = True
    return mock


def test_client_device_info_links_to_master() -> None:
    """The client device_info points to the master node via via_device."""
    client = make_client(mac="AA:11:22:33:44:55", name="Phone")
    master = make_node(mac="DD:EE:FF:00:11:22", role="master")
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[master], performance=None)
    device = TpLinkDecoClientDevice(_coordinator(snapshot), client)

    info = device.device_info
    assert info["identifiers"] == {(DOMAIN, client.mac)}
    assert (CONNECTION_NETWORK_MAC, client.mac) in info["connections"]
    assert info["via_device"] == (DOMAIN, master.mac)
    assert info["name"] == "Phone"


def test_client_device_info_without_master_node() -> None:
    """device_info returns no via_device when no master is present."""
    client = make_client()
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    device = TpLinkDecoClientDevice(_coordinator(snapshot), client)
    assert "via_device" not in device.device_info


def test_client_available_when_present() -> None:
    """Available is true when the client appears in the snapshot."""
    client = make_client()
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    device = TpLinkDecoClientDevice(_coordinator(snapshot), client)
    assert device.available is True


def test_client_unavailable_when_offline() -> None:
    """Available is false when the client is no longer in the snapshot."""
    client = make_client()
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[], performance=None)
    device = TpLinkDecoClientDevice(_coordinator(snapshot), client)
    assert device.available is False
    assert device.client is None


def test_deco_device_info_includes_all_bssids() -> None:
    """Deco device_info exposes main MAC plus every populated BSSID."""
    node = make_node(
        mac="AA:BB:CC:00:00:01",
        bssid_2g="AA:BB:CC:00:00:02",
        bssid_5g="AA:BB:CC:00:00:03",
        bssid_sta_2g="AA:BB:CC:00:00:04",
        bssid_sta_5g="",
    )
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None)
    device = TpLinkDecoDecoDevice(_coordinator(snapshot), node)

    info = device.device_info
    macs = {mac for kind, mac in info["connections"] if kind == CONNECTION_NETWORK_MAC}
    assert macs == {
        "AA:BB:CC:00:00:01",
        "AA:BB:CC:00:00:02",
        "AA:BB:CC:00:00:03",
        "AA:BB:CC:00:00:04",
    }
    assert info["manufacturer"] == MANUFACTURER
    assert info["model"] == node.device_model
    assert info["sw_version"] == node.software_ver


def test_deco_device_uses_custom_nickname_when_present() -> None:
    """Custom nickname overrides the default nickname."""
    node = make_node(nickname="Default", custom_nickname="Office")
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None)
    device = TpLinkDecoDecoDevice(_coordinator(snapshot), node)
    assert device.device_info["name"] == "Office"


def test_deco_unavailable_when_node_missing() -> None:
    """The Deco device is unavailable when removed from the snapshot."""
    node = make_node()
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[], performance=make_performance())
    device = TpLinkDecoDecoDevice(_coordinator(snapshot), node)
    assert device.available is False
    assert device.node is None


def test_client_stays_available_during_grace_period(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A client that disappears stays available for 90s using its cached state."""
    fake_time = 0.0
    monkeypatch.setattr(time, "monotonic", lambda: fake_time)

    client = make_client()
    coordinator = _coordinator(
        TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None),
    )
    device = TpLinkDecoClientDevice(coordinator, client)
    assert device.available is True
    assert device.client is client

    coordinator.data = TpLinkDecoSnapshot(clients=[], nodes=[], performance=None)
    fake_time = 30.0
    assert device.available is True
    assert device.client is client


def test_client_unavailable_after_grace_period(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The client becomes unavailable once the 90s grace period elapses."""
    fake_time = 0.0
    monkeypatch.setattr(time, "monotonic", lambda: fake_time)

    client = make_client()
    coordinator = _coordinator(
        TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None),
    )
    device = TpLinkDecoClientDevice(coordinator, client)
    assert device.client is client

    coordinator.data = TpLinkDecoSnapshot(clients=[], nodes=[], performance=None)
    fake_time = 95.0
    assert device.available is False
    assert device.client is None


def test_client_grace_period_resets_when_device_returns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reappearing during the grace period resets the timer and refreshes the cache."""
    fake_time = 0.0
    monkeypatch.setattr(time, "monotonic", lambda: fake_time)

    client = make_client(ip="192.168.0.10")
    coordinator = _coordinator(
        TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None),
    )
    device = TpLinkDecoClientDevice(coordinator, client)
    assert device.client is client

    coordinator.data = TpLinkDecoSnapshot(clients=[], nodes=[], performance=None)
    fake_time = 30.0
    assert device.available is True

    refreshed = make_client(ip="192.168.0.20")
    coordinator.data = TpLinkDecoSnapshot(
        clients=[refreshed],
        nodes=[],
        performance=None,
    )
    fake_time = 60.0
    assert device.client is refreshed

    coordinator.data = TpLinkDecoSnapshot(clients=[], nodes=[], performance=None)
    fake_time = 145.0
    assert device.available is True
    assert device.client is refreshed

    fake_time = 155.0
    assert device.available is False
    assert device.client is None


def test_deco_stays_available_during_grace_period(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A Deco node that disappears stays available for 90s using cached state."""
    fake_time = 0.0
    monkeypatch.setattr(time, "monotonic", lambda: fake_time)

    node = make_node()
    coordinator = _coordinator(
        TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None),
    )
    device = TpLinkDecoDecoDevice(coordinator, node)
    assert device.available is True

    coordinator.data = TpLinkDecoSnapshot(clients=[], nodes=[], performance=None)
    fake_time = 89.0
    assert device.available is True
    assert device.node is node


def test_deco_unavailable_after_grace_period(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The Deco node becomes unavailable once the 90s grace period elapses."""
    fake_time = 0.0
    monkeypatch.setattr(time, "monotonic", lambda: fake_time)

    node = make_node()
    coordinator = _coordinator(
        TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None),
    )
    device = TpLinkDecoDecoDevice(coordinator, node)
    assert device.node is node

    coordinator.data = TpLinkDecoSnapshot(clients=[], nodes=[], performance=None)
    fake_time = 90.0
    assert device.available is False
    assert device.node is None
