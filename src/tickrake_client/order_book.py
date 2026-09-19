"""Order book data access — local parquet files organized by provider/date/symbol."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from tickrake_client.config import TickrakeConfig

_FILENAME_RE = re.compile(r"^(.+?)_(\d{6})Z\.parquet$")


class OrderBookClient:
    def __init__(self, cfg: TickrakeConfig) -> None:
        self._cfg = cfg

    def read(
        self,
        symbol: str,
        sample_date: date,
        provider: str = "schwab",
    ) -> pd.DataFrame:
        """Read all order book snapshots for a symbol on a given date.

        Returns a concatenated DataFrame sorted by received_at_ms.
        """
        day_dir = self._date_dir(provider, sample_date)
        if not day_dir.exists():
            return pd.DataFrame()

        files = sorted(day_dir.glob(f"{symbol}_*Z.parquet"))
        if not files:
            return pd.DataFrame()

        combined = pa.concat_tables([pq.read_table(f) for f in files])
        df: pd.DataFrame = combined.to_pandas()
        return df.sort_values("received_at_ms").reset_index(drop=True)

    def list_symbols(
        self,
        provider: str = "schwab",
        sample_date: date | None = None,
    ) -> list[str]:
        """Return sorted list of symbols with order book data.

        If sample_date is given, only check that date. Otherwise scan all dates.
        """
        base = self._cfg.provider_order_book_dir(provider)
        if not base.exists():
            return []

        dirs = [self._date_dir(provider, sample_date)] if sample_date else list(base.glob("*/*/*"))
        symbols: set[str] = set()
        for day_dir in dirs:
            if not day_dir.is_dir():
                continue
            for p in day_dir.glob("*_*Z.parquet"):
                m = _FILENAME_RE.match(p.name)
                if m:
                    symbols.add(m.group(1))
        return sorted(symbols)

    def list_dates(
        self,
        provider: str = "schwab",
        symbol: str | None = None,
    ) -> list[date]:
        """Return sorted list of dates with order book data.

        If symbol is given, only return dates that have data for that symbol.
        """
        base = self._cfg.provider_order_book_dir(provider)
        if not base.exists():
            return []
        dates: list[date] = []
        for day_dir in base.glob("*/*/*"):
            if not day_dir.is_dir():
                continue
            if symbol and not list(day_dir.glob(f"{symbol}_*Z.parquet")):
                continue
            try:
                parts = day_dir.relative_to(base).parts
                dates.append(date(int(parts[0]), int(parts[1]), int(parts[2])))
            except (ValueError, IndexError):
                continue
        return sorted(dates)

    def list_providers(self) -> list[str]:
        """Return sorted list of order book data providers."""
        base = self._cfg.order_book_dir
        if not base.exists():
            return []
        return sorted(d.name for d in base.iterdir() if d.is_dir())

    def _date_dir(self, provider: str, d: date) -> Path:
        return (
            self._cfg.provider_order_book_dir(provider)
            / f"{d.year:04d}"
            / f"{d.month:02d}"
            / f"{d.day:02d}"
        )
