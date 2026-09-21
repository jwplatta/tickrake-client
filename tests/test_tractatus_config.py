"""Tests for layered Tractatus configuration."""

from __future__ import annotations

from tractatus.config import TractatusConfig, config_template
from tractatus.tickrake.config import TickrakeConfig


def test_config_precedence(tmp_path, monkeypatch):
    config_path = tmp_path / "config.toml"
    config_path.write_text('s3_bucket = "global-bucket"\naws_profile = "global-profile"\n')
    project = tmp_path / "project"
    project.mkdir()
    (project / ".env").write_text("S3_BUCKET=project-bucket\nAWS_PROFILE=project-profile\n")
    monkeypatch.setenv("S3_BUCKET", "environment-bucket")

    config = TractatusConfig.load(
        project_dir=project,
        config_path=config_path,
        overrides={"s3_bucket": "override-bucket"},
    )

    assert config.s3_bucket == "override-bucket"
    assert config.aws_profile == "project-profile"


def test_tickrake_config_uses_resolved_aws_settings(tmp_path):
    config = TractatusConfig.load(
        project_dir=tmp_path,
        config_path=tmp_path / "absent.toml",
        overrides={
            "tickrake_data_dir": str(tmp_path / "tickrake"),
            "s3_bucket": "research-bucket",
            "aws_profile": "research",
        },
    )

    tickrake = TickrakeConfig.from_tractatus_config(config)

    assert tickrake.data_dir == tmp_path / "tickrake"
    assert tickrake.s3_bucket == "research-bucket"
    assert tickrake.aws_profile == "research"


def test_config_template_excludes_credentials():
    template = config_template()
    assert "aws_profile" in template
    assert "s3_bucket" in template
    assert "aws_secret_access_key =" not in template
