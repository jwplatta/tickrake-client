"""Tests for TickrakeConfig."""

from __future__ import annotations

from pathlib import Path

from tickrake_client.config import TickrakeConfig


def test_from_env_defaults(monkeypatch):
    monkeypatch.delenv("TICKRAKE_DATA_DIR", raising=False)
    cfg = TickrakeConfig.from_env()
    assert cfg.data_dir == Path.home() / ".tickrake" / "data"
    assert cfg.minio_endpoint == "http://localhost:9000"


def test_from_env_custom_data_dir(monkeypatch):
    monkeypatch.setenv("TICKRAKE_DATA_DIR", "/tmp/custom")
    cfg = TickrakeConfig.from_env()
    assert cfg.data_dir == Path("/tmp/custom")


def test_provider_dir_helpers(cfg):
    assert cfg.provider_options_dir("schwab") == cfg.data_dir / "options" / "schwab"
    assert cfg.provider_candles_dir("ibkr") == cfg.data_dir / "candles" / "ibkr"
    assert cfg.provider_level_one_dir("schwab") == cfg.data_dir / "level_one" / "schwab"
    assert cfg.provider_order_book_dir("schwab") == cfg.data_dir / "order_book" / "schwab"
