"""Local timestamped CSV scanning for intraday option snapshots."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

from tickrake_client.config import TickrakeConfig


class FilesystemClient:
    def __init__(self, cfg: TickrakeConfig) -> None:
        self._cfg = cfg

    def scan_snapshots(
        self,
        root: str,
        sample_date: date,
        provider: str = "schwab",
    ) -> list[tuple[datetime, Path]]:
        """Return all timestamped CSVs for any expiry on sample_date, sorted by fetch time."""
        dir_path = _date_dir(self._cfg.provider_options_dir(provider), sample_date)
        if not dir_path.exists():
            return []
        results: list[tuple[datetime, Path]] = []
        for p in dir_path.glob(f"{root}_exp*_*_*.csv"):
            parsed = parse_snapshot_filename(p)
            if parsed is None:
                continue
            _exp, fetch_dt = parsed
            results.append((fetch_dt, p))
        return sorted(results, key=lambda x: x[0])

    def scan_snapshots_for_expiry(
        self,
        root: str,
        expiry: date,
        sample_date: date,
        provider: str = "schwab",
    ) -> list[tuple[datetime, Path]]:
        """Return timestamped CSVs for a specific expiry on sample_date."""
        return [
            (dt, p)
            for dt, p in self.scan_snapshots(root, sample_date, provider)
            if _expiry_from_path(p) == expiry
        ]

    def scan_all_snapshots_for_expiry(
        self,
        root: str,
        expiry: date,
        provider: str = "schwab",
    ) -> list[tuple[datetime, Path]]:
        """Scan all date directories for snapshots of the given expiry."""
        options_dir = self._cfg.provider_options_dir(provider)
        results: list[tuple[datetime, Path]] = []
        for day_dir in sorted(options_dir.glob("*/*/*")):
            if not day_dir.is_dir():
                continue
            for p in day_dir.glob(f"{root}_exp{expiry.isoformat()}_*_*.csv"):
                parsed = parse_snapshot_filename(p)
                if parsed is None:
                    continue
                _exp, fetch_dt = parsed
                results.append((fetch_dt, p))
        return sorted(results, key=lambda x: x[0])

    def list_sample_dates(self, root: str, provider: str = "schwab") -> list[date]:
        """Return sorted historical sample dates from the local ROOT.json."""
        root_json = self._cfg.provider_options_dir(provider) / f"{root}.json"
        if not root_json.exists():
            return []
        data: dict[str, object] = json.loads(root_json.read_text())
        historical = data.get("historical", [])
        if not isinstance(historical, list):
            return []
        return sorted(
            date.fromisoformat(str(entry["sample_date"]))
            for entry in historical
            if "sample_date" in entry
        )

    def list_sample_dates_for_expiry(
        self, root: str, expiry: date, provider: str = "schwab"
    ) -> list[date]:
        """Return historical sample dates that likely include snapshots for expiry."""
        return self.list_sample_dates(root, provider)

    def list_expirations_in_window_on_date(
        self,
        root: str,
        sample_date: date,
        start_exp: date,
        end_exp: date,
        provider: str = "schwab",
    ) -> list[date]:
        """Return distinct expiration dates in [start_exp, end_exp] with snapshots on sample_date."""
        expiries: set[date] = set()
        for _dt, p in self.scan_snapshots(root, sample_date, provider):
            exp = _expiry_from_path(p)
            if exp is not None and start_exp <= exp <= end_exp:
                expiries.add(exp)
        return sorted(expiries)

    def list_roots(self, provider: str = "schwab") -> list[str]:
        """Return sorted list of option roots with index files."""
        tickers_json = self._cfg.provider_options_dir(provider) / "tickers.json"
        if not tickers_json.exists():
            return []
        data = json.loads(tickers_json.read_text())
        return sorted(data.get("roots", []))


def parse_snapshot_filename(path: Path) -> tuple[date, datetime] | None:
    """Parse {ROOT}_exp{YYYY-MM-DD}_{YYYY-MM-DD}_{HH-MM-SS}.csv.

    Returns (expiration_date, fetch_datetime_utc) or None if pattern does not match.
    """
    parts = path.stem.split("_")
    if len(parts) < 4:
        return None
    try:
        exp_date = date.fromisoformat(parts[1].removeprefix("exp"))
        fetch_dt = datetime.strptime(f"{parts[2]}_{parts[3]}", "%Y-%m-%d_%H-%M-%S").replace(
            tzinfo=UTC
        )
        return exp_date, fetch_dt
    except ValueError:
        return None


def _expiry_from_path(path: Path) -> date | None:
    parsed = parse_snapshot_filename(path)
    return parsed[0] if parsed is not None else None


def _date_dir(options_dir: Path, d: date) -> Path:
    return options_dir / f"{d.year:04d}" / f"{d.month:02d}" / f"{d.day:02d}"
