"""Diagnostics for the TP-Link Deco integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, cast

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_PASSWORD

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import TpLinkDecoConfigEntry


TO_REDACT: frozenset[str] = frozenset({CONF_PASSWORD})


class TpLinkDecoEntryDiagnostics(TypedDict):
    """Redacted view of the config entry stored on disk."""

    data: dict[str, str]
    options: dict[str, str]


class TpLinkDecoDiagnostics(TypedDict):
    """Diagnostics payload returned to Home Assistant."""

    entry: TpLinkDecoEntryDiagnostics


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,  # noqa: ARG001 -- HA diagnostics platform contract requires this parameter
    entry: TpLinkDecoConfigEntry,
) -> TpLinkDecoDiagnostics:
    """Return redacted diagnostics for a config entry."""
    redacted = async_redact_data(dict(entry.data), TO_REDACT)
    return {
        "entry": {
            "data": cast("dict[str, str]", redacted),
            "options": cast("dict[str, str]", dict(entry.options)),
        },
    }
