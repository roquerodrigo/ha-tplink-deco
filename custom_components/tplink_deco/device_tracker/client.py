"""Device tracker for a TP-Link Deco client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.device_tracker import ScannerEntity, SourceType

from custom_components.tplink_deco.device import TpLinkDecoClientDevice

if TYPE_CHECKING:
    from homeassistant.helpers.device_registry import DeviceInfo


class TpLinkDecoClientTracker(TpLinkDecoClientDevice, ScannerEntity):
    """Device tracker for a client connected to the TP-Link Deco network."""

    _attr_name = None

    @property
    def source_type(self) -> SourceType:
        """Return the device tracker source type."""
        return SourceType.ROUTER

    @property
    def unique_id(self) -> str:
        """Return the unique entity ID."""
        return f"{self._client_mac}_tracker"

    @property
    def available(self) -> bool:
        """Return True as long as the coordinator is working, even when offline."""
        return self.coordinator.last_update_success

    @property
    def is_connected(self) -> bool:
        """Return whether the client is connected to the network."""
        return self.client is not None

    @property
    def ip_address(self) -> str | None:
        """Return the client IP address."""
        client = self.client
        return client.ip if client else None

    @property
    def mac_address(self) -> str:
        """Return the client MAC address."""
        return self._client_mac

    @property  # type: ignore[misc]
    def device_info(self) -> DeviceInfo | None:
        """
        Return the parent's identifier-based device info.

        Override of ScannerEntity's @final device_info — intentional to keep
        the tracker entity attached to the same client device created by the
        sensor/binary_sensor entities, instead of ScannerEntity's default
        MAC-based device matching.
        """
        prop = TpLinkDecoClientDevice.__dict__["device_info"]
        return prop.fget(self)
