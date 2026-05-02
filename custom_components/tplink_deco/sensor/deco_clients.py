"""Online clients counter sensor for a TP-Link Deco node."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from custom_components.tplink_deco.entity import TpLinkDecoDecoEntity


class TpLinkDecoDecoClientsSensor(TpLinkDecoDecoEntity, SensorEntity):
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
        snapshot = self.coordinator.data
        return len(snapshot.clients) if snapshot else None
