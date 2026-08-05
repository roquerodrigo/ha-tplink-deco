"""Tests for the bundled Lovelace card registration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.frontend import DATA_EXTRA_MODULE_URL, UrlManager
from homeassistant.components.lovelace import LOVELACE_DATA
from homeassistant.loader import async_get_integration
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.tplink_deco import async_remove_entry
from custom_components.tplink_deco.card_registration import TpLinkDecoCardRegistration
from custom_components.tplink_deco.const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

CARD_URL = "/tplink_deco/tplink-deco-card.js"


def _card_resource_urls(hass: HomeAssistant) -> list[str]:
    """Return the registered dashboard resource URLs of the card."""
    resources = hass.data[LOVELACE_DATA].resources
    return [
        item["url"]
        for item in resources.async_items()
        if item["url"].startswith(CARD_URL)
    ]


async def _register(hass: HomeAssistant, version: str) -> None:
    """Set up http and run the card registration."""
    assert await async_setup_component(hass, "http", {})
    await TpLinkDecoCardRegistration(hass, version).async_register()


async def test_register_creates_dashboard_resource(hass: HomeAssistant) -> None:
    """Storage mode gets a versioned dashboard resource for the card."""
    assert await async_setup_component(hass, "lovelace", {})
    await _register(hass, "1.2.3")

    assert _card_resource_urls(hass) == [f"{CARD_URL}?v=1.2.3"]


async def test_register_updates_stale_resource_version(hass: HomeAssistant) -> None:
    """An existing resource with an old version is updated in place."""
    assert await async_setup_component(hass, "lovelace", {})
    await _register(hass, "1.2.3")
    await TpLinkDecoCardRegistration(hass, "1.3.0").async_register()

    assert _card_resource_urls(hass) == [f"{CARD_URL}?v=1.3.0"]


async def test_register_twice_keeps_single_resource(hass: HomeAssistant) -> None:
    """Registering the same version twice does not duplicate the resource."""
    assert await async_setup_component(hass, "lovelace", {})
    await _register(hass, "1.2.3")
    await TpLinkDecoCardRegistration(hass, "1.2.3").async_register()

    assert _card_resource_urls(hass) == [f"{CARD_URL}?v=1.2.3"]


async def test_register_keeps_unrelated_resources(hass: HomeAssistant) -> None:
    """Resources of other cards are left untouched."""
    assert await async_setup_component(hass, "lovelace", {})
    resources = hass.data[LOVELACE_DATA].resources
    await resources.async_load()
    await resources.async_create_item(
        {"res_type": "module", "url": "/hacsfiles/other-card/other-card.js"}
    )

    await _register(hass, "1.2.3")

    urls = [item["url"] for item in resources.async_items()]
    assert "/hacsfiles/other-card/other-card.js" in urls


async def test_yaml_mode_falls_back_to_extra_module(hass: HomeAssistant) -> None:
    """YAML-mode resources fall back to add_extra_js_url."""
    hass.data.setdefault(DATA_EXTRA_MODULE_URL, UrlManager(lambda *_: None, []))
    assert await async_setup_component(hass, "lovelace", {"lovelace": {"mode": "yaml"}})

    await _register(hass, "1.2.3")
    await TpLinkDecoCardRegistration(hass, "1.2.3").async_register()

    urls = [u for u in hass.data[DATA_EXTRA_MODULE_URL].urls if u.startswith(CARD_URL)]
    assert urls == [f"{CARD_URL}?v=1.2.3"]


async def test_missing_lovelace_data_falls_back_to_extra_module(
    hass: HomeAssistant,
) -> None:
    """Without lovelace data the card is registered as an extra module."""
    hass.data.setdefault(DATA_EXTRA_MODULE_URL, UrlManager(lambda *_: None, []))

    await _register(hass, "1.2.3")

    urls = hass.data[DATA_EXTRA_MODULE_URL].urls
    assert any(u.startswith(f"{CARD_URL}?v=") for u in urls)


async def test_remove_deletes_dashboard_resource(hass: HomeAssistant) -> None:
    """Removing the registration drops the dashboard resource."""
    assert await async_setup_component(hass, "lovelace", {})
    await _register(hass, "1.2.3")

    await TpLinkDecoCardRegistration(hass, "1.2.3").async_remove()

    assert _card_resource_urls(hass) == []


async def test_remove_without_lovelace_data_is_noop(hass: HomeAssistant) -> None:
    """Removing with no lovelace data does nothing."""
    await TpLinkDecoCardRegistration(hass, "1.2.3").async_remove()


async def test_remove_loads_resources_before_deleting(hass: HomeAssistant) -> None:
    """Removing right after startup loads the resource collection first."""
    assert await async_setup_component(hass, "lovelace", {})

    await TpLinkDecoCardRegistration(hass, "1.2.3").async_remove()

    assert _card_resource_urls(hass) == []


async def test_remove_entry_drops_resource_for_last_entry(
    hass: HomeAssistant,
) -> None:
    """Removing the last config entry deletes the dashboard resource."""
    assert await async_setup_component(hass, "lovelace", {})
    await _register(hass, "1.2.3")
    await async_get_integration(hass, DOMAIN)
    entry = MockConfigEntry(domain=DOMAIN, data={})

    await async_remove_entry(hass, entry)

    assert _card_resource_urls(hass) == []


async def test_remove_entry_keeps_resource_while_entries_remain(
    hass: HomeAssistant,
) -> None:
    """The resource stays while another config entry still exists."""
    assert await async_setup_component(hass, "lovelace", {})
    await _register(hass, "1.2.3")
    remaining_entry = MockConfigEntry(domain=DOMAIN, data={})
    remaining_entry.add_to_hass(hass)
    removed_entry = MockConfigEntry(domain=DOMAIN, data={})

    await async_remove_entry(hass, removed_entry)

    assert _card_resource_urls(hass) == [f"{CARD_URL}?v=1.2.3"]
