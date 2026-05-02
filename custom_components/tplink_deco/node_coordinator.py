"""DataUpdateCoordinator for TP-Link Deco nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from tplink_deco_api import Device

from .api.errors import (
    TpLinkDecoApiClientAuthenticationError,
    TpLinkDecoApiClientError,
)

if TYPE_CHECKING:
    from .data import TpLinkDecoConfigEntry


class TpLinkDecoNodeCoordinator(DataUpdateCoordinator[list[Device]]):
    """Class to manage fetching Deco node data from the router."""

    config_entry: TpLinkDecoConfigEntry

    async def _async_update_data(self) -> list[Device]:
        """Fetch node list from the router."""
        try:
            return await self.hass.async_add_executor_job(
                self.config_entry.runtime_data.client.get_devices
            )
        except TpLinkDecoApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except TpLinkDecoApiClientError as exception:
            raise UpdateFailed(exception) from exception
