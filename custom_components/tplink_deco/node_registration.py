"""Registration of the Deco mesh nodes in the device registry."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers import device_registry as dr

from .const import CONF_LINK_DEVICES_BY_MAC, DEFAULT_LINK_DEVICES_BY_MAC
from .device import build_deco_device_info

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from tplink_deco_api import Device

    from .data import TpLinkDecoConfigEntry


class TpLinkDecoNodeRegistration:
    """
    Create the device entry of every mesh node up front.

    Client devices name their node through ``via_device``, and Home Assistant
    drops that link when the referenced device does not exist yet. Platforms
    add their entities concurrently, so no ordering between them guarantees
    the nodes come first; registering them before the platforms are forwarded
    does.
    """

    def __init__(self, hass: HomeAssistant, entry: TpLinkDecoConfigEntry) -> None:
        """Initialize the registration for one config entry."""
        self._hass = hass
        self._entry = entry

    def register(self, nodes: list[Device]) -> None:
        """Ensure every node of the mesh has a device entry."""
        registry = dr.async_get(self._hass)
        link_devices_by_mac = self._entry.data.get(
            CONF_LINK_DEVICES_BY_MAC,
            DEFAULT_LINK_DEVICES_BY_MAC,
        )
        for node in nodes:
            registry.async_get_or_create(
                config_entry_id=self._entry.entry_id,
                **build_deco_device_info(
                    node,
                    node.mac,
                    link_devices_by_mac=link_devices_by_mac,
                ),
            )
