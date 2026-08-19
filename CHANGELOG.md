# Changelog

## [1.6.2](https://github.com/roquerodrigo/ha-tplink-deco/compare/v1.6.1...v1.6.2) (2026-08-19)


### Bug Fixes

* **sensor:** restore the total state class on the online clients sensor ([eac3021](https://github.com/roquerodrigo/ha-tplink-deco/commit/eac302104505edb89b3eb8a2722d0041a0812231))

## [1.6.1](https://github.com/roquerodrigo/ha-tplink-deco/compare/v1.6.0...v1.6.1) (2026-08-14)


### Bug Fixes

* **sensor:** count only the clients reported as online ([87be053](https://github.com/roquerodrigo/ha-tplink-deco/commit/87be0533a6e4482ec86e1abe69a8fce657266f39))


### Documentation

* drop the empty TODO list from the repository ([23d6a1d](https://github.com/roquerodrigo/ha-tplink-deco/commit/23d6a1d9951f0ee612c7b16c84cb2c20bbd105dd))
* normalize README header layout ([0340199](https://github.com/roquerodrigo/ha-tplink-deco/commit/0340199fe32b0e27127a52aa62786891db242fa0))

## [1.6.0](https://github.com/roquerodrigo/ha-tplink-deco/compare/v1.5.2...v1.6.0) (2026-08-07)


### Features

* **sensor:** mark the MAC and IP address sensors as diagnostic ([b6b3c98](https://github.com/roquerodrigo/ha-tplink-deco/commit/b6b3c987f57e29b5eee2b2d9bb615b8a5e89e91c))


### Bug Fixes

* **config_flow:** add a reauth flow for rejected credentials ([09788b5](https://github.com/roquerodrigo/ha-tplink-deco/commit/09788b5ad9deb856aacceb65a8a70414147f20da))
* **device:** guard the client and node lookups before the first refresh ([46bb1db](https://github.com/roquerodrigo/ha-tplink-deco/commit/46bb1dbf5da6127cf9bfac72ab255835d60932c9))
* report client presence from the router's online flag ([66efa9a](https://github.com/roquerodrigo/ha-tplink-deco/commit/66efa9ac8371c08823aef11062fb848019c61a93))


### Code Refactoring

* **const:** enable postponed annotation evaluation ([0d0ddc8](https://github.com/roquerodrigo/ha-tplink-deco/commit/0d0ddc82e468208cf110f92df473cc62f634f9da))
* **coordinator:** declare the grace and smoothing caches in a typed constructor ([bcf2c11](https://github.com/roquerodrigo/ha-tplink-deco/commit/bcf2c1154594574f6ff380182dc7fed567e6c425))


### Dependencies

* align the manifest SDK pin and HACS floor with the tested versions ([cc44bad](https://github.com/roquerodrigo/ha-tplink-deco/commit/cc44bad04e310bcd67793db064d393a545d0482f))


### Documentation

* align the project docs with the current implementation ([2ebe713](https://github.com/roquerodrigo/ha-tplink-deco/commit/2ebe71363e36e5787ed21b160a022230bdffca0d))


### Continuous Integration

* run checks on pull requests targeting any branch ([d7e9399](https://github.com/roquerodrigo/ha-tplink-deco/commit/d7e9399e65c7776338e0de293b8b373a5e7bc85c))
* run code scanning on pull requests targeting any branch ([157c159](https://github.com/roquerodrigo/ha-tplink-deco/commit/157c15980f2fe51202e359b03e47788c77e43851))


### Tests

* keep translation locales and entity translation keys in sync ([04daa47](https://github.com/roquerodrigo/ha-tplink-deco/commit/04daa479406dc94df34deb81bbf569c27136ba42))


### Miscellaneous Chores

* **card:** drop the unused card.title translation key ([a1acbbd](https://github.com/roquerodrigo/ha-tplink-deco/commit/a1acbbd0708621f94a372258b7a4b760f83f9c3d))
* run the setup script and pre-commit hooks through uv ([d77791c](https://github.com/roquerodrigo/ha-tplink-deco/commit/d77791cf3169995cb67c8fed594313a401675187))

## [1.5.2](https://github.com/roquerodrigo/ha-tplink-deco/compare/v1.5.1...v1.5.2) (2026-08-05)


### Bug Fixes

* register the bundled card as a Lovelace dashboard resource ([963e122](https://github.com/roquerodrigo/ha-tplink-deco/commit/963e1221ec68429ac13042a2fab965765259e17b))


### Development Dependencies

* **deps-dev:** bump pre-commit ([2ff6f08](https://github.com/roquerodrigo/ha-tplink-deco/commit/2ff6f08d4024e4652698e0ea87d44d70f26fa2ee))
* **deps-dev:** bump ruff ([2675d8d](https://github.com/roquerodrigo/ha-tplink-deco/commit/2675d8d37956f513b606b8caf26d796cb4d6adc2))
* **deps-dev:** bump ruff in the python-development group ([695b6e3](https://github.com/roquerodrigo/ha-tplink-deco/commit/695b6e38ce8fe5e393211d0f461b8b8797518b5e))


### Documentation

* update CLAUDE.md ([d31624a](https://github.com/roquerodrigo/ha-tplink-deco/commit/d31624ac875ec481199997423a63f68b164598bb))


### Continuous Integration

* assign open issues and pull requests to the repository owner ([4c73801](https://github.com/roquerodrigo/ha-tplink-deco/commit/4c738017b569bfa89fd84ace58b293a3e66920b2))
* call the shared auto-assign workflow instead of duplicating it ([724e8bc](https://github.com/roquerodrigo/ha-tplink-deco/commit/724e8bccd927633424f467aaf9d39d1a11c4ecef))
* drop the auto-assign job now handled by its own workflow ([1525190](https://github.com/roquerodrigo/ha-tplink-deco/commit/152519086367aba352437b1bcd08bc60bcbc0bab))
* drop the blank line left by the removed job ([1f5dad5](https://github.com/roquerodrigo/ha-tplink-deco/commit/1f5dad591772b8c2924921e5697edc5bdb015c6c))
* split the CI workflow into one file per concern ([d14944d](https://github.com/roquerodrigo/ha-tplink-deco/commit/d14944db5d8eb8dae44fbd256f3d6496c6403685))


### Miscellaneous Chores

* **deps-dev:** bump ruff to 0.16.0 ([58b218b](https://github.com/roquerodrigo/ha-tplink-deco/commit/58b218b402085297f968f467092f05338acf6cfa))
* move CI to the shared workflows repository ([5790a90](https://github.com/roquerodrigo/ha-tplink-deco/commit/5790a906e1f2a2533766280fa657c7684d00d50f))
* release on every conventional commit type ([630aa26](https://github.com/roquerodrigo/ha-tplink-deco/commit/630aa261b11291d35b60f33b6251c8f3a45b0500))

## [1.5.1](https://github.com/roquerodrigo/ha-tplink-deco/compare/v1.5.0...v1.5.1) (2026-07-15)


### Bug Fixes

* guard against duplicate custom element registration ([2ea8004](https://github.com/roquerodrigo/ha-tplink-deco/commit/2ea800488de6cca1a7d83b83ad5f82dab79524c1))

## [1.5.0](https://github.com/roquerodrigo/ha-tplink-deco/compare/v1.4.2...v1.5.0) (2026-07-12)


### Features

* add bundled Lovelace card for Deco clients ([2695b38](https://github.com/roquerodrigo/ha-tplink-deco/commit/2695b38d41f3a3baf74d8f07555351030f3b0403))
* add bundled Lovelace card for Deco clients ([a60f301](https://github.com/roquerodrigo/ha-tplink-deco/commit/a60f301fae9ac01cde7c173e38bcdc9badf12dee))
* allow removing offline devices from the UI ([027e74b](https://github.com/roquerodrigo/ha-tplink-deco/commit/027e74bd1c551058d728fd6a58dc247faecfcd13))
* allow removing offline devices from the UI ([a216439](https://github.com/roquerodrigo/ha-tplink-deco/commit/a2164391a3e379f65036c616d0f7e7350f28ecf6))


### Dependencies

* **deps:** bump pip from 26.1.1 to 26.1.2 ([4ddcc1c](https://github.com/roquerodrigo/ha-tplink-deco/commit/4ddcc1ca7ef07f9fca413e08503438618e73331d))

## [1.4.2](https://github.com/roquerodrigo/ha-tplink-deco/compare/v1.4.1...v1.4.2) (2026-07-03)


### Bug Fixes

* point manifest documentation and issue_tracker to integration repo ([9f26bac](https://github.com/roquerodrigo/ha-tplink-deco/commit/9f26bac0a404f3dcf9723593097c910fe989f4e6))

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
