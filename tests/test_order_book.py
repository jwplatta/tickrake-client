"""Tests for OrderBookClient."""

from __future__ import annotations

from datetime import date

from tickrake_client.order_book import OrderBookClient


def test_list_providers(cfg, order_book_dir):
    client = OrderBookClient(cfg)
    assert "test-provider" in client.list_providers()


def test_list_dates(cfg, order_book_dir):
    client = OrderBookClient(cfg)
    assert client.list_dates("test-provider") == [date(2026, 1, 5)]


def test_list_dates_filtered_by_symbol(cfg, order_book_dir):
    client = OrderBookClient(cfg)
    assert client.list_dates("test-provider", symbol="SPY") == [date(2026, 1, 5)]
    assert client.list_dates("test-provider", symbol="AAPL") == []


def test_list_symbols(cfg, order_book_dir):
    client = OrderBookClient(cfg)
    assert client.list_symbols("test-provider") == ["SPY"]


def test_read(cfg, order_book_dir):
    client = OrderBookClient(cfg)
    df = client.read("SPY", date(2026, 1, 5), provider="test-provider")
    assert len(df) == 2
    assert "received_at_ms" in df.columns
    assert "bids_json" in df.columns


def test_read_missing(cfg, order_book_dir):
    client = OrderBookClient(cfg)
    df = client.read("AAPL", date(2026, 1, 5), provider="test-provider")
    assert df.empty
