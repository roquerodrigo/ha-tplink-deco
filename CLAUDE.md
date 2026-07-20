# ha-tplink-deco

Home Assistant custom integration for TP-Link Deco mesh routers. Talks to the
router's local web API via the `tplink_deco_api` SDK.

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
  Users *can* manually delete an offline device from the UI:
  `async_remove_config_entry_device` in `__init__.py` only refuses removal for
  clients/nodes the router still reports as active; a removed device that
  reconnects later is simply re-registered.
- The bundled Lovelace card (`www/tplink-deco-card.js`) is served from
  `custom_components/tplink_deco/www` via a registered static path and
  auto-added as a frontend module (`add_extra_js_url`) in `async_setup_entry`
  — users don't need to add a dashboard resource by hand. Its URL is
  cache-busted with `?v=<integration.version>` on every release.

## Dev environment

```bash
source .venv/bin/activate
bash scripts/develop                          # starts HA at http://localhost:8123
uv run ruff format .                          # format
uv run ruff check . --fix                     # lint
uv run mypy custom_components/tplink_deco     # type-check
pytest tests/ --cov=custom_components.tplink_deco
```

The SDK installs as `tplink_deco_api` in the venv (renamed from `tplink_deco`
to avoid colliding with this component's namespace).

The SDK version is pinned in **two places that don't auto-sync**:
`manifest.json`'s `requirements` (what HA actually installs at runtime) and
the `tplink-deco-api` entry in `pyproject.toml`'s dev group (what tests run
against). Dependabot only bumps the `pyproject.toml`/`uv.lock` pin — bumping
the SDK requires manually updating `manifest.json` too, or tests will pass
against a newer SDK than what ships.

## Update interval

Configured in `__init__.py` via `update_interval=timedelta(seconds=20)`.
