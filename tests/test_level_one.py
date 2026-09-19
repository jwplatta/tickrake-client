"""Tests for LevelOneClient."""

from __future__ import annotations

from datetime import date

from tickrake_client.level_one import LevelOneClient


def test_list_providers(cfg, level_one_dir):
    client = LevelOneClient(cfg)
    assert "test-provider" in client.list_providers()


def test_list_dates(cfg, level_one_dir):
    client = LevelOneClient(cfg)
    assert client.list_dates("test-provider") == [date(2026, 1, 5)]


def test_list_dates_filtered_by_symbol(cfg, level_one_dir):
    client = LevelOneClient(cfg)
    assert client.list_dates("test-provider", symbol="SPY") == [date(2026, 1, 5)]
    assert client.list_dates("test-provider", symbol="AAPL") == []


def test_list_symbols(cfg, level_one_dir):
    client = LevelOneClient(cfg)
    assert client.list_symbols("test-provider") == ["SPY"]


def test_list_symbols_filtered_by_date(cfg, level_one_dir):
    client = LevelOneClient(cfg)
    assert client.list_symbols("test-provider", sample_date=date(2026, 1, 5)) == ["SPY"]
    assert client.list_symbols("test-provider", sample_date=date(2026, 1, 6)) == []


def test_read(cfg, level_one_dir):
    client = LevelOneClient(cfg)
    df = client.read("SPY", date(2026, 1, 5), provider="test-provider")
    assert len(df) == 3
    assert "received_at_ms" in df.columns
    assert "bid" in df.columns
    assert df["received_at_ms"].is_monotonic_increasing


def test_read_missing(cfg, level_one_dir):
    client = LevelOneClient(cfg)
    df = client.read("AAPL", date(2026, 1, 5), provider="test-provider")
    assert df.empty
