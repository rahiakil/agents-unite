#!/usr/bin/env python3
"""Load agents-unite reports for algo / RAG / backtest pipelines."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA = REPO_ROOT / "data"

SCORE_RE = re.compile(r"^sentiment_score:\s*(-?\d+(?:\.\d+)?)", re.MULTILINE)


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def load_reports(
    *,
    ticker: str | None = None,
    since: str | None = None,
    until: str | None = None,
    last_n_days: int | None = None,
) -> list[dict]:
    rows: list[dict] = []
    if not DATA.is_dir():
        return rows

    since_d = datetime.strptime(since, "%Y-%m-%d").date() if since else None
    until_d = datetime.strptime(until, "%Y-%m-%d").date() if until else None

    for report_path in sorted(DATA.glob("*/*/report*.md")):
        day_s = report_path.parent.parent.name
        tick = report_path.parent.name
        if day_s.startswith("_") or tick.startswith("_"):
            continue
        if ticker and tick.upper() != ticker.upper():
            continue
        try:
            day = date.fromisoformat(day_s)
        except ValueError:
            continue
        if since_d and day < since_d:
            continue
        if until_d and day > until_d:
            continue

        text = report_path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        score = fm.get("sentiment_score")
        if score is None:
            m = SCORE_RE.search(text)
            score = m.group(1) if m else None

        sources_path = report_path.parent / report_path.name.replace("report", "sources", 1).replace(".md", ".json")
        if not sources_path.is_file():
            sources_path = report_path.parent / "sources.json"
        sources_count = 0
        if sources_path.is_file():
            try:
                sources_count = len(json.loads(sources_path.read_text()).get("sources", []))
            except json.JSONDecodeError:
                pass

        rows.append(
            {
                "date": day_s,
                "ticker": tick.upper(),
                "path": str(report_path.relative_to(REPO_ROOT)),
                "sentiment_score": float(score) if score is not None else None,
                "github_username": fm.get("github_username"),
                "focus": fm.get("focus"),
                "prompt_hash": fm.get("prompt_hash"),
                "sources_count": sources_count,
            }
        )

    rows.sort(key=lambda r: (r["date"], r["ticker"]))
    if last_n_days and rows:
        dates = sorted({r["date"] for r in rows})
        cutoff = dates[-last_n_days] if len(dates) > last_n_days else dates[0]
        rows = [r for r in rows if r["date"] >= cutoff]
    return rows


def main() -> int:
    p = argparse.ArgumentParser(description="Export agents-unite reports for builders.")
    p.add_argument("--ticker")
    p.add_argument("--since")
    p.add_argument("--until")
    p.add_argument("--last", type=int, dest="last_n_days")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    rows = load_reports(
        ticker=args.ticker,
        since=args.since,
        until=args.until,
        last_n_days=args.last_n_days,
    )
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        for r in rows:
            s = f"{r['sentiment_score']:+.2f}" if r["sentiment_score"] is not None else "n/a"
            print(f"{r['date']} {r['ticker']:6} score={s} sources={r['sources_count']} {r['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
