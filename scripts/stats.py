#!/usr/bin/env python3
"""Print aggregate statistics for agents-unite sentiment reports."""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from assign_ticker import load_active_tickers  # noqa: E402
from validate_report import DATA_DIR, parse_report_sentiment  # noqa: E402


def discover_reports() -> list[tuple[str, str, float | None, Path]]:
    """Return (date, ticker, sentiment_score, report_dir) for each report."""
    reports: list[tuple[str, str, float | None, Path]] = []
    if not DATA_DIR.is_dir():
        return reports

    for report_path in sorted(DATA_DIR.glob("*/*/report*.md")):
        if report_path.parent.parent.name.startswith("_"):
            continue
        date = report_path.parent.parent.name
        ticker = report_path.parent.name
        text = report_path.read_text(encoding="utf-8")
        score, _ = parse_report_sentiment(text)
        reports.append((date, ticker, score, report_path.parent))
    return reports


def format_score(score: float | None) -> str:
    if score is None:
        return "n/a"
    return f"{score:+.2f}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Print agents-unite dataset statistics.")
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of top bullish/bearish tickers to show (default: 5)",
    )
    args = parser.parse_args()

    reports = discover_reports()
    universe_size = len(load_active_tickers())

    print("=== agents-unite stats ===\n")

    if not reports:
        print("Total reports:     0")
        print("Universe size:     ", universe_size)
        print("\nNo reports found under data/.")
        return 0

    dates = sorted({r[0] for r in reports})
    tickers = {r[1] for r in reports}
    scored = [(d, t, s) for d, t, s, _ in reports if s is not None]

    print(f"Total reports:     {len(reports)}")
    print(f"Unique tickers:    {len(tickers)}")
    print(f"Date range:        {dates[0]} → {dates[-1]} ({len(dates)} day(s))")
    print(f"Universe size:     {universe_size}")

    by_date: dict[str, list[float]] = defaultdict(list)
    for date, _, score in scored:
        by_date[date].append(score)

    print("\nAverage sentiment by date:")
    for date in dates:
        scores = by_date.get(date, [])
        if scores:
            avg = sum(scores) / len(scores)
            coverage = len(scores) / universe_size * 100
            print(
                f"  {date}:  {avg:+.3f}  "
                f"({len(scores)} reports, {coverage:.1f}% coverage)"
            )
        else:
            print(f"  {date}:  n/a  (0 scored reports)")

    latest_date = dates[-1]
    latest_tickers = {t for d, t, _, _ in reports if d == latest_date}
    latest_coverage = len(latest_tickers) / universe_size * 100
    print(f"\nLatest-day coverage ({latest_date}): {latest_coverage:.1f}%")

    if scored:
        ranked = sorted(scored, key=lambda item: item[2], reverse=True)
        top_n = max(1, args.top)

        print(f"\nTop {top_n} bullish (all dates, by score):")
        for date, ticker, score in ranked[:top_n]:
            print(f"  {ticker:6s}  {score:+.2f}  ({date})")

        print(f"\nTop {top_n} bearish (all dates, by score):")
        for date, ticker, score in ranked[-top_n:][::-1]:
            print(f"  {ticker:6s}  {score:+.2f}  ({date})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
