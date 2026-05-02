"""DataUpdateCoordinator for tplink_deco."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from tplink_deco_api import ClientDevice

from .api.errors import (
    TpLinkDecoApiClientAuthenticationError,
    TpLinkDecoApiClientError,
)

if TYPE_CHECKING:
    from .data import TpLinkDecoConfigEntry


class TpLinkDecoDataUpdateCoordinator(DataUpdateCoordinator[list[ClientDevice]]):
    """Class to manage fetching data from the TP-Link Deco router."""

    config_entry: TpLinkDecoConfigEntry

    async def _async_update_data(self) -> list[ClientDevice]:
        """Fetch client list from the router."""
        try:
            return await self.hass.async_add_executor_job(
                self.config_entry.runtime_data.client.get_clients
            )
        except TpLinkDecoApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except TpLinkDecoApiClientError as exception:
            raise UpdateFailed(exception) from exception
