"""Constants for the TP-Link Deco integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "tplink_deco"
ATTRIBUTION = "Data provided by TP-Link Deco"
MANUFACTURER = "TP-Link"

CONF_LINK_DEVICES_BY_MAC = "link_devices_by_mac"
DEFAULT_LINK_DEVICES_BY_MAC = True

UNAVAILABLE_GRACE_PERIOD_SECONDS = 600
