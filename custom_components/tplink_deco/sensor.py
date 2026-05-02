"""Sensor platform for TP-Link Deco clients."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from tplink_deco_api import ClientDevice

from .entity import TpLinkDecoClientEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import TpLinkDecoDataUpdateCoordinator
    from .data import TpLinkDecoConfigEntry

_MAC_DESCRIPTION = SensorEntityDescription(
    key="mac",
    name="MAC Address",
    icon="mdi:identifier",
)

_IP_DESCRIPTION = SensorEntityDescription(
    key="ip",
    name="IP Address",
    icon="mdi:ip-network",
)

_SENSOR_DESCRIPTIONS = (_MAC_DESCRIPTION, _IP_DESCRIPTION)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: TpLinkDecoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for all connected clients."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        TpLinkDecoClientSensor(coordinator, client, description)
        for client in coordinator.data
        for description in _SENSOR_DESCRIPTIONS
    )


class TpLinkDecoClientSensor(TpLinkDecoClientEntity, SensorEntity):
    """Sensor for a TP-Link Deco client attribute."""

    def __init__(
        self,
        coordinator: TpLinkDecoDataUpdateCoordinator,
        client: ClientDevice,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, client)
        self.entity_description = entity_description
        self._attr_unique_id = f"{client.mac}_{entity_description.key}"

    @property
    def native_value(self) -> str | None:
        """Return the sensor value."""
        if self.client is None:
            return None
        if self.entity_description.key == "mac":
            return self.client.mac
        if self.entity_description.key == "ip":
            return self.client.ip
        return None
