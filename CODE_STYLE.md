# Code Style Guide

Style conventions for the `ha-tplink-deco` project. Before committing run
`uv run ruff format .`, `uv run ruff check . --fix` and
`uv run mypy custom_components/tplink_deco`, all of which must exit cleanly.
`pytest` (with the 80 % coverage gate) follows.

**Always read this file before adding or restructuring code.**

## Language

- Code is written in **English**: file names, class names, function names,
  variable names, dictionary keys, identifier strings.
- The conversation language with the user can be Portuguese or anything else;
  what is committed to disk stays English.
- User-facing strings live in `custom_components/tplink_deco/translations/{en,pt-BR}.json`
  only — never hardcoded in Python.

## File organization

- **One top-level class per file.** Multiple semantically related classes (e.g.
  exception families, sensor entities for one platform) get grouped into a
  package directory with one class per submodule and an `__init__.py`
  re-exporting the public symbols.
- **Subdirectories group classes by context**:
  - `api/` — SDK wrapper, errors, snapshot dataclass.
  - `device/` — base device classes (`TpLinkDecoClientDevice`, `TpLinkDecoDecoDevice`).
  - `sensor/`, `binary_sensor/`, `device_tracker/` — Home Assistant platforms.
- **TypedDicts and `type` aliases do not count as "classes"** for this rule —
  they live alongside related code and don't need their own file.
- **File name prefixes** mirror the represented entity:
  - `client_*.py` → entities for connected clients.
  - `deco_*.py` → entities for the Deco mesh nodes themselves.
- **Platform `__init__.py` files** contain only `async_setup_entry`.
- **Subpackage `__init__.py` files** only re-export public symbols via `__all__`.
- **`__init__.py` of the integration package** wires `async_setup_entry`,
  `async_unload_entry`, `async_reload_entry` and nothing else.

## Entities: one class per entity

- **One class per entity.** Every entity gets its own dedicated class — never
  share a generic class parameterized by an `EntityDescription` subclass with
  callable fields like `value_fn` or `action_fn`. Encode the entity's behaviour
  directly in its class via `@property` and class-level `_attr_*` constants
  (or a plain `EntityDescription` instance assigned at the class level).
  - Don't write a `TpLinkDecoSensorDescription` subclass with a `value_fn` field.
  - Do write `TpLinkDecoClientMacSensor`, `TpLinkDecoClientConnectedBinarySensor`,
    `TpLinkDecoDecoCpuSensor`, etc. — one file each under `sensor/` /
    `binary_sensor/` / `device_tracker/`.
- The reason: each entity is a discrete contract; mixing them through a
  generic class hides the contract behind indirection and discourages per-entity
  refinement (icons, state attributes, custom logic).

## Naming

- Public classes are prefixed with `TpLinkDeco`.
- Base device classes end with `Device` (e.g. `TpLinkDecoClientDevice`,
  `TpLinkDecoDecoDevice`).
- Concrete Home Assistant entities end with the entity type
  (e.g. `TpLinkDecoClientMacSensor`, `TpLinkDecoClientConnectedBinarySensor`).
- Exception classes end with `Error`: `TpLinkDecoApiClientError`,
  `TpLinkDecoApiClientCommunicationError`,
  `TpLinkDecoApiClientAuthenticationError`.
- Private attributes are prefixed with `_` (e.g. `self._client_mac`).

## Typing

**Strict typing. No generics, no `Any`.** `uv run mypy custom_components/tplink_deco` enforces this.

Banned: `typing.Any`, `object` as a value type, bare `dict` / `list` / `tuple` /
`set`, `dict[str, Any]`, `Mapping[str, Any]`.

Required:

- `@dataclass` for structured records (`TpLinkDecoSnapshot`, `TpLinkDecoData`).
- `frozenset[str]` / `tuple[str, ...]` for fixed string collections.
- `cast("TypedDictName", value)` at HA framework boundaries that hand us a
  permissive type (e.g. `entry.data` is `MappingProxyType[str, Any]`).

When narrowing an HA-provided callback signature, mypy reports `[override]`
(Liskov violation). Add `# type: ignore[override]` with a one-line comment
explaining the deliberate narrowing.

## Properties and `__init__`

- **Always prefer `@property`** over assigning `_attr_*` values in `__init__`.
  When the body of `__init__` would only call `super().__init__(...)`, omit
  `__init__` entirely and let Python inherit the parent.
- Compute attributes lazily from backing fields stored in the parent class
  (e.g. `self._client_mac`, `self._node_mac`).

## Imports

- Always start every module with `from __future__ import annotations` so type
  hints become lazy strings.
- Use **absolute imports from the package root** for parent modules:

  ```python
  from custom_components.tplink_deco.device import TpLinkDecoClientDevice
  ```

  Relative `from ..something import` is rejected by Ruff's `TID252`.
- Same-package relative imports (`from .module import …`) are allowed.
- Move third-party type-only imports into a `TYPE_CHECKING` block (Ruff
  `TC002`):

  ```python
  from __future__ import annotations
  from typing import TYPE_CHECKING

  if TYPE_CHECKING:
      from tplink_deco_api import ClientDevice
  ```

- `noqa` comments are reserved for unavoidable framework constraints. Never
  silence to "make ruff happy" — fix the underlying code.

## Docstrings

- Every public class, function, method (including `@property`) and `__init__`
  has a docstring. Ruff enforces this via `D102`/`D107`.
- A single sentence is usually enough. Describe the *contract* or the *why*,
  not the obvious implementation.
- Module-level docstring at the top of every `.py` file.
- Avoid restating the type — the signature already does that.

## Comments

- Default to **no comments**. Add one only when the *why* is not obvious from
  the code: a hidden constraint, a workaround, a subtle invariant.
- Never describe *what* the code does — well-named identifiers handle that.
- **No section dividers** like `# --- Client sensors ---` to group related
  declarations. If a file has so many sections that you feel the need for
  visual separators, split it into multiple files instead.

## Logging

- Each module uses the package-level `LOGGER` from `const.py`
  (`LOGGER: Logger = getLogger(__package__)`); never call `logging.getLogger(...)`
  ad-hoc.
- Use **lazy `%`-formatting**, never f-strings — they force string interpolation
  even when the level is filtered:

  ```python
  LOGGER.warning("Authentication failed: %s", exception)   # ✓
  LOGGER.warning(f"Authentication failed: {exception}")    # ✗
  ```

- Levels:
  - `debug` — successful fetch summaries, every-poll diagnostics.
  - `info` — one-shot lifecycle (setup complete, reauth flow started).
  - `warning` — recoverable failures (transient API error, falling back).
  - `error` / `exception` — unrecoverable in current cycle.
- Never log secrets (`password`, full session cookies). Wrap the upstream
  exception in the API-client boundary so its string form doesn't leak.

## Error messages

- Format: `"Failed to <verb> <object>: <cause>"`. Keep them short and grep-able.
- Custom exceptions get the same hierarchy:
  `TpLinkDecoApiClientError` (base) → `…CommunicationError` (timeout,
  connection, DNS) and `…AuthenticationError` (401/403). Wrap raw upstream
  errors at the API client boundary; everything above only catches the
  custom hierarchy.

## Coordinator, snapshot, and grace period

- All API data flows through `TpLinkDecoSnapshot` (defined in
  `api/snapshot.py`). The coordinator's `_async_update_data` calls
  `client.get_snapshot()` then runs `_apply_grace()` to re-inject clients and
  nodes that disappeared from the latest fetch but are still within
  `UNAVAILABLE_GRACE_PERIOD_SECONDS` (single source of truth for the grace
  cache; per-entity properties just read the augmented snapshot).
- Performing multiple API calls **must** happen inside a single
  `DecoClient` session (see `api/client.py::get_snapshot`) to avoid concurrent
  authentication conflicts.
- A device disappearing from the API response means it is offline, not gone.
  Entities stay registered (listener-driven registration handles devices that
  return) and just report `available=False` once the grace window expires.

## Config / repairs / diagnostics

- `config_flow.py` carries `user`, `reauth`, `reauth_confirm` and `reconfigure`
  steps, all sharing one `_validate` helper and one `_credentials_schema`
  builder.
- `diagnostics.py` redacts `password` via `async_redact_data` (driven by
  `TO_REDACT: frozenset[str]`).

## Translations

- Two locales: `en.json` and `pt-BR.json`. The translation file's nested key
  sets must stay in sync between locales.
- Issue strings live under `issues.<issue_id>`; flow strings under
  `config.step.<step_id>`; entity names under `entity.<platform>.<key>.name`.

## Pre-commit hooks

`pre-commit` is recommended. `.pre-commit-config.yaml` mirrors the lint
gates (ruff format, ruff check, mypy); install it once per clone:

```bash
pre-commit install
```

The hook runs the same gates as CI on every commit. Skip it only on
emergency `git commit --no-verify` and immediately re-run
`uv run ruff format .`, `uv run ruff check . --fix` and
`uv run mypy custom_components/tplink_deco`.

## Conventional commits

All commits follow [Conventional Commits](https://www.conventionalcommits.org/),
which `release-please` parses to bump the version and generate `CHANGELOG.md`:

| Type | Meaning | Bump |
|---|---|---|
| `feat` | New feature | minor |
| `fix` | Bug fix | patch |
| `perf` | Performance improvement | patch |
| `deps` | Dependency bump | patch |
| `docs` | Documentation only | none |
| `refactor` | Refactor without behavior change | none |
| `test` | Test-only change | none |
| `ci` | CI / tooling change | none |
| `chore` | Anything else (rarely) | none |

- Subject line: imperative mood, lowercase, no trailing period.
- Use scopes when useful: `fix(sensor): map non-enum interface values to None`.
- A `BREAKING CHANGE:` footer (or `!` after type) bumps the major version.

## Linting and verification

- Ruff configuration lives in `pyproject.toml` (`[tool.ruff]`) with
  `select = ["ALL"]`.
- Mypy configuration also lives in `pyproject.toml` (`[tool.mypy]`).
- After every change run `uv run ruff format .`, `uv run ruff check . --fix`,
  `uv run mypy custom_components/tplink_deco` and `pytest`. All gates mirror CI
  (`.github/workflows/ci.yml`).
- Tests live in `tests/`, mirroring the production layout. The 80 % coverage
  gate (`pyproject.toml`, `[tool.pytest.ini_options]`) prevents untested code
  from sneaking in. When a test
  exercises a state that is impossible under the new types, update or remove
  it — never weaken the type to satisfy the test.
