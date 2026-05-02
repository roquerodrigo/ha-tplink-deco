"""Tests for the TpLinkDecoSnapshot dataclass."""

from __future__ import annotations

from custom_components.tplink_deco.api import TpLinkDecoSnapshot

from .factories import make_client, make_node, make_performance


def test_snapshot_holds_all_data() -> None:
    """Snapshot should expose clients, nodes and performance."""
    client = make_client()
    node = make_node()
    perf = make_performance()
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[node], performance=perf)
    assert snapshot.clients == [client]
    assert snapshot.nodes == [node]
    assert snapshot.performance is perf


def test_snapshot_allows_missing_performance() -> None:
    """Performance is optional in the snapshot."""
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[], performance=None)
    assert snapshot.performance is None
