"""Constants for the TP-Link Deco integration."""

from __future__ import annotations

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "tplink_deco"
ATTRIBUTION = "Data provided by TP-Link Deco"
MANUFACTURER = "TP-Link"
STATIC_URL_PREFIX = "/tplink_deco"

CONF_LINK_DEVICES_BY_MAC = "link_devices_by_mac"
DEFAULT_LINK_DEVICES_BY_MAC = True

DEFAULT_SCAN_INTERVAL_SECONDS = 20
MIN_SCAN_INTERVAL_SECONDS = 10
MAX_SCAN_INTERVAL_SECONDS = 600

DEFAULT_TIMEOUT_SECONDS = 30
MIN_TIMEOUT_SECONDS = 5
MAX_TIMEOUT_SECONDS = 120

UNAVAILABLE_GRACE_PERIOD_SECONDS = 600

SPEED_EMA_ALPHA = 0.4
