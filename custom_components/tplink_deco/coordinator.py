"""DataUpdateCoordinator for the TP-Link Deco integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TpLinkDecoSnapshot
from .api.errors import (
    TpLinkDecoApiClientAuthenticationError,
    TpLinkDecoApiClientError,
)

if TYPE_CHECKING:
    from .data import TpLinkDecoConfigEntry


class TpLinkDecoDataUpdateCoordinator(DataUpdateCoordinator[TpLinkDecoSnapshot]):
    """Fetches data in a single session to avoid concurrent auth conflicts."""

    config_entry: TpLinkDecoConfigEntry

    async def _async_update_data(self) -> TpLinkDecoSnapshot:
        try:
            return await self.hass.async_add_executor_job(
                self.config_entry.runtime_data.client.get_snapshot
            )
        except TpLinkDecoApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except TpLinkDecoApiClientError as exception:
            raise UpdateFailed(exception) from exception
