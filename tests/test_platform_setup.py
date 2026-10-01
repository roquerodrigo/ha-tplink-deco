"""Tests for the async_setup_entry of each platform."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from custom_components.tplink_deco.api import TpLinkDecoSnapshot
from custom_components.tplink_deco.binary_sensor import (
    async_setup_entry as async_setup_binary_sensor,
)
from custom_components.tplink_deco.device_tracker import (
    async_setup_entry as async_setup_tracker,
)
from custom_components.tplink_deco.sensor import (
    async_setup_entry as async_setup_sensor,
)

from .factories import make_client, make_node

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


def _entry_with_snapshot(snapshot: TpLinkDecoSnapshot) -> MagicMock:
    """Build a config entry whose runtime_data exposes a coordinator."""
    coordinator = MagicMock()
    coordinator.data = snapshot
    coordinator.async_add_listener = MagicMock(return_value=lambda: None)
    entry = MagicMock()
    entry.runtime_data.coordinator = coordinator
    return entry


@pytest.mark.parametrize(
    ("setup", "expected_count"),
    [
        (async_setup_sensor, 6 + 7),
        (async_setup_binary_sensor, 1 + 1),
        (async_setup_tracker, 1),
    ],
)
async def test_platform_registers_entities_for_initial_snapshot(
    hass: HomeAssistant, setup: object, expected_count: int
) -> None:
    """Each platform registers entities for clients and nodes already present."""
    snapshot = TpLinkDecoSnapshot(
        clients=[make_client()],
        nodes=[make_node(role="master")],
        performance=None,
    )
    entry = _entry_with_snapshot(snapshot)
    added: list[object] = []

    def add_entities(items: object) -> None:
        added.extend(list(items))

    await setup(hass, entry, add_entities)
    assert len(added) == expected_count


async def test_sensor_platform_skips_master_only_sensors_for_satellites(
    hass: HomeAssistant,
) -> None:
    """Satellite Deco nodes get only base sensors (no CPU/memory/clients)."""
    snapshot = TpLinkDecoSnapshot(
        clients=[],
        nodes=[make_node(role="slave", mac="11:22:33:44:55:66")],
        performance=None,
    )
    entry = _entry_with_snapshot(snapshot)
    added: list[object] = []
    await async_setup_sensor(hass, entry, added.extend)
    assert len(added) == 2


async def test_platform_listener_registers_new_clients_on_update(
    hass: HomeAssistant,
) -> None:
    """The registered listener picks up clients that appear later."""
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[], performance=None)
    entry = _entry_with_snapshot(snapshot)
    coordinator = entry.runtime_data.coordinator

    captured_listener: list[object] = []

    def capture_listener(callback: object) -> object:
        captured_listener.append(callback)
        return lambda: None

    coordinator.async_add_listener = capture_listener
    added: list[object] = []
    await async_setup_tracker(hass, entry, added.extend)
    assert added == []

    coordinator.data = TpLinkDecoSnapshot(
        clients=[make_client(mac="AA:00:00:00:00:99")],
        nodes=[],
        performance=None,
    )
    captured_listener[0]()
    assert len(added) == 1
