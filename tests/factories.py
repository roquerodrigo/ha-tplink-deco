"""Factories for building SDK dataclasses used in tests."""

from __future__ import annotations

from typing import Any

from tplink_deco_api import ClientDevice, Device, Performance
from tplink_deco_api.models.signal_level import SignalLevel


def make_client(
    mac: str = "AA:BB:CC:DD:EE:01",
    ip: str = "192.168.0.10",
    name: str = "Phone",
    **overrides: Any,
) -> ClientDevice:
    """Build a ClientDevice with sensible defaults."""
    fields: dict[str, Any] = {
        "mac": mac,
        "ip": ip,
        "name": name,
        "up_speed": 100,
        "down_speed": 200,
        "wire_type": "wireless",
        "connection_type": "band5",
        "space_id": "",
        "access_host": "",
        "interface": "main",
        "client_type": "",
        "owner_id": "",
        "remain_time": 0,
        "online": True,
        "client_mesh": False,
        "enable_priority": False,
    }
    fields.update(overrides)
    return ClientDevice(**fields)


def make_node(
    mac: str = "11:22:33:44:55:66",
    role: str = "master",
    **overrides: Any,
) -> Device:
    """Build a Device (Deco node) with sensible defaults."""
    fields: dict[str, Any] = {
        "mac": mac,
        "device_ip": "192.168.0.1",
        "device_model": "X20",
        "device_type": "home",
        "role": role,
        "nickname": "Living Room",
        "custom_nickname": "",
        "hardware_ver": "1.0",
        "software_ver": "1.5.10",
        "oem_id": "",
        "hw_id": "",
        "bssid_2g": "11:22:33:44:55:67",
        "bssid_5g": "11:22:33:44:55:68",
        "bssid_sta_2g": "",
        "bssid_sta_5g": "",
        "inet_status": "online",
        "inet_error_msg": "",
        "group_status": "",
        "signal_level": SignalLevel(band2_4="4", band5="5", band6="0"),
        "product_level": 1,
        "set_gateway_support": True,
        "support_plc": False,
        "oversized_firmware": False,
        "nand_flash": False,
    }
    fields.update(overrides)
    return Device(**fields)


def make_performance(cpu: float = 0.42, memory: float = 0.65) -> Performance:
    """Build a Performance instance."""
    return Performance(cpu_usage=cpu, mem_usage=memory)
