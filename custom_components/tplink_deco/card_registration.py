"""Registration of the bundled Lovelace card with the frontend."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, TypedDict, cast

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace import LOVELACE_DATA
from homeassistant.components.lovelace.resources import ResourceStorageCollection

from .const import DOMAIN, STATIC_URL_PREFIX

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_STATIC_PATH_REGISTERED_KEY = f"{DOMAIN}_static_path_registered"
_EXTRA_MODULE_REGISTERED_KEY = f"{DOMAIN}_extra_module_registered"
_CARD_URL = f"{STATIC_URL_PREFIX}/tplink-deco-card.js"
_WWW_DIR = Path(__file__).parent / "www"


class TpLinkDecoDashboardResource(TypedDict):
    """Dashboard resource entry as stored by the Lovelace resource collection."""

    id: str
    url: str


class TpLinkDecoCardRegistration:
    """
    Serve the bundled card and keep it registered on dashboards.

    The card is registered as a Lovelace dashboard resource instead of an
    extra frontend module: extra modules are embedded in index.html only for
    pages served after this integration has started setting up, so a
    dashboard opened while Home Assistant was still starting rendered a
    configuration error until a manual reload. Dashboard resources persist
    in storage and are fetched on every dashboard load, which closes that
    startup window. add_extra_js_url() remains only as the fallback for
    YAML-mode resources, which cannot be managed programmatically.
    """

    def __init__(self, hass: HomeAssistant, version: str) -> None:
        """Initialize the registration for one card version."""
        self._hass = hass
        self._versioned_url = f"{_CARD_URL}?v={version}"

    async def async_register(self) -> None:
        """Serve the card files and ensure dashboards can load them."""
        await self._async_register_static_path()
        if (resources := self._storage_resources()) is None:
            self._register_extra_module()
        else:
            await self._async_ensure_resource(resources)

    async def async_remove(self) -> None:
        """Drop the dashboard resource of the card."""
        if (resources := self._storage_resources()) is None:
            return
        if not resources.loaded:
            await resources.async_load()
        for item in _resource_items(resources):
            if item["url"].startswith(_CARD_URL):
                await resources.async_delete_item(item["id"])

    async def _async_register_static_path(self) -> None:
        if self._hass.data.get(_STATIC_PATH_REGISTERED_KEY):
            return
        await self._hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL_PREFIX, str(_WWW_DIR), cache_headers=True)]
        )
        self._hass.data[_STATIC_PATH_REGISTERED_KEY] = True

    def _register_extra_module(self) -> None:
        if self._hass.data.get(_EXTRA_MODULE_REGISTERED_KEY):
            return
        add_extra_js_url(self._hass, self._versioned_url)
        self._hass.data[_EXTRA_MODULE_REGISTERED_KEY] = True

    def _storage_resources(self) -> ResourceStorageCollection | None:
        if (lovelace := self._hass.data.get(LOVELACE_DATA)) is None:
            return None
        resources = lovelace.resources
        if not isinstance(resources, ResourceStorageCollection):
            return None
        return resources

    async def _async_ensure_resource(
        self, resources: ResourceStorageCollection
    ) -> None:
        if not resources.loaded:
            await resources.async_load()
        for item in _resource_items(resources):
            if not item["url"].startswith(_CARD_URL):
                continue
            if item["url"] != self._versioned_url:
                await resources.async_update_item(
                    item["id"], {"url": self._versioned_url}
                )
            return
        await resources.async_create_item(
            {"res_type": "module", "url": self._versioned_url}
        )


def _resource_items(
    resources: ResourceStorageCollection,
) -> list[TpLinkDecoDashboardResource]:
    return [
        cast("TpLinkDecoDashboardResource", item) for item in resources.async_items()
    ]
