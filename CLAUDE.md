# ha-tplink-deco

Home Assistant custom integration for TP-Link Deco routers.

## Structure

```
custom_components/tplink_deco/
├── __init__.py              # Integration setup, update_interval
├── const.py                 # Constants (DOMAIN, LOGGER, ATTRIBUTION)
├── manifest.json            # Integration metadata and requirements
├── config_flow.py           # TpLinkDecoFlowHandler — UI config flow
├── coordinator.py           # TpLinkDecoDataUpdateCoordinator
├── data.py                  # TpLinkDecoData dataclass + TpLinkDecoConfigEntry type
├── entity.py                # TpLinkDecoClientEntity — base entity with availability logic
├── api/
│   ├── __init__.py          # re-exports TpLinkDecoApiClient
│   ├── client.py            # TpLinkDecoApiClient
│   └── errors/
│       ├── __init__.py      # re-exports all error classes
│       ├── base.py          # TpLinkDecoApiClientError
│       ├── authentication.py # TpLinkDecoApiClientAuthenticationError
│       └── communication.py  # TpLinkDecoApiClientCommunicationError
└── sensor/
    ├── __init__.py          # async_setup_entry (HA platform entry point)
    ├── mac.py               # TpLinkDecoMacSensor
    └── ip.py                # TpLinkDecoIpSensor
```

## Conventions

- **One class per file.**
- **Subdirectories per context** — `api/` for the SDK wrapper and errors, `sensor/` for sensor entities.
- Platform files (`sensor/__init__.py`) contain only the `async_setup_entry` function.
- Subpackage `__init__.py` files only re-export public symbols.

## Dev environment

```bash
source .venv/bin/activate
bash scripts/develop   # starts HA at http://localhost:8123
```

The SDK (`tplink-deco-api`) installs as module `tplink_deco` in site-packages.
It has been renamed to `tplink_deco_api` inside the venv to avoid collision with
the custom component's own `tplink_deco` namespace.

## Sensor update interval

Configured in `__init__.py` via `update_interval=timedelta(seconds=10)`.
