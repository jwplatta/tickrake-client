"""S3 archive access with local parquet cache."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import urlparse

import boto3

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client

from tractatus.tickrake.config import TickrakeConfig


class ArchiveClient:
    def __init__(self, cfg: TickrakeConfig) -> None:
        self._cfg = cfg
        self._s3: S3Client = boto3.client(
            "s3",
            region_name=cfg.s3_region,
        )

    def get_root_index(self, root: str, provider: str = "schwab") -> dict[str, Any]:
        """Read the local ROOT.json index for root."""
        path = self._cfg.provider_options_dir(provider) / f"{root}.json"
        if not path.exists():
            return {}
        return cast(dict[str, Any], json.loads(path.read_text()))

    def get_parquet_path(
        self, root: str, sample_date: date, provider: str = "schwab"
    ) -> Path | None:
        """Return the local parquet path for sample_date, downloading from S3 if needed."""
        options_dir = self._cfg.provider_options_dir(provider)
        local_path = (
            options_dir
            / f"{sample_date.year:04d}"
            / f"{sample_date.month:02d}"
            / f"{sample_date.day:02d}"
            / f"{root}_samples_{sample_date.isoformat()}.parquet"
        )
        if local_path.exists():
            return local_path

        uri = self._find_parquet_uri(root, sample_date, provider)
        if uri is None:
            return None

        self._download(uri, local_path)
        return local_path if local_path.exists() else None

    def _find_parquet_uri(self, root: str, sample_date: date, provider: str) -> str | None:
        index = self.get_root_index(root, provider)
        for entry in index.get("historical", []):
            if entry.get("sample_date") == sample_date.isoformat():
                files = entry.get("files", {})
                parquet = files.get("parquet")
                if parquet and "uri" in parquet:
                    return str(parquet["uri"])
        return None

    def _download(self, uri: str, local_path: Path) -> None:
        parsed = urlparse(uri)
        bucket = parsed.netloc or self._cfg.s3_bucket
        key = parsed.path.lstrip("/")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        self._s3.download_file(bucket, key, str(local_path))
