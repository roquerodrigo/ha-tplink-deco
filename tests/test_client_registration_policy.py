"""Tests for the client registration policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.tplink_deco.client_registration_policy import (
    TpLinkDecoClientRegistrationPolicy,
)
from custom_components.tplink_deco.const import DOMAIN

from .factories import make_client

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

CLIENT_MAC = "AA:BB:CC:DD:EE:01"


def _entry(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    return entry


def _register(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, CLIENT_MAC)},
    )


async def test_online_unknown_client_is_selected(hass: HomeAssistant) -> None:
    """A connected client without a device gets entities."""
    entry = _entry(hass)
    client = make_client(mac=CLIENT_MAC, online=True)

    selected = TpLinkDecoClientRegistrationPolicy(hass, entry).select_new(
        [client], set()
    )

    assert selected == [client]


async def test_offline_client_without_device_is_skipped(hass: HomeAssistant) -> None:
    """An offline client whose device was removed is not re-created."""
    entry = _entry(hass)

    selected = TpLinkDecoClientRegistrationPolicy(hass, entry).select_new(
        [make_client(mac=CLIENT_MAC, online=False)], set()
    )

    assert selected == []


async def test_offline_client_with_device_is_selected(hass: HomeAssistant) -> None:
    """An offline client that still has a device keeps its entities."""
    entry = _entry(hass)
    _register(hass, entry)
    client = make_client(mac=CLIENT_MAC, online=False)

    selected = TpLinkDecoClientRegistrationPolicy(hass, entry).select_new(
        [client], set()
    )

    assert selected == [client]


async def test_known_client_with_device_is_skipped(hass: HomeAssistant) -> None:
    """A client the platform already covers is not added twice."""
    entry = _entry(hass)
    _register(hass, entry)

    selected = TpLinkDecoClientRegistrationPolicy(hass, entry).select_new(
        [make_client(mac=CLIENT_MAC, online=True)], {CLIENT_MAC}
    )

    assert selected == []


async def test_removed_client_is_selected_on_reconnect(hass: HomeAssistant) -> None:
    """A client whose device was removed comes back once it connects again."""
    entry = _entry(hass)
    policy = TpLinkDecoClientRegistrationPolicy(hass, entry)

    offline = policy.select_new(
        [make_client(mac=CLIENT_MAC, online=False)], {CLIENT_MAC}
    )
    reconnected = make_client(mac=CLIENT_MAC, online=True)
    online = policy.select_new([reconnected], {CLIENT_MAC})

    assert offline == []
    assert online == [reconnected]


async def test_device_of_other_entry_is_ignored(hass: HomeAssistant) -> None:
    """A device registered by another entry does not count as registered."""
    entry = _entry(hass)
    _register(hass, _entry(hass))

    selected = TpLinkDecoClientRegistrationPolicy(hass, entry).select_new(
        [make_client(mac=CLIENT_MAC, online=False)], set()
    )

    assert selected == []
