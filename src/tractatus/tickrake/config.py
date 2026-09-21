"""Connection config for tickrake data sources."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from tractatus.config import TractatusConfig


@dataclass
class TickrakeConfig:
    data_dir: Path
    minio_endpoint: str
    minio_bucket: str
    minio_access_key: str
    minio_secret_key: str
    s3_bucket: str
    s3_region: str
    aws_profile: str | None = None

    @property
    def options_dir(self) -> Path:
        return self.data_dir / "options"

    @property
    def candles_dir(self) -> Path:
        return self.data_dir / "candles"

    @property
    def level_one_dir(self) -> Path:
        return self.data_dir / "level_one"

    @property
    def order_book_dir(self) -> Path:
        return self.data_dir / "order_book"

    @property
    def index_cache_dir(self) -> Path:
        return self.data_dir / "index_cache"

    def provider_options_dir(self, provider: str) -> Path:
        return self.options_dir / provider

    def provider_candles_dir(self, provider: str) -> Path:
        return self.candles_dir / provider

    def provider_level_one_dir(self, provider: str) -> Path:
        return self.level_one_dir / provider

    def provider_order_book_dir(self, provider: str) -> Path:
        return self.order_book_dir / provider

    @classmethod
    def from_env(cls) -> TickrakeConfig:
        return cls.from_tractatus_config(TractatusConfig.load())

    @classmethod
    def from_tractatus_config(cls, config: TractatusConfig) -> TickrakeConfig:
        return cls(
            data_dir=config.tickrake_data_dir,
            minio_endpoint=os.environ.get("MINIO_ENDPOINT", "http://localhost:9000"),
            minio_bucket=os.environ.get("MINIO_BUCKET", "tickrake"),
            minio_access_key=os.environ.get("MINIO_ACCESS_KEY", ""),
            minio_secret_key=os.environ.get("MINIO_SECRET_KEY", ""),
            s3_bucket=config.s3_bucket or "",
            s3_region=config.s3_region,
            aws_profile=config.aws_profile,
        )
