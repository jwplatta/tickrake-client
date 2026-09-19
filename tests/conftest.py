"""Shared fixtures for tickrake-client tests."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from tractatus.tickrake.config import TickrakeConfig


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """Create a minimal tickrake data directory structure."""
    return tmp_path / "data"


@pytest.fixture
def cfg(data_dir: Path) -> TickrakeConfig:
    """TickrakeConfig pointing at the tmp data dir with no real S3/MinIO."""
    return TickrakeConfig(
        data_dir=data_dir,
        minio_endpoint="http://localhost:9000",
        minio_bucket="tickrake",
        minio_access_key="",
        minio_secret_key="",
        s3_bucket="",
        s3_region="us-east-1",
    )


@pytest.fixture
def candles_dir(data_dir: Path) -> Path:
    """Populate candles/test-provider/5min/SPY_5min.csv."""
    freq_dir = data_dir / "candles" / "test-provider" / "5min"
    freq_dir.mkdir(parents=True)
    df = pd.DataFrame(
        {
            "datetime": [
                "2026-01-05T14:30:00Z",
                "2026-01-05T14:35:00Z",
                "2026-01-05T14:40:00Z",
            ],
            "open": [100.0, 101.0, 102.0],
            "high": [101.0, 102.0, 103.0],
            "low": [99.0, 100.0, 101.0],
            "close": [100.5, 101.5, 102.5],
            "volume": [1000, 2000, 3000],
        }
    )
    df.to_csv(freq_dir / "SPY_5min.csv", index=False)
    return data_dir / "candles"


@pytest.fixture
def level_one_dir(data_dir: Path) -> Path:
    """Populate level_one/test-provider/2026/01/05/SPY_143000Z.parquet."""
    day_dir = data_dir / "level_one" / "test-provider" / "2026" / "01" / "05"
    day_dir.mkdir(parents=True)
    table = pa.table(
        {
            "received_at_ms": [1000, 2000, 3000],
            "symbol": ["SPY", "SPY", "SPY"],
            "service": ["LEVELONE_EQUITIES"] * 3,
            "bid": [100.0, 100.1, 100.2],
            "ask": [100.1, 100.2, 100.3],
            "last": [100.05, 100.15, 100.25],
        }
    )
    pq.write_table(table, day_dir / "SPY_143000Z.parquet")
    return data_dir / "level_one"


@pytest.fixture
def order_book_dir(data_dir: Path) -> Path:
    """Populate order_book/test-provider/2026/01/05/SPY_150000Z.parquet."""
    day_dir = data_dir / "order_book" / "test-provider" / "2026" / "01" / "05"
    day_dir.mkdir(parents=True)
    table = pa.table(
        {
            "received_at_ms": [4000, 5000],
            "symbol": ["SPY", "SPY"],
            "service": ["LISTED_BOOK"] * 2,
            "bids_json": ['[{"0":100}]', '[{"0":100.1}]'],
            "asks_json": ['[{"0":100.1}]', '[{"0":100.2}]'],
        }
    )
    pq.write_table(table, day_dir / "SPY_150000Z.parquet")
    return data_dir / "order_book"


@pytest.fixture
def options_dir(data_dir: Path) -> Path:
    """Populate options/test-provider/ with tickers.json, ROOT.json, and a snapshot CSV."""
    provider_dir = data_dir / "options" / "test-provider"
    provider_dir.mkdir(parents=True)

    # tickers.json
    (provider_dir / "tickers.json").write_text(
        json.dumps({"schema_version": 1, "provider": "test-provider", "roots": ["SPY", "SPXW"]})
    )

    # ROOT.json
    (provider_dir / "SPY.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "provider": "test-provider",
                "root": "SPY",
                "historical": [
                    {
                        "sample_date": "2026-01-04",
                        "status": "ready",
                        "files": {
                            "parquet": {
                                "uri": "s3://bucket/SPY_samples_2026-01-04.parquet",
                                "row_count": 100,
                            }
                        },
                    }
                ],
                "intraday": None,
            }
        )
    )

    # snapshot CSV
    day_dir = provider_dir / "2026" / "01" / "05"
    day_dir.mkdir(parents=True)
    snapshot = day_dir / "SPY_exp2026-01-10_2026-01-05_14-30-00.csv"
    snapshot.write_text("strike,bid,ask\n100,1.0,1.1\n")

    # cached parquet (so archive doesn't need S3)
    day_dir_hist = provider_dir / "2026" / "01" / "04"
    day_dir_hist.mkdir(parents=True)
    table = pa.table({"strike": [100, 105], "bid": [1.0, 2.0], "ask": [1.1, 2.1]})
    pq.write_table(table, day_dir_hist / "SPY_samples_2026-01-04.parquet")

    return data_dir / "options"
