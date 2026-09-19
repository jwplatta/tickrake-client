# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-19

### Changed

- Renamed package from `tickrake-client` to `tractatus`.
- Moved all tickrake data access modules under `tractatus.tickrake` subpackage. Import path is now `from tractatus.tickrake import TickrakeClient`.
- Updated intraday index reader to support renamed `option_chains` key (tickrake PR #92), with backward compatibility for `intraday` key.

### Added

- `IntradayClient.fetch_candle_csv()` and `list_candle_frequencies()` for reading candle CSVs from MinIO.

## [0.1.0] - 2026-09-19

### Added

- `TickrakeConfig` with data dir and provider path helpers, configurable via environment variables.
- `CandlesClient` for reading candle CSVs with date range filtering and discovery helpers (`list_symbols`, `list_frequencies`, `list_providers`, `date_range`).
- `LevelOneClient` for reading level one quote parquet snapshots with discovery helpers (`list_symbols`, `list_dates`, `list_providers`).
- `OrderBookClient` for reading order book parquet snapshots with discovery helpers (`list_symbols`, `list_dates`, `list_providers`).
- Options sub-clients:
  - `ArchiveClient` for S3 historical parquet with local cache.
  - `IntradayClient` for MinIO intraday CSV access.
  - `FilesystemClient` for local snapshot scanning and index reading (`list_roots`, `list_sample_dates`, `scan_snapshots`).
- `TickrakeClient` facade exposing all sub-clients.
- Basic test suite covering all dataset clients.
