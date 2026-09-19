"""Candle data access — local CSV files organized by provider/frequency/symbol."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pandas as pd

from tickrake_client.config import TickrakeConfig


class CandlesClient:
    def __init__(self, cfg: TickrakeConfig) -> None:
        self._cfg = cfg

    def read(
        self,
        symbol: str,
        frequency: str,
        provider: str = "schwab",
        start: date | None = None,
        end: date | None = None,
    ) -> pd.DataFrame:
        """Read candle data for a symbol/frequency, optionally filtered by date range.

        Returns a DataFrame with columns: datetime, open, high, low, close, volume.
        """
        path = self._candle_path(provider, symbol, frequency)
        if not path.exists():
            return pd.DataFrame(columns=["datetime", "open", "high", "low", "close", "volume"])

        df = pd.read_csv(path, parse_dates=["datetime"])
        if df["datetime"].dt.tz is None:
            df["datetime"] = df["datetime"].dt.tz_localize("UTC")
        if start is not None:
            df = df[df["datetime"] >= pd.Timestamp(start, tz="UTC")]
        if end is not None:
            end_ts = (
                pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)
            )
            df = df[df["datetime"] <= end_ts]
        return df

    def list_symbols(self, provider: str = "schwab", frequency: str | None = None) -> list[str]:
        """Return sorted list of symbols available for a provider, optionally filtered by frequency."""
        base = self._cfg.provider_candles_dir(provider)
        if not base.exists():
            return []
        symbols: set[str] = set()
        freqs = [frequency] if frequency else self.list_frequencies(provider)
        for freq in freqs:
            freq_dir = base / freq
            if not freq_dir.exists():
                continue
            for p in freq_dir.glob("*.csv"):
                # filename: SYMBOL_freq.csv
                name = p.stem
                suffix = f"_{freq}"
                sym = name.removesuffix(suffix) if name.endswith(suffix) else name
                symbols.add(sym)
        return sorted(symbols)

    def list_frequencies(self, provider: str = "schwab") -> list[str]:
        """Return sorted list of frequencies available for a provider."""
        base = self._cfg.provider_candles_dir(provider)
        if not base.exists():
            return []
        return sorted(d.name for d in base.iterdir() if d.is_dir())

    def list_providers(self) -> list[str]:
        """Return sorted list of candle data providers."""
        base = self._cfg.candles_dir
        if not base.exists():
            return []
        return sorted(d.name for d in base.iterdir() if d.is_dir())

    def date_range(
        self, symbol: str, frequency: str, provider: str = "schwab"
    ) -> tuple[datetime, datetime] | None:
        """Return (earliest, latest) datetime for a candle file, or None if not found."""
        path = self._candle_path(provider, symbol, frequency)
        if not path.exists():
            return None
        df = pd.read_csv(path, usecols=["datetime"], parse_dates=["datetime"])
        if df.empty:
            return None
        return df["datetime"].min().to_pydatetime(), df["datetime"].max().to_pydatetime()

    def _candle_path(self, provider: str, symbol: str, frequency: str) -> Path:
        return self._cfg.provider_candles_dir(provider) / frequency / f"{symbol}_{frequency}.csv"
