# tickrake-client

Python client for reading data collected by [tickrake](https://github.com/jwplatta/tickrake). Provides a unified interface over local filesystem data, MinIO intraday snapshots, and S3 historical archives.

## Supported data types

| Dataset | Format | Source |
|---|---|---|
| **Options chains** | CSV (intraday), Parquet (historical) | MinIO, S3, local filesystem |
| **Candles** | CSV | Local filesystem |
| **Level one quotes** | Parquet | Local filesystem |
| **Order book** | Parquet | Local filesystem |

## Installation

```bash
# As a path dependency in another project
uv add tickrake-client --path ~/repos/tickrake-client

# Or install directly
uv pip install -e ~/repos/tickrake-client
```

## Setup

tickrake-client reads from `~/.tickrake/data/` by default. Override with the `TICKRAKE_DATA_DIR` environment variable.

For MinIO (intraday options) and S3 (historical options), set:

```bash
export MINIO_ENDPOINT="http://localhost:9000"
export MINIO_BUCKET="tickrake"
export MINIO_ACCESS_KEY="..."
export MINIO_SECRET_KEY="..."
export S3_BUCKET="your-tickrake-bucket"
export S3_REGION="us-east-1"
```

## Usage

```python
from tickrake_client import TickrakeClient

client = TickrakeClient()
```

### Candles

```python
# List available symbols and frequencies
client.candles.list_providers()          # ['ibkr-paper', 'schwab', ...]
client.candles.list_frequencies("schwab") # ['1min', '5min', '30min', 'day']
client.candles.list_symbols("schwab", frequency="5min")  # ['SPX', 'SPY', ...]

# Read candle data
from datetime import date
df = client.candles.read("SPX", "5min", provider="schwab")
df = client.candles.read("SPX", "5min", start=date(2026, 1, 1), end=date(2026, 6, 1))

# Check date range
client.candles.date_range("SPX", "5min")  # (datetime, datetime)
```

### Level one quotes

```python
# Discover available data
client.level_one.list_providers()                        # ['schwab']
client.level_one.list_symbols("schwab")                  # ['IWM', 'QQQ', 'SPY']
client.level_one.list_dates("schwab", symbol="SPY")      # [date(2026, 9, 18)]

# Read all snapshots for a symbol on a date
df = client.level_one.read("SPY", date(2026, 9, 18))
```

### Order book

```python
# Discover available data
client.order_book.list_symbols("schwab")
client.order_book.list_dates("schwab", symbol="IWM")

# Read all snapshots for a symbol on a date
df = client.order_book.read("IWM", date(2026, 9, 18))
```

### Options

```python
# Discover roots from index files
client.options_filesystem.list_roots("schwab")  # ['AAPL', 'AMZN', 'SPY', 'SPXW', ...]

# Historical sample dates from ROOT.json
client.options_filesystem.list_sample_dates("SPXW", "schwab")

# Scan local intraday snapshots
snapshots = client.options_filesystem.scan_snapshots("SPXW", date(2026, 9, 18))
for fetch_dt, path in snapshots:
    print(fetch_dt, path)

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
