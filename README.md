# tractatus

[![Tests](https://github.com/jwplatta/tractatus/actions/workflows/ci.yml/badge.svg)](https://github.com/jwplatta/tractatus/actions/workflows/ci.yml)

Tractatus Research — data access, calculations, and utilities for trading research. Built on data collected by [tickrake](https://github.com/jwplatta/tickrake).

## Installation

```bash
# As a git dependency
uv add "tractatus @ git+ssh://git@github.com/jwplatta/tractatus.git@main"
```

## Tickrake data access

The `tractatus.tickrake` module reads from `~/.tickrake/data/` by default. Override with the `TICKRAKE_DATA_DIR` environment variable.

| Dataset | Format | Source |
|---|---|---|
| **Options chains** | CSV (intraday), Parquet (historical) | MinIO, S3, local filesystem |
| **Candles** | CSV | Local filesystem |
| **Level one quotes** | Parquet | Local filesystem |
| **Order book** | Parquet | Local filesystem |

For MinIO and S3 access, set the relevant environment variables:

```bash
export MINIO_ENDPOINT="http://localhost:9000"
export MINIO_BUCKET="tickrake"
export MINIO_ACCESS_KEY="..."
export MINIO_SECRET_KEY="..."
export S3_BUCKET="your-tickrake-bucket"
export S3_REGION="us-east-1"
```

### Usage

```python
from tractatus.tickrake import TickrakeClient

client = TickrakeClient()
```

#### Candles

```python
client.candles.list_providers()  # ['ibkr-paper', 'schwab', ...]
client.candles.list_frequencies("schwab")  # ['1min', '5min', '30min', 'day']
client.candles.list_symbols("schwab", frequency="5min")  # ['SPX', 'SPY', ...]

from datetime import date

df = client.candles.read("SPX", "5min", provider="schwab")
df = client.candles.read("SPX", "5min", start=date(2026, 1, 1), end=date(2026, 6, 1))
client.candles.date_range("SPX", "5min")  # (datetime, datetime)
```

#### Level one quotes

```python
client.level_one.list_symbols("schwab")  # ['IWM', 'QQQ', 'SPY']
client.level_one.list_dates("schwab", symbol="SPY")  # [date(2026, 9, 18)]
df = client.level_one.read("SPY", date(2026, 9, 18))
```

#### Order book

```python
client.order_book.list_symbols("schwab")
client.order_book.list_dates("schwab", symbol="IWM")
df = client.order_book.read("IWM", date(2026, 9, 18))
```

#### Options

```python
client.options_filesystem.list_roots("schwab")  # ['AAPL', 'SPXW', ...]
client.options_filesystem.list_sample_dates("SPXW", "schwab")

# Scan local intraday snapshots
snapshots = client.options_filesystem.scan_snapshots("SPXW", date(2026, 9, 18))

# Get historical parquet (downloads from S3 if not cached locally)
path = client.options_archive.get_parquet_path("SPXW", date(2026, 9, 17))

# Fetch current intraday data from MinIO
expirations = client.options_intraday.list_expirations("SPXW")
df = client.options_intraday.fetch_csv(uri, dtypes={...})
```

## Development

```bash
uv sync
uv run pytest
uv run ruff check .
uv run mypy src
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for workflow details.
