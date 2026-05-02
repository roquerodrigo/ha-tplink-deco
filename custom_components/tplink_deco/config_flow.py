"""Config flow for TP-Link Deco."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import selector

from .api import (
    TpLinkDecoApiClient,
    TpLinkDecoApiClientAuthenticationError,
    TpLinkDecoApiClientCommunicationError,
    TpLinkDecoApiClientError,
)
from .const import DOMAIN, LOGGER


class TpLinkDecoFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for TP-Link Deco."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial configuration step."""
        _errors = {}
        if user_input is not None:
            try:
                await self.hass.async_add_executor_job(
                    self._test_credentials,
                    user_input[CONF_HOST],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                )
            except TpLinkDecoApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except TpLinkDecoApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except TpLinkDecoApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_HOST],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=(user_input or {}).get(CONF_HOST, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                }
            ),
            errors=_errors,
        )

    def _test_credentials(self, host: str, username: str, password: str) -> None:
        """Validate credentials by connecting to the router (runs in executor)."""
        client = TpLinkDecoApiClient(host=host, username=username, password=password)
        client.get_clients()
