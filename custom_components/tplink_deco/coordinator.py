"""DataUpdateCoordinator for the TP-Link Deco integration."""

from __future__ import annotations

import dataclasses
import time
from typing import TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TpLinkDecoSnapshot
from .api.errors import (
    TpLinkDecoApiClientAuthenticationError,
    TpLinkDecoApiClientError,
)
from .const import LOGGER, SPEED_EMA_ALPHA, UNAVAILABLE_GRACE_PERIOD_SECONDS

if TYPE_CHECKING:
    from tplink_deco_api import ClientDevice, Device

    from .data import TpLinkDecoConfigEntry


class TpLinkDecoDataUpdateCoordinator(DataUpdateCoordinator[TpLinkDecoSnapshot]):
    """Fetches data in a single session to avoid concurrent auth conflicts."""

    config_entry: TpLinkDecoConfigEntry

    async def _async_update_data(self) -> TpLinkDecoSnapshot:
        try:
            snapshot = await self.hass.async_add_executor_job(
                self.config_entry.runtime_data.client.get_snapshot
            )
        except TpLinkDecoApiClientAuthenticationError as exception:
            LOGGER.warning("Authentication failed: %s", exception)
            raise ConfigEntryAuthFailed(exception) from exception
        except TpLinkDecoApiClientError as exception:
            LOGGER.error("Failed to fetch snapshot: %s", exception)
            raise UpdateFailed(exception) from exception
        LOGGER.debug(
            "Snapshot fetched: %d clients, %d nodes, performance=%s",
            len(snapshot.clients),
            len(snapshot.nodes),
            "ok" if snapshot.performance else "missing",
        )
        return self._apply_grace(snapshot)

    def _apply_grace(self, snapshot: TpLinkDecoSnapshot) -> TpLinkDecoSnapshot:
        """
        Re-include clients/nodes still within the grace period.

        Caches the latest sighting of each client and node by MAC. When the
        next snapshot arrives missing some entries, this re-injects them
        (using their last-known state) for up to UNAVAILABLE_GRACE_PERIOD_SECONDS,
        so transient drops (e.g., mobile WiFi sleep) don't propagate as
        immediate state changes to dependent sensors.
        """
        client_grace = self.__dict__.setdefault("_client_grace", {})
        node_grace = self.__dict__.setdefault("_node_grace", {})

        now = time.monotonic()
        cutoff = now - UNAVAILABLE_GRACE_PERIOD_SECONDS

        for client in snapshot.clients:
            client_grace[client.mac] = (client, now)
        for node in snapshot.nodes:
            node_grace[node.mac] = (node, now)

        seen_clients = {c.mac for c in snapshot.clients}
        graced_clients: list[ClientDevice] = list(snapshot.clients)
        for mac in list(client_grace):
            cached, ts = client_grace[mac]
            if ts < cutoff:
                del client_grace[mac]
            elif mac not in seen_clients:
                graced_clients.append(cached)

        seen_nodes = {n.mac for n in snapshot.nodes}
        graced_nodes: list[Device] = list(snapshot.nodes)
        for mac in list(node_grace):
            cached, ts = node_grace[mac]
            if ts < cutoff:
                del node_grace[mac]
            elif mac not in seen_nodes:
                graced_nodes.append(cached)

        return TpLinkDecoSnapshot(
            clients=self._smooth_speeds(graced_clients),
            nodes=graced_nodes,
            performance=snapshot.performance,
        )

    def _smooth_speeds(
        self, clients: list[ClientDevice]
    ) -> list[ClientDevice]:
        """Apply exponential moving average to client speed values."""
        ema: dict[str, tuple[float, float]] = self.__dict__.setdefault(
            "_speed_ema", {}
        )
        alpha = SPEED_EMA_ALPHA
        result: list[ClientDevice] = []
        for client in clients:
            prev = ema.get(client.mac)
            if prev is None:
                smoothed_down = float(client.down_speed)
                smoothed_up = float(client.up_speed)
            else:
                smoothed_down = (
                    alpha * client.down_speed + (1 - alpha) * prev[0]
                )
                smoothed_up = (
                    alpha * client.up_speed + (1 - alpha) * prev[1]
                )
            ema[client.mac] = (smoothed_down, smoothed_up)
            result.append(
                dataclasses.replace(
                    client,
                    down_speed=round(smoothed_down),
                    up_speed=round(smoothed_up),
                )
            )
        return result
