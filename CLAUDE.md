# ha-tplink-deco

Home Assistant custom integration for TP-Link Deco mesh routers. Talks to the
router's local web API via the `tplink_deco_api` SDK.

## Structure

```
custom_components/tplink_deco/
├── __init__.py              # Integration setup, update_interval=10s
├── const.py                 # DOMAIN, LOGGER, ATTRIBUTION, MANUFACTURER
├── manifest.json
├── config_flow.py           # TpLinkDecoFlowHandler
├── coordinator.py           # TpLinkDecoDataUpdateCoordinator (returns TpLinkDecoSnapshot)
├── data.py                  # TpLinkDecoData + TpLinkDecoConfigEntry type
├── api/
│   ├── __init__.py          # re-exports TpLinkDecoApiClient, TpLinkDecoSnapshot
│   ├── client.py            # TpLinkDecoApiClient.get_snapshot()
│   ├── snapshot.py          # TpLinkDecoSnapshot dataclass
│   └── errors/              # base / authentication / communication exceptions
├── device/
│   ├── __init__.py          # re-exports base device classes
│   ├── client.py            # TpLinkDecoClientDevice
│   └── deco.py              # TpLinkDecoDecoDevice
├── sensor/                  # client_*.py for clients, deco_*.py for nodes
├── binary_sensor/           # client_connected.py, deco_internet.py
├── device_tracker/          # client.py (TpLinkDecoClientTracker)
└── translations/            # en.json, pt-BR.json

tests/                       # pytest suite, ~99% coverage
```

## Key conventions (full list in CODE_STYLE.md)

- **One class per file**, English identifiers, `client_*` / `deco_*` prefixes.
- Base classes in `device/` are named `*Device` (not `*Entity`) and inherit
  `CoordinatorEntity`. Concrete entities multi-inherit `*Device + SensorEntity`
  (or BinarySensorEntity / ScannerEntity).
- **Always `@property`** instead of `_attr_*` assignments in `__init__`.
- **Absolute imports** for parent modules:
  `from custom_components.tplink_deco.device import …`
- All API calls go through a **single `DecoClient` session** in
  `api/client.py::get_snapshot()` to avoid concurrent auth conflicts.
- Coordinator data is always a `TpLinkDecoSnapshot` (clients + nodes +
  optional performance).
- Devices that disappear from the API are **offline, not removed** — entities
  stay registered, `available` returns False. Entity registration is
  listener-driven so devices that come back are picked up automatically.

## Dev environment

```bash
source .venv/bin/activate
bash scripts/develop                          # starts HA at http://localhost:8123
bash scripts/lint                             # ruff format + check
pytest tests/ --cov=custom_components.tplink_deco
```

The SDK installs as `tplink_deco_api` in the venv (renamed from `tplink_deco`
to avoid colliding with this component's namespace).

## Update interval

Configured in `__init__.py` via `update_interval=timedelta(seconds=10)`.
