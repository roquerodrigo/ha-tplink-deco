"""Tests for client and Deco sensor entities."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.const import EntityCategory

from custom_components.tplink_deco.api import TpLinkDecoSnapshot
from custom_components.tplink_deco.sensor.client_connection_type import (
    TpLinkDecoClientConnectionTypeSensor,
)
from custom_components.tplink_deco.sensor.client_download import (
    TpLinkDecoClientDownloadSensor,
)
from custom_components.tplink_deco.sensor.client_interface import (
    TpLinkDecoClientInterfaceSensor,
)
from custom_components.tplink_deco.sensor.client_ip import TpLinkDecoClientIpSensor
from custom_components.tplink_deco.sensor.client_mac import TpLinkDecoClientMacSensor
from custom_components.tplink_deco.sensor.client_upload import (
    TpLinkDecoClientUploadSensor,
)
from custom_components.tplink_deco.sensor.deco_clients import (
    TpLinkDecoDecoClientsSensor,
)
from custom_components.tplink_deco.sensor.deco_cpu import TpLinkDecoDecoCpuSensor
from custom_components.tplink_deco.sensor.deco_download import (
    TpLinkDecoDecoDownloadSensor,
)
from custom_components.tplink_deco.sensor.deco_ip import TpLinkDecoDecoIpSensor
from custom_components.tplink_deco.sensor.deco_mac import TpLinkDecoDecoMacSensor
from custom_components.tplink_deco.sensor.deco_memory import TpLinkDecoDecoMemorySensor
from custom_components.tplink_deco.sensor.deco_upload import (
    TpLinkDecoDecoUploadSensor,
)

from .factories import make_client, make_node, make_performance


def _coord(snapshot: TpLinkDecoSnapshot) -> MagicMock:
    mock = MagicMock()
    mock.data = snapshot
    mock.last_update_success = True
    return mock


def test_client_mac_sensor() -> None:
    """MAC sensor returns the client MAC and a unique id derived from it."""
    client = make_client(mac="AA:BB:CC:DD:EE:01")
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    sensor = TpLinkDecoClientMacSensor(_coord(snapshot), client)
    assert sensor.native_value == "AA:BB:CC:DD:EE:01"
    assert sensor.unique_id == "AA:BB:CC:DD:EE:01_mac"


def test_client_ip_sensor() -> None:
    """IP sensor returns the client IP."""
    client = make_client(mac="AA:BB:CC:DD:EE:02", ip="10.0.0.5")
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    sensor = TpLinkDecoClientIpSensor(_coord(snapshot), client)
    assert sensor.native_value == "10.0.0.5"
    assert sensor.unique_id == "AA:BB:CC:DD:EE:02_ip"


def test_client_download_sensor() -> None:
    """Download sensor returns the down_speed value."""
    client = make_client(mac="AA:BB:CC:DD:EE:03", down_speed=1500)
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    sensor = TpLinkDecoClientDownloadSensor(_coord(snapshot), client)
    assert sensor.native_value == 1500
    assert sensor.unique_id == "AA:BB:CC:DD:EE:03_download"


def test_client_upload_sensor() -> None:
    """Upload sensor returns the up_speed value."""
    client = make_client(mac="AA:BB:CC:DD:EE:04", up_speed=750)
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    sensor = TpLinkDecoClientUploadSensor(_coord(snapshot), client)
    assert sensor.native_value == 750
    assert sensor.unique_id == "AA:BB:CC:DD:EE:04_upload"


def test_client_connection_type_sensor() -> None:
    """Connection type sensor returns the connection_type field."""
    client = make_client(mac="AA:BB:CC:DD:EE:05", connection_type="band6")
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    sensor = TpLinkDecoClientConnectionTypeSensor(_coord(snapshot), client)
    assert sensor.native_value == "band6"
    assert sensor.unique_id == "AA:BB:CC:DD:EE:05_connection_type"


def test_client_connection_type_sensor_returns_none_for_unknown_value() -> None:
    """Values outside the ENUM options map to None to avoid HA ValueError."""
    client = make_client(mac="AA:BB:CC:DD:EE:0A", connection_type="unknown")
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    sensor = TpLinkDecoClientConnectionTypeSensor(_coord(snapshot), client)
    assert sensor.native_value is None


def test_client_interface_sensor() -> None:
    """Interface sensor returns the interface field."""
    client = make_client(mac="AA:BB:CC:DD:EE:06", interface="iot")
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    sensor = TpLinkDecoClientInterfaceSensor(_coord(snapshot), client)
    assert sensor.native_value == "iot"
    assert sensor.unique_id == "AA:BB:CC:DD:EE:06_interface"


def test_client_interface_sensor_returns_none_for_unknown_value() -> None:
    """Values outside the ENUM options map to None to avoid HA ValueError."""
    client = make_client(mac="AA:BB:CC:DD:EE:0B", interface="unknown")
    snapshot = TpLinkDecoSnapshot(clients=[client], nodes=[], performance=None)
    sensor = TpLinkDecoClientInterfaceSensor(_coord(snapshot), client)
    assert sensor.native_value is None


def test_client_sensor_value_is_none_when_offline() -> None:
    """Sensors return None once the client disappears from the snapshot."""
    client = make_client()
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[], performance=None)
    sensor = TpLinkDecoClientMacSensor(_coord(snapshot), client)
    assert sensor.native_value is None


def test_deco_mac_sensor() -> None:
    """Deco MAC sensor returns the node MAC."""
    node = make_node(mac="DE:CO:00:00:00:01")
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None)
    sensor = TpLinkDecoDecoMacSensor(_coord(snapshot), node)
    assert sensor.native_value == "DE:CO:00:00:00:01"
    assert sensor.unique_id == "DE:CO:00:00:00:01_mac"


def test_deco_ip_sensor() -> None:
    """Deco IP sensor returns the node device_ip."""
    node = make_node(mac="DE:CO:00:00:00:02")
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None)
    sensor = TpLinkDecoDecoIpSensor(_coord(snapshot), node)
    assert sensor.native_value == node.device_ip
    assert sensor.unique_id == "DE:CO:00:00:00:02_ip"


def test_deco_cpu_sensor_scales_to_percentage() -> None:
    """CPU sensor multiplies the raw fraction by 100."""
    node = make_node(mac="DE:CO:00:00:00:03")
    snapshot = TpLinkDecoSnapshot(
        clients=[], nodes=[node], performance=make_performance(cpu=0.42, memory=0.5)
    )
    sensor = TpLinkDecoDecoCpuSensor(_coord(snapshot), node)
    assert sensor.native_value == 42.0
    assert sensor.unique_id == "DE:CO:00:00:00:03_cpu_usage"


def test_deco_memory_sensor_scales_to_percentage() -> None:
    """Memory sensor multiplies the raw fraction by 100."""
    node = make_node(mac="DE:CO:00:00:00:04")
    snapshot = TpLinkDecoSnapshot(
        clients=[], nodes=[node], performance=make_performance(cpu=0.1, memory=0.65)
    )
    sensor = TpLinkDecoDecoMemorySensor(_coord(snapshot), node)
    assert sensor.native_value == 65.0
    assert sensor.unique_id == "DE:CO:00:00:00:04_mem_usage"


def test_deco_cpu_returns_none_without_performance() -> None:
    """Performance sensors return None when performance data is missing."""
    node = make_node()
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None)
    sensor = TpLinkDecoDecoCpuSensor(_coord(snapshot), node)
    assert sensor.native_value is None


def test_deco_clients_counter_returns_count() -> None:
    """The clients counter returns the number of online clients."""
    node = make_node(mac="DE:CO:00:00:00:05")
    clients = [
        make_client(mac="AA:00:00:00:00:01"),
        make_client(mac="AA:00:00:00:00:02"),
        make_client(mac="AA:00:00:00:00:03"),
    ]
    snapshot = TpLinkDecoSnapshot(clients=clients, nodes=[node], performance=None)
    sensor = TpLinkDecoDecoClientsSensor(_coord(snapshot), node)
    assert sensor.native_value == 3
    assert sensor.unique_id == "DE:CO:00:00:00:05_clients_online"


def test_deco_total_download_sensor_sums_clients() -> None:
    """Total download sensor sums down_speed across all clients."""
    node = make_node(mac="DE:CO:00:00:00:06")
    clients = [
        make_client(mac="AA:00:00:00:00:01", down_speed=100),
        make_client(mac="AA:00:00:00:00:02", down_speed=250),
        make_client(mac="AA:00:00:00:00:03", down_speed=50),
    ]
    snapshot = TpLinkDecoSnapshot(clients=clients, nodes=[node], performance=None)
    sensor = TpLinkDecoDecoDownloadSensor(_coord(snapshot), node)
    assert sensor.native_value == 400
    assert sensor.unique_id == "DE:CO:00:00:00:06_total_download"


def test_deco_total_upload_sensor_sums_clients() -> None:
    """Total upload sensor sums up_speed across all clients."""
    node = make_node(mac="DE:CO:00:00:00:07")
    clients = [
        make_client(mac="AA:00:00:00:00:01", up_speed=80),
        make_client(mac="AA:00:00:00:00:02", up_speed=120),
    ]
    snapshot = TpLinkDecoSnapshot(clients=clients, nodes=[node], performance=None)
    sensor = TpLinkDecoDecoUploadSensor(_coord(snapshot), node)
    assert sensor.native_value == 200
    assert sensor.unique_id == "DE:CO:00:00:00:07_total_upload"


def test_deco_total_download_returns_zero_for_no_clients() -> None:
    """Totals are zero when no clients are connected."""
    node = make_node(mac="DE:CO:00:00:00:08")
    snapshot = TpLinkDecoSnapshot(clients=[], nodes=[node], performance=None)
    sensor = TpLinkDecoDecoDownloadSensor(_coord(snapshot), node)
    assert sensor.native_value == 0


def test_address_sensors_are_diagnostic() -> None:
    """MAC and IP sensors are categorized as diagnostic entities."""
    assert TpLinkDecoClientMacSensor.entity_description.entity_category == (
        EntityCategory.DIAGNOSTIC
    )
    assert TpLinkDecoClientIpSensor.entity_description.entity_category == (
        EntityCategory.DIAGNOSTIC
    )
    assert TpLinkDecoDecoMacSensor.entity_description.entity_category == (
        EntityCategory.DIAGNOSTIC
    )
    assert TpLinkDecoDecoIpSensor.entity_description.entity_category == (
        EntityCategory.DIAGNOSTIC
    )
