# Contributing

## Development setup

1. Install Python 3.11+.
2. Install project dependencies:

```bash
uv sync
```

## Workflow

1. Branch off `main` with a focused branch named `feature/...`, `fix/...`, `chore/...`, `docs/...`, or `refactor/...`.
2. Keep changes targeted. Do not mix unrelated cleanup into the same branch.
3. Add or update tests for behavior changes.
4. Run relevant checks before opening a pull request.
5. Use conventional commits, for example `feat: add order book date filtering` or `fix: handle missing parquet files`.
6. Bump the package version only when cutting a release.

## Running checks

Run all checks before committing or opening a pull request:

```bash
make check    # runs lint, format, typecheck, and tests
```

Individual checks:

```bash
make lint       # uv run ruff check src tests
make format     # uv run ruff format --check src tests
make typecheck  # uv run mypy src
make test       # uv run pytest tests/ -q
make fix        # auto-fix lint and format issues
```

## Testing

Write simple tests that focus on core functionality — reading data, discovery helpers, and config behavior. Use `tmp_path` fixtures to create minimal data directory structures rather than mocking. Tests should verify that the right data comes back in the right shape, not implementation details. See `tests/conftest.py` for shared fixture examples.

## Project boundaries

- Keep production code under `src/tractatus/`.
- Keep automated tests under `tests/`.
- This package is read-only against tickrake data. Never write, modify, or delete files under `~/.tickrake/`.
- Prefer small, focused modules per dataset type over large mixed-responsibility files.

## Changelog

Update `CHANGELOG.md` as part of every pull request. Add entries under an `## [Unreleased]` section at the top. Use `### Added`, `### Changed`, `### Fixed`, or `### Removed` sub-headings as appropriate. When cutting a release, rename `[Unreleased]` to the version and date.

## Pull requests

- Open pull requests against `main`.
- Keep commits focused and intentional.
- Use conventional commit messages.
- Include a `CHANGELOG.md` update describing user-visible changes.
- Include tests for data-loading, discovery, or config changes.
- Call out any manual verification steps for behavior that is difficult to cover with automated tests.
