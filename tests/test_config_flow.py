"""Tests for the TP-Link Deco config flow."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.tplink_deco.api.errors import (
    TpLinkDecoApiClientAuthenticationError,
    TpLinkDecoApiClientCommunicationError,
    TpLinkDecoApiClientError,
)
from custom_components.tplink_deco.const import CONF_LINK_DEVICES_BY_MAC, DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

USER_INPUT = {
    CONF_HOST: "192.168.0.1",
    CONF_USERNAME: "admin",
    CONF_PASSWORD: "secret",
    CONF_LINK_DEVICES_BY_MAC: True,
}


async def _start_flow(hass: HomeAssistant) -> dict:
    """Start the user flow and return the form result."""
    return await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )


async def test_form_shown(hass: HomeAssistant) -> None:
    """Initial flow shows the user form."""
    result = await _start_flow(hass)
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_create_entry_on_valid_credentials(hass: HomeAssistant) -> None:
    """Submitting valid credentials creates an entry."""
    result = await _start_flow(hass)
    with patch(
        "custom_components.tplink_deco.config_flow.TpLinkDecoApiClient.get_snapshot",
        return_value=None,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == USER_INPUT[CONF_HOST]
    assert result["data"] == USER_INPUT


async def test_create_entry_with_link_devices_disabled(hass: HomeAssistant) -> None:
    """The link_devices_by_mac toggle is persisted when disabled at setup."""
    result = await _start_flow(hass)
    user_input = {**USER_INPUT, CONF_LINK_DEVICES_BY_MAC: False}
    with patch(
        "custom_components.tplink_deco.config_flow.TpLinkDecoApiClient.get_snapshot",
        return_value=None,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input
        )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_LINK_DEVICES_BY_MAC] is False


async def test_auth_error_shows_form_with_error(hass: HomeAssistant) -> None:
    """Auth errors return the form with an auth error message."""
    result = await _start_flow(hass)
    with patch(
        "custom_components.tplink_deco.config_flow.TpLinkDecoApiClient.get_snapshot",
        side_effect=TpLinkDecoApiClientAuthenticationError("bad creds"),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "auth"}


async def test_communication_error_shows_form_with_error(hass: HomeAssistant) -> None:
    """Communication errors return the form with a connection error message."""
    result = await _start_flow(hass)
    with patch(
        "custom_components.tplink_deco.config_flow.TpLinkDecoApiClient.get_snapshot",
        side_effect=TpLinkDecoApiClientCommunicationError("offline"),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )
    assert result["errors"] == {"base": "connection"}


async def test_unknown_error_shows_form_with_error(hass: HomeAssistant) -> None:
    """Generic errors return the form with an unknown error message."""
    result = await _start_flow(hass)
    with patch(
        "custom_components.tplink_deco.config_flow.TpLinkDecoApiClient.get_snapshot",
        side_effect=TpLinkDecoApiClientError("oops"),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )
    assert result["errors"] == {"base": "unknown"}


def _existing_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Add a configured entry to hass and return it."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={**USER_INPUT, CONF_LINK_DEVICES_BY_MAC: True},
        unique_id=USER_INPUT[CONF_HOST],
    )
    entry.add_to_hass(hass)
    return entry


async def test_reconfigure_updates_link_devices_by_mac(hass: HomeAssistant) -> None:
    """Reconfigure flow persists the toggle change without recreating the entry."""
    entry = _existing_entry(hass)
    result = await entry.start_reconfigure_flow(hass)
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    updated = {**USER_INPUT, CONF_LINK_DEVICES_BY_MAC: False}
    with patch(
        "custom_components.tplink_deco.config_flow.TpLinkDecoApiClient.get_snapshot",
        return_value=None,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], updated
        )
    assert result["type"] == data_entry_flow.FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_LINK_DEVICES_BY_MAC] is False


async def test_reconfigure_surfaces_credential_errors(hass: HomeAssistant) -> None:
    """Reconfigure flow keeps the form and reports validation errors."""
    entry = _existing_entry(hass)
    result = await entry.start_reconfigure_flow(hass)

    with patch(
        "custom_components.tplink_deco.config_flow.TpLinkDecoApiClient.get_snapshot",
        side_effect=TpLinkDecoApiClientAuthenticationError("bad creds"),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "auth"}
