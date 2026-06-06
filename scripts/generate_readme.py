#!/usr/bin/env python3
"""Regenerate live README sections from the sentiment dataset."""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
README_PATH = REPO_ROOT / "README.md"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from assign_ticker import load_active_tickers  # noqa: E402
from validate_report import DATA_DIR, parse_report_sentiment  # noqa: E402

MARKER_START = "<!-- LIVE:{name}:START -->"
MARKER_END = "<!-- LIVE:{name}:END -->"


def discover_reports() -> list[tuple[str, str, float | None]]:
    rows: list[tuple[str, str, float | None]] = []
    if not DATA_DIR.is_dir():
        return rows
    for report_path in sorted(DATA_DIR.glob("*/*/report*.md")):
        if report_path.parent.parent.name.startswith("_"):
            continue
        if not (report_path.name == "report.md" or report_path.name.startswith("report.")):
            continue
        date = report_path.parent.parent.name
        ticker = report_path.parent.name
        text = report_path.read_text(encoding="utf-8")
        score, _ = parse_report_sentiment(text)
        rows.append((date, ticker, score))
    return rows


def sentiment_label(score: float | None) -> str:
    if score is None:
        return "—"
    if score >= 0.25:
        return "🟢 bullish"
    if score <= -0.25:
        return "🔴 bearish"
    return "🟡 neutral"


def coverage_bar(pct: float, width: int = 24) -> str:
    if pct <= 0:
        filled = 0
    else:
        filled = min(width, max(1, int(round(pct / 100 * width))))
    return f"[{'█' * filled}{'░' * (width - filled)}] {pct:.1f}%"


def render_header_stats(reports: list[tuple[str, str, float | None]], universe: int) -> str:
    dates = sorted({d for d, _, _ in reports})
    tickers = {t for _, t, _ in reports}
    scored = [s for _, _, s in reports if s is not None]
    latest = dates[-1] if dates else None
    latest_count = sum(1 for d, _, _ in reports if d == latest) if latest else 0
    latest_cov = latest_count / universe * 100 if universe and latest else 0.0
    avg = sum(scored) / len(scored) if scored else 0.0

    return "\n".join(
        [
            "| Reports | Tickers | Universe | Latest day | Coverage | Avg sentiment |",
            "|---------|---------|----------|------------|----------|---------------|",
            f"| **{len(reports)}** | **{len(tickers)}** | **{universe}** | "
            f"**{latest or '—'}** | **{latest_cov:.1f}%** | **{avg:+.3f}** |",
        ]
    )


def render_market_pulse(reports: list[tuple[str, str, float | None]]) -> str:
    if not reports:
        return "_No reports yet — be the first contributor._"

    dates = sorted({d for d, _, _ in reports})
    latest = dates[-1]
    day_rows = sorted(
        [(t, s) for d, t, s in reports if d == latest],
        key=lambda item: item[1] if item[1] is not None else -999,
        reverse=True,
    )

    lines = [
        f"**Latest pulse — {latest}** · updated automatically on every push",
        "",
        "| Ticker | Score | Mood |",
        "|--------|-------|------|",
    ]
    for ticker, score in day_rows[:12]:
        score_txt = f"{score:+.2f}" if score is not None else "n/a"
        lines.append(f"| `{ticker}` | {score_txt} | {sentiment_label(score)} |")

    if len(day_rows) > 12:
        lines.append(f"| _+{len(day_rows) - 12} more_ | | |")

    return "\n".join(lines)


def render_coverage(reports: list[tuple[str, str, float | None]], universe: int) -> str:
    if not reports or not universe:
        return "_Coverage tracking starts with the first report._"

    by_date: dict[str, set[str]] = defaultdict(set)
    for date, ticker, _ in reports:
        by_date[date].append(ticker) if False else by_date[date].add(ticker)

    dates = sorted(by_date)
    latest = dates[-1]
    latest_cov = len(by_date[latest]) / universe * 100
    total_cov = len({t for _, t, _ in reports}) / universe * 100

    lines = [
        f"**Universe progress** — {len({t for _, t, _ in reports})} / {universe} tickers ever covered",
        "",
        f"Today ({latest}): {coverage_bar(latest_cov)}",
        f"All-time:       {coverage_bar(total_cov)}",
        "",
        "| Date | Reports | Coverage | Avg sentiment |",
        "|------|---------|----------|---------------|",
    ]

    for date in dates[-7:]:
        tickers = by_date[date]
        day_scores = [s for d, _, s in reports if d == date and s is not None]
        cov = len(tickers) / universe * 100
        avg = sum(day_scores) / len(day_scores) if day_scores else None
        avg_txt = f"{avg:+.3f}" if avg is not None else "n/a"
        lines.append(f"| {date} | {len(tickers)} | {cov:.1f}% | {avg_txt} |")

    return "\n".join(lines)


def render_footer_stamp() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"_Live sections last regenerated: **{ts}** · [`scripts/generate_readme.py`](scripts/generate_readme.py)_"


def build_sections() -> dict[str, str]:
    reports = discover_reports()
    universe = len(load_active_tickers())
    return {
        "HEADER_STATS": render_header_stats(reports, universe),
        "MARKET_PULSE": render_market_pulse(reports),
        "COVERAGE": render_coverage(reports, universe),
        "FOOTER_STAMP": render_footer_stamp(),
    }


def patch_readme(text: str, sections: dict[str, str]) -> str:
    for name, body in sections.items():
        pattern = re.compile(
            re.escape(MARKER_START.format(name=name))
            + r".*?"
            + re.escape(MARKER_END.format(name=name)),
            re.DOTALL,
        )
        replacement = (
            f"{MARKER_START.format(name=name)}\n{body}\n{MARKER_END.format(name=name)}"
        )
        if not pattern.search(text):
            raise ValueError(f"Missing README markers for LIVE:{name}")
        text = pattern.sub(replacement, text, count=1)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate live README.md sections.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if README would change (for CI drift detection)",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print generated sections instead of patching README",
    )
    args = parser.parse_args()

    sections = build_sections()

    if args.stdout:
        for name, body in sections.items():
            print(f"=== LIVE:{name} ===")
            print(body)
            print()
        return 0

    if not README_PATH.is_file():
        print(f"error: README not found at {README_PATH}", file=sys.stderr)
        return 1

    original = README_PATH.read_text(encoding="utf-8")
    updated = patch_readme(original, sections)

    if args.check:
        if updated != original:
            print("README live sections are stale; run scripts/generate_readme.py", file=sys.stderr)
            return 1
        print("README live sections are up to date.")
        return 0

    if updated != original:
        README_PATH.write_text(updated, encoding="utf-8")
        print(f"Updated live sections in {README_PATH.relative_to(REPO_ROOT)}")
    else:
        print("README live sections already current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
