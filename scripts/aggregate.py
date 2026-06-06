#!/usr/bin/env python3
"""Generate daily sentiment rollup index under data/_index/."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from assign_ticker import load_active_tickers  # noqa: E402
from validate_report import DATA_DIR, parse_report_sentiment  # noqa: E402

INDEX_DIR = DATA_DIR / "_index"


def collect_day_reports(investigation_date: str) -> list[tuple[str, float | None]]:
    day_dir = DATA_DIR / investigation_date
    if not day_dir.is_dir():
        return []

    rows: list[tuple[str, float | None]] = []
    for report_path in sorted(day_dir.glob("*/report*.md")):
        if not (report_path.name == "report.md" or report_path.name.startswith("report.")):
            continue
        ticker = report_path.parent.name
        text = report_path.read_text(encoding="utf-8")
        score, _ = parse_report_sentiment(text)
        rows.append((ticker, score))
    return rows


def sentiment_label(score: float | None) -> str:
    if score is None:
        return "unknown"
    if score >= 0.25:
        return "bullish"
    if score <= -0.25:
        return "bearish"
    return "neutral"


def render_summary(investigation_date: str, rows: list[tuple[str, float | None]]) -> str:
    universe_size = len(load_active_tickers())
    scored = [(t, s) for t, s in rows if s is not None]
    coverage_pct = len(rows) / universe_size * 100 if universe_size else 0.0

    lines = [
        f"# Daily Sentiment Summary — {investigation_date}",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "## Overview",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Reports | {len(rows)} |",
        f"| Scored | {len(scored)} |",
        f"| Universe | {universe_size} |",
        f"| Coverage | {coverage_pct:.1f}% |",
    ]

    if scored:
        avg = sum(s for _, s in scored) / len(scored)
        bullish = sum(1 for _, s in scored if s >= 0.25)
        bearish = sum(1 for _, s in scored if s <= -0.25)
        neutral = len(scored) - bullish - bearish
        lines.extend(
            [
                f"| Avg sentiment | {avg:+.3f} |",
                f"| Bullish (≥0.25) | {bullish} |",
                f"| Neutral | {neutral} |",
                f"| Bearish (≤−0.25) | {bearish} |",
            ]
        )
    else:
        lines.append("| Avg sentiment | n/a |")

    lines.extend(["", "## Tickers", ""])
    if not rows:
        lines.append("_No reports for this date._")
    else:
        lines.extend(
            [
                "| Ticker | Score | Label |",
                "|--------|-------|-------|",
            ]
        )
        for ticker, score in sorted(rows, key=lambda item: (-(item[1] or -999), item[0])):
            score_str = f"{score:+.2f}" if score is not None else "n/a"
            lines.append(f"| {ticker} | {score_str} | {sentiment_label(score)} |")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build daily sentiment summary index.")
    parser.add_argument(
        "--date",
        help="Investigation date YYYY-MM-DD (default: today UTC)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Regenerate summaries for every date under data/",
    )
    args = parser.parse_args()

    dates: list[str]
    if args.all:
        if not DATA_DIR.is_dir():
            print("No data/ directory found.", file=sys.stderr)
            return 1
        dates = sorted(
            p.name
            for p in DATA_DIR.iterdir()
            if p.is_dir() and not p.name.startswith("_")
        )
    elif args.date:
        dates = [args.date]
    else:
        dates = [datetime.now(timezone.utc).date().isoformat()]

    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    for investigation_date in dates:
        rows = collect_day_reports(investigation_date)
        summary = render_summary(investigation_date, rows)
        out_path = INDEX_DIR / f"summary-{investigation_date}.md"
        out_path.write_text(summary, encoding="utf-8")
        print(f"Wrote {out_path.relative_to(REPO_ROOT)} ({len(rows)} reports)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
