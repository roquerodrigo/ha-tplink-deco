# Contributing

Bug reports, ideas and pull requests are welcome.

## Reporting a bug

Open an [issue](https://github.com/roquerodrigo/ha-tplink-deco/issues/new/choose)
with:

- the Home Assistant version, the integration version and the Deco model;
- what you did, what you expected and what happened;
- the diagnostics downloaded from the integration's menu (the password is
  redacted) and the relevant log lines.

## Development setup

The project uses [uv](https://docs.astral.sh/uv/). A dev container
(`.devcontainer.json`) with everything installed is also provided.

```bash
scripts/setup      # install the dependencies into .venv
scripts/develop    # run Home Assistant at http://localhost:8123 with this integration loaded
```

`scripts/develop` uses the configuration in [`config/`](config/).

## Checks

Run these before opening a pull request. CI runs the same ones, and
`pre-commit install` runs the first three on every commit.

```bash
uv run ruff format .                         # format
uv run ruff check . --fix                    # lint
uv run mypy custom_components/tplink_deco    # type-check
uv run pytest                                # tests, coverage must stay at 90 % or more
```

Read [CODE_STYLE.md](CODE_STYLE.md) before adding or restructuring code.

## Pull requests

1. Fork the repository and branch from `main`.
2. Write commit messages as [Conventional Commits](https://www.conventionalcommits.org/).
   Releases and their notes are generated from them. Mark breaking changes
   with `!` or a `BREAKING CHANGE:` footer.
3. Update `translations/en.json` and `translations/pt-BR.json` together when
   you change user-facing strings.
4. Update the README when behaviour, configuration or entities change.
5. Fill in the pull request template.

## License

Contributions are released under the project's [MIT License](LICENSE).
