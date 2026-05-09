# Changelog

## [1.1.2](https://github.com/roquerodrigo/ha-tplink-deco/compare/v1.1.1...v1.1.2) (2026-05-09)


### Bug Fixes

* apply unavailable grace period in coordinator, not per-entity ([#19](https://github.com/roquerodrigo/ha-tplink-deco/issues/19)) ([c86ae7c](https://github.com/roquerodrigo/ha-tplink-deco/commit/c86ae7cf6d27602714b102e31edc254707f09c35))

## [1.1.1](https://github.com/roquerodrigo/ha-tplink-deco/compare/v1.1.0...v1.1.1) (2026-05-08)


### Bug Fixes

* increase unavailable grace period to 600s for mobile wifi sleep ([a9b981a](https://github.com/roquerodrigo/ha-tplink-deco/commit/a9b981ae56f286bf84b7be85d8f039430d61067c))
* **sensor:** map non-enum connection_type values to None ([eea89b5](https://github.com/roquerodrigo/ha-tplink-deco/commit/eea89b5e0b37c043fb816133435113b07c5cd8b1))
* **sensor:** map non-enum interface values to None ([5f26113](https://github.com/roquerodrigo/ha-tplink-deco/commit/5f26113f5f0c4b72e9aae75e02f33769592f98e5))

## [1.1.0](https://github.com/roquerodrigo/ha-tplink-deco/compare/v1.0.2...v1.1.0) (2026-05-08)


### Features

* delay reporting devices as unavailable by 90s ([3864bd9](https://github.com/roquerodrigo/ha-tplink-deco/commit/3864bd99900d22c7bf53d1f10392f5b18ea31671))


### Bug Fixes

* **types:** resolve mypy errors surfaced by the new strict config ([f874410](https://github.com/roquerodrigo/ha-tplink-deco/commit/f8744107cf3f59d8d073073ec13715b97e18a4a1))


### Dependencies

* **deps:** bump github/codeql-action ([283d92d](https://github.com/roquerodrigo/ha-tplink-deco/commit/283d92db012386c1b5460a9c7bc838de81fb91fd))
* **deps:** bump mypy from 1.18.2 to 2.0.0 ([93c8445](https://github.com/roquerodrigo/ha-tplink-deco/commit/93c8445b80bf27914c4da4d449b1fe85ea12610e))
* **deps:** update pip requirement from &gt;=26.1 to &gt;=26.1.1 ([9547bdc](https://github.com/roquerodrigo/ha-tplink-deco/commit/9547bdcbb8d04e9986ef2026d83871d8fa96decb))
