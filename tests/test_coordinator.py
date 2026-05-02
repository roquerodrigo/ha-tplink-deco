"""Tests for the TpLinkDecoDataUpdateCoordinator."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.tplink_deco.api import TpLinkDecoSnapshot
from custom_components.tplink_deco.api.errors import (
    TpLinkDecoApiClientAuthenticationError,
    TpLinkDecoApiClientCommunicationError,
)
from custom_components.tplink_deco.coordinator import TpLinkDecoDataUpdateCoordinator

from .factories import make_client, make_node, make_performance


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


async def test_update_returns_snapshot() -> None:
    """A successful executor call returns the snapshot directly."""
    snapshot = TpLinkDecoSnapshot(
        clients=[make_client()],
        nodes=[make_node()],
        performance=make_performance(),
    )
    coordinator = _build_coordinator(snapshot)
    result = await coordinator._async_update_data()
    assert result is snapshot


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
