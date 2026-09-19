"""Tests for CandlesClient."""

from __future__ import annotations

from datetime import date

from tickrake_client.candles import CandlesClient


def test_list_providers(cfg, candles_dir):
    client = CandlesClient(cfg)
    assert "test-provider" in client.list_providers()


def test_list_frequencies(cfg, candles_dir):
    client = CandlesClient(cfg)
    assert client.list_frequencies("test-provider") == ["5min"]


def test_list_symbols(cfg, candles_dir):
    client = CandlesClient(cfg)
    assert client.list_symbols("test-provider") == ["SPY"]
    assert client.list_symbols("test-provider", frequency="5min") == ["SPY"]


def test_list_symbols_missing_provider(cfg, candles_dir):
    client = CandlesClient(cfg)
    assert client.list_symbols("nonexistent") == []


def test_read(cfg, candles_dir):
    client = CandlesClient(cfg)
    df = client.read("SPY", "5min", provider="test-provider")
    assert len(df) == 3
    assert list(df.columns) == ["datetime", "open", "high", "low", "close", "volume"]


def test_read_with_date_filter(cfg, candles_dir):
    client = CandlesClient(cfg)
    df = client.read(
        "SPY", "5min", provider="test-provider",
        start=date(2026, 1, 5), end=date(2026, 1, 5),
    )
    assert len(df) == 3


def test_read_missing_symbol(cfg, candles_dir):
    client = CandlesClient(cfg)
    df = client.read("AAPL", "5min", provider="test-provider")
    assert df.empty


def test_date_range(cfg, candles_dir):
    client = CandlesClient(cfg)
    result = client.date_range("SPY", "5min", provider="test-provider")
    assert result is not None
    earliest, latest = result
    assert earliest < latest


def test_date_range_missing(cfg, candles_dir):
    client = CandlesClient(cfg)
    assert client.date_range("AAPL", "5min", provider="test-provider") is None
