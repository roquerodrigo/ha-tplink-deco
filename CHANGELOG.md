# Changelog

## [1.4.1](https://github.com/roquerodrigo/ha-tplink-deco/compare/v1.4.0...v1.4.1) (2026-05-25)


### Documentation

* fix and standardize README badges ([3e86082](https://github.com/roquerodrigo/ha-tplink-deco/commit/3e8608220db0614dd7009fb5faa73bf70f7acc4d))
* fix and standardize README badges ([c685377](https://github.com/roquerodrigo/ha-tplink-deco/commit/c68537739a69829304e1c538a85a65842cfd5db7))

## [1.4.0](https://github.com/roquerodrigo/ha-tplink-deco/compare/v1.3.1...v1.4.0) (2026-05-17)


### Features

* smooth download/upload speeds with exponential moving average ([7d69139](https://github.com/roquerodrigo/ha-tplink-deco/commit/7d69139753cf1ca7f340317ce2335143891fc555))


### Reverts

* undo branch rename attempts ([649dbe9](https://github.com/roquerodrigo/ha-tplink-deco/commit/649dbe9ccf36f7b1a5b836b59afd9874a2e10f4f))

## [1.3.1](https://github.com/roquerodrigo/ha-tplink-deco/compare/v1.3.0...v1.3.1) (2026-05-17)


### Bug Fixes

* remove unused type-ignore comment flagged by mypy ([11806b4](https://github.com/roquerodrigo/ha-tplink-deco/commit/11806b4bc7316954a7468c632894ceab7be8249f))
* resolve mypy and ruff lint errors ([6f5b2bc](https://github.com/roquerodrigo/ha-tplink-deco/commit/6f5b2bc8bfd28f1dd9c57828d9185112117f02f8))
* unmerge devices when link_devices_by_mac is disabled ([93183ee](https://github.com/roquerodrigo/ha-tplink-deco/commit/93183eec5caa14aefb9139deddcee4d797dff491))

## [1.3.0](https://github.com/roquerodrigo/ha-tplink-deco/compare/v1.2.0...v1.3.0) (2026-05-14)


### Features

* add option to disable MAC-based device linking ([3324f92](https://github.com/roquerodrigo/ha-tplink-deco/commit/3324f92614f66950d29d7d4724b4e6f2eaab99d0))
* **diagnostics:** add diagnostics platform with password redaction ([dc68ce2](https://github.com/roquerodrigo/ha-tplink-deco/commit/dc68ce230180e8689231ae26128a656a12cbf5f3))

## [1.2.0](https://github.com/roquerodrigo/ha-tplink-deco/compare/v1.1.2...v1.2.0) (2026-05-11)


### Features

* add total download and upload speed sensors ([3977374](https://github.com/roquerodrigo/ha-tplink-deco/commit/39773748edba8e0536d53a953f125f8132d5988b))
* total download and upload speed sensors ([aecfd8c](https://github.com/roquerodrigo/ha-tplink-deco/commit/aecfd8cc2cc9f8a1a7aab139261e3dbc9703124c))


### Dependencies

* bump tplink-deco-api to 1.1.0 ([7e2969c](https://github.com/roquerodrigo/ha-tplink-deco/commit/7e2969c4fc38fd1c6e57bbea73a8f92954507aaf))


### Documentation

* standardize CODE_STYLE.md template ([83cfeaa](https://github.com/roquerodrigo/ha-tplink-deco/commit/83cfeaaaf9e82689d93d3e6617faa1bc87b8aa72))
* standardize CODE_STYLE.md template ([0c0fd67](https://github.com/roquerodrigo/ha-tplink-deco/commit/0c0fd6730fa489fbc553f27751f143b7eba5e2d2))

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
