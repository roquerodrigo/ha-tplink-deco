"""Online clients counter sensor for a TP-Link Deco node."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from custom_components.tplink_deco.device import TpLinkDecoDecoDevice

if TYPE_CHECKING:
    from custom_components.tplink_deco.api import TpLinkDecoSnapshot


class TpLinkDecoDecoClientsSensor(TpLinkDecoDecoDevice, SensorEntity):
    """Sensor counting online clients on the TP-Link Deco network."""

    entity_description = SensorEntityDescription(
        key="clients_online",
        translation_key="clients_online",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:account-multiple",
    )

    @property
    def unique_id(self) -> str:
        """Return the unique entity ID."""
        return f"{self._node_mac}_clients_online"

    @property
    def native_value(self) -> int | None:
        """Return the number of online clients."""
        snapshot: TpLinkDecoSnapshot | None = self.coordinator.data
        if snapshot is None:
            return None
        return sum(1 for client in snapshot.clients if client.online)
