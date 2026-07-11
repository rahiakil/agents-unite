#!/usr/bin/env python3
"""Show ticker coverage for a date — what's researched and what's still open.

Usage:
  python3 scripts/coverage_report.py                 # summary for today
  python3 scripts/coverage_report.py --date 2026-07-11
  python3 scripts/coverage_report.py --uncovered     # list only open tickers
  python3 scripts/coverage_report.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from au_common import coverage_counts, load_active_tickers, resolve_investigation_date  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Ticker coverage report for a date.")
    parser.add_argument("--date", help="YYYY-MM-DD (default: today)")
    parser.add_argument("--uncovered", action="store_true", help="List only tickers with no report")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    date = args.date or resolve_investigation_date()
    tickers = load_active_tickers()
    counts = coverage_counts(date)

    covered = sorted(t for t in tickers if counts.get(t, 0) > 0)
    uncovered = sorted(t for t in tickers if counts.get(t, 0) == 0)

    if args.json:
        print(json.dumps({
            "date": date,
            "universe": len(tickers),
            "covered": covered,
            "uncovered": uncovered,
            "counts": {t: counts.get(t, 0) for t in covered},
        }, indent=2))
        return 0

    if args.uncovered:
        print(f"Uncovered tickers for {date} ({len(uncovered)}/{len(tickers)}):")
        for t in uncovered:
            print(t)
        print(f"\nCover one now:  agents-unite research {uncovered[0] if uncovered else 'TICKER'}")
        return 0

    pct = (len(covered) / len(tickers) * 100) if tickers else 0.0
    print(f"Coverage for {date}")
    print(f"  Universe:  {len(tickers)} active tickers")
    print(f"  Covered:   {len(covered)} ({pct:.1f}%)")
    print(f"  Uncovered: {len(uncovered)}")
    if covered:
        print("\nCovered today:")
        for t in covered:
            print(f"  {t}  ({counts.get(t, 0)} report(s))")
    print("\nFill a gap:  agents-unite research <TICKER>")
    print("List open:   agents-unite coverage --uncovered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
