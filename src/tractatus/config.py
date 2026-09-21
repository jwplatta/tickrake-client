"""Resolved configuration for Tractatus research projects and data access."""

from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import cast

from dotenv import dotenv_values

_GLOBAL_CONFIG_PATH = Path.home() / ".tractatus" / "config.toml"
_DEFAULTS = {
    "mlflow_tracking_uri": "http://localhost:5000",
    "mlflow_experiment_name": "default",
    "aws_region": "us-east-1",
    "s3_region": "us-east-1",
    "tickrake_data_dir": str(Path.home() / ".tickrake" / "data"),
}
_ENV_NAMES = {
    "mlflow_tracking_uri": "MLFLOW_TRACKING_URI",
    "mlflow_experiment_name": "MLFLOW_EXPERIMENT_NAME",
    "aws_profile": "AWS_PROFILE",
    "aws_region": "AWS_REGION",
    "s3_bucket": "S3_BUCKET",
    "s3_region": "S3_REGION",
    "tickrake_data_dir": "TICKRAKE_DATA_DIR",
}


@dataclass(frozen=True)
class TractatusConfig:
    """Resolve overrides, environment, project, user config, then defaults."""

    mlflow_tracking_uri: str
    mlflow_experiment_name: str
    aws_profile: str | None
    aws_region: str
    s3_bucket: str | None
    s3_region: str
    tickrake_data_dir: Path

    @classmethod
    def load(
        cls,
        *,
        project_dir: Path | None = None,
        config_path: Path | None = None,
        overrides: Mapping[str, str | None] | None = None,
    ) -> TractatusConfig:
        """Resolve settings without mutating the process environment."""
        user_values = _read_toml(config_path or _GLOBAL_CONFIG_PATH)
        project_values = {
            key: value
            for key, value in dotenv_values((project_dir or Path.cwd()) / ".env").items()
            if value is not None
        }
        values: dict[str, str | None] = dict(_DEFAULTS)
        values.update({key: str(value) for key, value in user_values.items() if key in _ENV_NAMES})
        values.update(
            {
                key: project_values[env_name]
                for key, env_name in _ENV_NAMES.items()
                if env_name in project_values
            }
        )
        values.update(
            {
                key: os.environ[env_name]
                for key, env_name in _ENV_NAMES.items()
                if env_name in os.environ
            }
        )
        if overrides:
            values.update(overrides)
        return cls(
            mlflow_tracking_uri=_required(values, "mlflow_tracking_uri"),
            mlflow_experiment_name=_required(values, "mlflow_experiment_name"),
            aws_profile=values.get("aws_profile") or None,
            aws_region=_required(values, "aws_region"),
            s3_bucket=values.get("s3_bucket") or None,
            s3_region=_required(values, "s3_region"),
            tickrake_data_dir=Path(_required(values, "tickrake_data_dir")).expanduser(),
        )

    def as_dict(self) -> dict[str, str | None]:
        values = asdict(self)
        values["tickrake_data_dir"] = str(self.tickrake_data_dir)
        return values


def default_config_path() -> Path:
    return _GLOBAL_CONFIG_PATH


def config_template() -> str:
    return """# Personal non-secret defaults for Tractatus.
# Project .env values and exported environment variables take precedence.
mlflow_tracking_uri = "http://localhost:5000"
mlflow_experiment_name = "default"
aws_profile = "default"
aws_region = "us-east-1"
s3_bucket = "your-tickrake-bucket"
s3_region = "us-east-1"
tickrake_data_dir = "~/.tickrake/data"

# Never put AWS access keys, session tokens, or passwords here. Boto3 uses the
# selected AWS profile, SSO, role credentials, or other standard AWS providers.
"""


def _read_toml(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    with path.open("rb") as source:
        values = tomllib.load(source)
    return (
        cast(dict[str, object], values.get("tractatus", values)) if isinstance(values, dict) else {}
    )


def _required(values: Mapping[str, str | None], key: str) -> str:
    value = values.get(key)
    if not value:
        raise ValueError(f"Missing required configuration value: {key}")
    return value
