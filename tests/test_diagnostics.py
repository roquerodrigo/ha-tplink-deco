"""Tests for the TP-Link Deco diagnostics platform."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.components.diagnostics import REDACTED
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME

from custom_components.tplink_deco.diagnostics import (
    TO_REDACT,
    async_get_config_entry_diagnostics,
)


async def test_password_is_redacted() -> None:
    """The diagnostics payload redacts the password but keeps host/username."""
    entry = MagicMock()
    entry.data = {
        CONF_HOST: "192.168.0.1",
        CONF_USERNAME: "admin",
        CONF_PASSWORD: "supersecret",
    }
    entry.options = {}

    result = await async_get_config_entry_diagnostics(MagicMock(), entry)

    assert result["entry"]["data"][CONF_HOST] == "192.168.0.1"
    assert result["entry"]["data"][CONF_USERNAME] == "admin"
    assert result["entry"]["data"][CONF_PASSWORD] == REDACTED
    assert result["entry"]["options"] == {}


def test_to_redact_only_targets_password() -> None:
    """TO_REDACT is a frozenset and limited to the password key."""
    assert isinstance(TO_REDACT, frozenset)
    assert frozenset({CONF_PASSWORD}) == TO_REDACT
