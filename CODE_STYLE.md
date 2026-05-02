# Code Style Guide

Style conventions for the `ha-tplink-deco` project. Run `bash scripts/lint`
before committing — it executes `ruff format` then `ruff check --fix` and must
exit cleanly.

## Language

- All code is written in **English**: file names, class names, function names,
  variable names, dictionary keys, translation keys and any identifier that
  appears in code.
- User-facing strings live in `translations/{en,pt-BR}.json` only — do not
  hardcode them in Python files.

## File organization

- **One class per file.** Each `.py` file under `custom_components/tplink_deco`
  contains exactly one public class.
- **Subdirectories group classes by context**:
  - `api/` — SDK wrapper, errors, snapshot dataclass
  - `device/` — base device classes (`TpLinkDecoClientDevice`, `TpLinkDecoDecoDevice`)
  - `sensor/`, `binary_sensor/`, `device_tracker/` — Home Assistant platforms
- **Platform `__init__.py` files** contain only `async_setup_entry`.
- **Subpackage `__init__.py` files** only re-export public symbols via `__all__`.
- **File name prefixes** mirror the represented entity:
  - `client_*.py` → entities for connected clients
  - `deco_*.py` → entities for the Deco mesh nodes themselves

## Naming

- Public classes are prefixed with `TpLinkDeco`.
- Base device classes end with `Device` (e.g. `TpLinkDecoClientDevice`).
- Concrete Home Assistant entities end with the entity type
  (e.g. `TpLinkDecoClientMacSensor`, `TpLinkDecoClientConnectedBinarySensor`).
- Private attributes are prefixed with `_` (e.g. `self._client_mac`).

## Properties and `__init__`

- **Always prefer `@property`** over assigning `_attr_*` values in `__init__`.
  When the body of `__init__` would only call `super().__init__(...)`, omit
  `__init__` entirely and let Python inherit the parent.
- Compute attributes lazily from backing fields stored in the parent class
  (e.g. `self._client_mac`, `self._node_mac`).

## Imports

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

- Always start runtime-typed modules with `from __future__ import annotations`
  so type hints become lazy strings.

## Docstrings

- Every public class, function, method (including `@property`) and `__init__`
  has a docstring. Ruff enforces this via `D102`/`D107`.
- Keep them short — a single sentence is usually enough. Describe **why** or
  the contract, not the obvious implementation.
- Avoid restating the type — the signature already does that.

## Comments

- Default to **no comments**. Add one only when the *why* is not obvious from
  the code (a hidden constraint, a workaround, a subtle invariant).
- Never describe *what* the code does — well-named identifiers handle that.
- **No section dividers** like `# --- Client sensors ---` to group related
  declarations. If a file has so many sections that you feel the need for
  visual separators, split it into multiple files instead.

## Coordinator and snapshot

- All API data flows through `TpLinkDecoSnapshot` (defined in
  `api/snapshot.py`). The coordinator's `_async_update_data` returns the
  snapshot as-is from `client.get_snapshot()`.
- Performing multiple API calls **must** happen inside a single
  `DecoClient` session (see `api/client.py::get_snapshot`) to avoid concurrent
  authentication conflicts.

## Entities and offline devices

- A device disappearing from the API response means it is offline, not gone.
  Entities must remain registered: override `available` on the base device
  class to compare against the current snapshot. Listener-driven entity
  registration handles devices that come back online or appear for the first
  time.

## Linting

- Ruff configuration lives in `.ruff.toml` with `select = ["ALL"]`.
- Do not silence rules with `# noqa` unless the violation is unavoidable and
  has a clear justification — fix the underlying code instead.
- `bash scripts/lint` runs both formatter and linter and is the single source
  of truth for style.
