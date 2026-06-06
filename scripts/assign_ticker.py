#!/usr/bin/env python3
"""Ticker assignment with coverage optimizer."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from au_common import (  # noqa: E402
    contributor_hash,
    contributor_id,
    coverage_counts,
    hash_fraction,
    load_active_tickers,
    resolve_investigation_date,
    weighted_pick,
)

# Weight for tickers with zero reports vs overcrowded tickers
ZERO_COVERAGE_WEIGHT = 10.0
OVERCROWD_PENALTY = 1.5


def assign_ticker(
    investigation_date: str | None = None,
    contributor: str | None = None,
    universe_path: Path | None = None,
    *,
    date_mode: str | None = None,
) -> dict:
    """
    Assign ticker using hash + coverage optimizer.

    Same contributor + same day → same ticker (deterministic draw).
    Coverage bias steers mass toward tickers with zero reports today.
    """
    if investigation_date is None:
        investigation_date = resolve_investigation_date(date_mode)

    _validate_date(investigation_date)

    path = universe_path or REPO_ROOT / "tickers" / "universe.json"
    tickers = load_active_tickers(path)
    cid = contributor_id(contributor)
    chash = contributor_hash(contributor)
    seed = f"{investigation_date}:{chash}:ticker"

    counts = coverage_counts(investigation_date)
    weights: list[float] = []
    for ticker in tickers:
        c = counts.get(ticker, 0)
        if c == 0:
            w = ZERO_COVERAGE_WEIGHT
        else:
            w = 1.0 / (1.0 + c * OVERCROWD_PENALTY)
        weights.append(w)

    ticker, index = weighted_pick(tickers, weights, seed)

    return {
        "date": investigation_date,
        "date_mode": date_mode or "utc_midnight",
        "ticker": ticker,
        "contributor_id": cid,
        "contributor_hash": chash,
        "github_username": cid if not cid.startswith("anonymous") else None,
        "seed": seed,
        "index": index,
        "universe_size": len(tickers),
        "coverage_today": counts.get(ticker, 0),
        "zero_coverage_pool": sum(1 for t in tickers if counts.get(t, 0) == 0),
    }


def _validate_date(value: str) -> None:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(f"Invalid date '{value}', expected YYYY-MM-DD") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Assign ticker with coverage optimizer.")
    parser.add_argument("--date", help="Override date YYYY-MM-DD")
    parser.add_argument("--date-mode", choices=["utc_midnight", "us_close"])
    parser.add_argument("--contributor", help="Contributor id (GitHub username preferred)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    investigation_date = args.date
    if investigation_date is None:
        investigation_date = resolve_investigation_date(args.date_mode)

    try:
        result = assign_ticker(
            investigation_date,
            args.contributor,
            date_mode=args.date_mode,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result["ticker"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
