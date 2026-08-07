"""Config flow for TP-Link Deco."""

from __future__ import annotations

from typing import NotRequired, TypedDict, cast

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import selector

from .api import TpLinkDecoApiClient
from .api.errors import (
    TpLinkDecoApiClientAuthenticationError,
    TpLinkDecoApiClientCommunicationError,
    TpLinkDecoApiClientError,
)
from .const import (
    CONF_LINK_DEVICES_BY_MAC,
    DEFAULT_LINK_DEVICES_BY_MAC,
    DOMAIN,
    LOGGER,
)


class TpLinkDecoUserInput(TypedDict):
    """
    Shape of the user-submitted config flow payload.

    ``link_devices_by_mac`` is ``NotRequired`` to keep older config entries
    (created before the option existed) loadable via the reconfigure step.
    """

    host: str
    username: str
    password: str
    link_devices_by_mac: NotRequired[bool]


class TpLinkDecoFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for TP-Link Deco."""

    VERSION = 1

    async def async_step_user(  # type: ignore[override]
        self,
        user_input: TpLinkDecoUserInput | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle the initial configuration step.

        Narrows HA's ``dict[str, Any] | None`` signature to a TypedDict; the
        override is safe because the form schema only accepts these keys.
        """
        _errors: dict[str, str] = {}
        if user_input is not None:
            _errors = await self._validate(user_input)
            if not _errors:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_HOST],
                    data=dict(user_input),
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self._build_schema(user_input),
            errors=_errors,
        )

    async def async_step_reauth(
        self,
        entry_data: TpLinkDecoUserInput,  # noqa: ARG002 -- HA reauth contract requires this parameter
    ) -> config_entries.ConfigFlowResult:
        """Start reauthentication after the router rejected the credentials."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: TpLinkDecoUserInput | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Revalidate the credentials and update the existing entry."""
        entry = self._get_reauth_entry()
        _errors: dict[str, str] = {}
        if user_input is not None:
            _errors = await self._validate(user_input)
            if not _errors:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_mismatch()
                return self.async_update_reload_and_abort(
                    entry,
                    data=dict(user_input),
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=self._build_schema(
                user_input or cast("TpLinkDecoUserInput", dict(entry.data)),
            ),
            errors=_errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: TpLinkDecoUserInput | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle reconfiguration of an existing entry."""
        entry = self._get_reconfigure_entry()
        _errors: dict[str, str] = {}
        if user_input is not None:
            _errors = await self._validate(user_input)
            if not _errors:
                return self.async_update_reload_and_abort(
                    entry,
                    data=dict(user_input),
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self._build_schema(
                user_input or cast("TpLinkDecoUserInput", dict(entry.data)),
            ),
            errors=_errors,
        )

    async def _validate(self, user_input: TpLinkDecoUserInput) -> dict[str, str]:
        """Validate credentials and return any flow errors."""
        try:
            await self.hass.async_add_executor_job(
                self._test_credentials,
                user_input[CONF_HOST],
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
            )
        except TpLinkDecoApiClientAuthenticationError as exception:
            LOGGER.warning("Failed to authenticate with the router: %s", exception)
            return {"base": "auth"}
        except TpLinkDecoApiClientCommunicationError as exception:
            LOGGER.error("Failed to connect to the router: %s", exception)
            return {"base": "connection"}
        except TpLinkDecoApiClientError:
            LOGGER.exception("Failed to validate the router credentials")
            return {"base": "unknown"}
        return {}

    @staticmethod
    def _build_schema(defaults: TpLinkDecoUserInput | None) -> vol.Schema:
        """Build the credentials + options schema, prefilled with defaults."""
        prefill: TpLinkDecoUserInput = defaults or TpLinkDecoUserInput(
            host="192.168.0.1",
            username="admin",
            password="",
        )
        return vol.Schema(
            {
                vol.Required(
                    CONF_HOST,
                    default=prefill.get(CONF_HOST, "192.168.0.1"),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                    ),
                ),
                vol.Required(
                    CONF_USERNAME,
                    default=prefill.get(CONF_USERNAME, "admin"),
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
                vol.Required(
                    CONF_LINK_DEVICES_BY_MAC,
                    default=prefill.get(
                        CONF_LINK_DEVICES_BY_MAC,
                        DEFAULT_LINK_DEVICES_BY_MAC,
                    ),
                ): selector.BooleanSelector(),
            }
        )

    def _test_credentials(self, host: str, username: str, password: str) -> None:
        """Validate credentials by connecting to the router (runs in executor)."""
        client = TpLinkDecoApiClient(host=host, username=username, password=password)
        client.get_snapshot()
