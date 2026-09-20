"""GEX term structure computation: net GEX across all expirations for a given snapshot time."""

from __future__ import annotations

from datetime import date

import pandas as pd

from tractatus.calc.gex import net_gex_by_strike


def compute_gex_term_structure(
    snapshots: dict[date, pd.DataFrame],
    spot: float,
    strike_range: float,
) -> tuple[list[float], list[date], list[list[float]]]:
    """Compute GEX term structure matrix from pre-loaded snapshot DataFrames.

    For each expiry, computes net GEX per strike using the standard formula:
    gamma * OI * spot² (calls positive, puts negative).

    Args:
        snapshots: {expiry_date: options_dataframe} — one DataFrame per expiry.
        spot: Current underlying price used for strike filtering and GEX formula.
        strike_range: Half-width in points; only strikes within [spot ± strike_range] included.

    Returns:
        (strikes, expirations, matrix) where:
            strikes: sorted list of all strikes that appear across any expiry
            expirations: sorted list of expiry dates
            matrix: matrix[i][j] = net_gex for strikes[i] at expirations[j], 0.0 if absent
    """
    expirations = sorted(snapshots.keys())
    per_expiry: dict[date, dict[float, float]] = {}

    for expiry in expirations:
        df = snapshots[expiry]
        gex_df = net_gex_by_strike(df, spot=spot, strike_range=strike_range)
        per_expiry[expiry] = {
            float(row["strike"]): float(row["net_gex"]) for _, row in gex_df.iterrows()
        }

    all_strikes = sorted({s for strike_map in per_expiry.values() for s in strike_map})

    if not all_strikes or not expirations:
        return [], [], []

    matrix = [[per_expiry[exp].get(strike, 0.0) for exp in expirations] for strike in all_strikes]

    return all_strikes, expirations, matrix
