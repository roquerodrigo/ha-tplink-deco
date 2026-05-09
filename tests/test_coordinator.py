"""Tests for the TpLinkDecoDataUpdateCoordinator."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.tplink_deco.api import TpLinkDecoSnapshot
from custom_components.tplink_deco.api.errors import (
    TpLinkDecoApiClientAuthenticationError,
    TpLinkDecoApiClientCommunicationError,
)
from custom_components.tplink_deco.const import UNAVAILABLE_GRACE_PERIOD_SECONDS
from custom_components.tplink_deco.coordinator import TpLinkDecoDataUpdateCoordinator

from .factories import make_client, make_node, make_performance

if TYPE_CHECKING:
    from collections.abc import Iterator


def _build_coordinator(
    snapshot_or_exception: object,
) -> TpLinkDecoDataUpdateCoordinator:
    """Create a coordinator with a stubbed executor and runtime data."""
    coordinator = TpLinkDecoDataUpdateCoordinator.__new__(
        TpLinkDecoDataUpdateCoordinator
    )

    if isinstance(snapshot_or_exception, BaseException):

        async def _executor(_func: object) -> object:
            raise snapshot_or_exception
    else:

        async def _executor(_func: object) -> object:
            return snapshot_or_exception

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock(side_effect=_executor)
    coordinator.hass = hass

    api_client = MagicMock()
    runtime_data = MagicMock(client=api_client)
    config_entry = MagicMock(runtime_data=runtime_data)
    coordinator.config_entry = config_entry
    return coordinator


def _build_coordinator_with_executor(
    snapshots: Iterator[TpLinkDecoSnapshot],
) -> TpLinkDecoDataUpdateCoordinator:
    """Create a coordinator that returns the next snapshot on each fetch."""
    coordinator = TpLinkDecoDataUpdateCoordinator.__new__(
        TpLinkDecoDataUpdateCoordinator
    )

    async def _executor(_func: object) -> object:
        return next(snapshots)

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock(side_effect=_executor)
    coordinator.hass = hass

    api_client = MagicMock()
    runtime_data = MagicMock(client=api_client)
    config_entry = MagicMock(runtime_data=runtime_data)
    coordinator.config_entry = config_entry
    return coordinator


async def test_update_returns_grace_augmented_snapshot() -> None:
    """A first successful fetch returns the snapshot unchanged."""
    snapshot = TpLinkDecoSnapshot(
        clients=[make_client()],
        nodes=[make_node()],
        performance=make_performance(),
    )
    coordinator = _build_coordinator(snapshot)
    result = await coordinator._async_update_data()
    assert result.clients == snapshot.clients
    assert result.nodes == snapshot.nodes
    assert result.performance is snapshot.performance


async def test_update_auth_error_raises_config_entry_auth_failed() -> None:
    """Auth errors raise ConfigEntryAuthFailed."""
    coordinator = _build_coordinator(
        TpLinkDecoApiClientAuthenticationError("bad creds")
    )
    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()


async def test_update_communication_error_raises_update_failed() -> None:
    """Communication errors raise UpdateFailed."""
    coordinator = _build_coordinator(TpLinkDecoApiClientCommunicationError("offline"))
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


async def test_grace_keeps_missing_client_in_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A client missing from a fresh snapshot is re-injected within grace."""
    fake_time = 0.0
    monkeypatch.setattr(time, "monotonic", lambda: fake_time)

    client = make_client(mac="AA:00:00:00:00:01")
    node = make_node(mac="DE:CO:00:00:00:01")
    snapshots = iter(
        [
            TpLinkDecoSnapshot(clients=[client], nodes=[node], performance=None),
            TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None),
        ]
    )
    coordinator = _build_coordinator_with_executor(snapshots)

    first = await coordinator._async_update_data()
    assert [c.mac for c in first.clients] == ["AA:00:00:00:00:01"]

    fake_time = UNAVAILABLE_GRACE_PERIOD_SECONDS - 1
    second = await coordinator._async_update_data()
    assert [c.mac for c in second.clients] == ["AA:00:00:00:00:01"]


async def test_grace_drops_client_after_period(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A client missing past the grace period is dropped from the snapshot."""
    fake_time = 0.0
    monkeypatch.setattr(time, "monotonic", lambda: fake_time)

    client = make_client(mac="AA:00:00:00:00:02")
    snapshots = iter(
        [
            TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None),
            TpLinkDecoSnapshot(clients=[], nodes=[], performance=None),
        ]
    )
    coordinator = _build_coordinator_with_executor(snapshots)

    await coordinator._async_update_data()

    fake_time = UNAVAILABLE_GRACE_PERIOD_SECONDS + 1
    second = await coordinator._async_update_data()
    assert second.clients == []


async def test_grace_refreshes_on_reappearance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A client that returns within grace resets the timer with the latest data."""
    fake_time = 0.0
    monkeypatch.setattr(time, "monotonic", lambda: fake_time)

    initial = make_client(mac="AA:00:00:00:00:03", ip="10.0.0.10")
    refreshed = make_client(mac="AA:00:00:00:00:03", ip="10.0.0.20")
    snapshots = iter(
        [
            TpLinkDecoSnapshot(clients=[initial], nodes=[], performance=None),
            TpLinkDecoSnapshot(clients=[], nodes=[], performance=None),
            TpLinkDecoSnapshot(clients=[refreshed], nodes=[], performance=None),
            TpLinkDecoSnapshot(clients=[], nodes=[], performance=None),
        ]
    )
    coordinator = _build_coordinator_with_executor(snapshots)

    await coordinator._async_update_data()

    fake_time = 30.0
    second = await coordinator._async_update_data()
    assert second.clients[0].ip == "10.0.0.10"

    fake_time = 60.0
    third = await coordinator._async_update_data()
    assert third.clients[0].ip == "10.0.0.20"

    fake_time = 60.0 + UNAVAILABLE_GRACE_PERIOD_SECONDS - 1
    fourth = await coordinator._async_update_data()
    assert fourth.clients[0].ip == "10.0.0.20"


async def test_grace_keeps_missing_node_in_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A node missing from a fresh snapshot is re-injected within grace."""
    fake_time = 0.0
    monkeypatch.setattr(time, "monotonic", lambda: fake_time)

    node = make_node(mac="DE:CO:00:00:00:02")
    snapshots = iter(
        [
            TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None),
            TpLinkDecoSnapshot(clients=[], nodes=[], performance=None),
        ]
    )
    coordinator = _build_coordinator_with_executor(snapshots)

    await coordinator._async_update_data()

    fake_time = UNAVAILABLE_GRACE_PERIOD_SECONDS - 1
    second = await coordinator._async_update_data()
    assert [n.mac for n in second.nodes] == ["DE:CO:00:00:00:02"]


async def test_grace_drops_node_after_period(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A node missing past the grace period is dropped from the snapshot."""
    fake_time = 0.0
    monkeypatch.setattr(time, "monotonic", lambda: fake_time)

    node = make_node(mac="DE:CO:00:00:00:03")
    snapshots = iter(
        [
            TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None),
            TpLinkDecoSnapshot(clients=[], nodes=[], performance=None),
        ]
    )
    coordinator = _build_coordinator_with_executor(snapshots)

    await coordinator._async_update_data()

    fake_time = UNAVAILABLE_GRACE_PERIOD_SECONDS + 1
    second = await coordinator._async_update_data()
    assert second.nodes == []


async def test_grace_count_includes_held_clients(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    The grace-augmented snapshot keeps the client count stable on transient drops.

    Regression for the count sensor flapping observed in production: a client
    that briefly disappears between polls used to immediately drop the count;
    with grace at the coordinator level, the count stays steady.
    """
    fake_time = 0.0
    monkeypatch.setattr(time, "monotonic", lambda: fake_time)

    clients = [make_client(mac=f"AA:00:00:00:00:{i:02x}") for i in range(3)]
    snapshots = iter(
        [
            TpLinkDecoSnapshot(clients=list(clients), nodes=[], performance=None),
            TpLinkDecoSnapshot(clients=clients[:2], nodes=[], performance=None),
        ]
    )
    coordinator = _build_coordinator_with_executor(snapshots)

    first = await coordinator._async_update_data()
    assert len(first.clients) == 3

    fake_time = 30.0
    second = await coordinator._async_update_data()
    assert len(second.clients) == 3
