#!/usr/bin/env python3
"""Track and prompt wiki ingestion of raw data/ reports."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
DATA_DIR = REPO_ROOT / "data"
STATE_PATH = WIKI_DIR / ".ingest-state.json"
INGEST_TEMPLATE = REPO_ROOT / "agents" / "wiki-ingest.md"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from validate_report import parse_report_sentiment  # noqa: E402


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_state() -> dict:
    if not STATE_PATH.is_file():
        return {"ingested": {}}
    with STATE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def discover_reports() -> list[dict]:
    reports: list[dict] = []
    if not DATA_DIR.is_dir():
        return reports
    for report_path in sorted(DATA_DIR.glob("*/*/report*.md")):
        day = report_path.parent.parent.name
        if day.startswith("_"):
            continue
        if not (report_path.name == "report.md" or report_path.name.startswith("report.")):
            continue
        ticker = report_path.parent.name
        text = report_path.read_text(encoding="utf-8")
        score, _ = parse_report_sentiment(text)
        rel = report_path.relative_to(REPO_ROOT)
        reports.append(
            {
                "date": day,
                "ticker": ticker,
                "path": str(rel),
                "dir": str(report_path.parent.relative_to(REPO_ROOT)),
                "hash": file_hash(report_path),
                "sentiment": score,
            }
        )
    return reports


def pending_reports(state: dict) -> list[dict]:
    ingested = state.get("ingested", {})
    pending: list[dict] = []
    for report in discover_reports():
        key = f"{report['date']}/{report['ticker']}"
        prev = ingested.get(key)
        if prev is None or prev.get("hash") != report["hash"]:
            pending.append(report)
    return pending


def render_prompt(report: dict) -> str:
    template = INGEST_TEMPLATE.read_text(encoding="utf-8")
    today = datetime.now(timezone.utc).date().isoformat()
    sentiment = report["sentiment"]
    sentiment_str = f"{sentiment:+.2f}" if sentiment is not None else "n/a"
    replacements = {
        "{{SOURCE_TYPE}}": "data/report",
        "{{SOURCE_PATH}}": report["path"],
        "{{TICKER}}": report["ticker"],
        "{{DATE}}": report["date"],
        "{{SENTIMENT}}": sentiment_str,
        "{{TODAY}}": today,
    }
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return rendered


def mark_done(date: str, ticker: str) -> int:
    report_path = DATA_DIR / date / ticker / "report.md"
    if not report_path.is_file():
        print(f"error: report not found: {report_path}", file=sys.stderr)
        return 1
    state = load_state()
    key = f"{date}/{ticker}"
    state.setdefault("ingested", {})[key] = {
        "hash": file_hash(report_path),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "path": str(report_path.relative_to(REPO_ROOT)),
    }
    save_state(state)
    print(f"Marked ingested: {key}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Wiki ingest tracker for agents-unite.")
    parser.add_argument("--json", action="store_true", help="Output pending as JSON")
    parser.add_argument("--prompt", action="store_true", help="Print ingest prompt for next pending")
    parser.add_argument("--mark-done", nargs=2, metavar=("DATE", "TICKER"), help="Mark report ingested")
    args = parser.parse_args()

    if args.mark_done:
        return mark_done(args.mark_done[0], args.mark_done[1])

    state = load_state()
    pending = pending_reports(state)
    all_reports = discover_reports()

    if args.json:
        print(json.dumps({"pending": pending, "total": len(all_reports)}, indent=2))
        return 0

    if args.prompt:
        if not pending:
            print("No pending reports to ingest.")
            return 0
        print(render_prompt(pending[0]))
        if len(pending) > 1:
            print(f"\n---\n({len(pending) - 1} more pending)", file=sys.stderr)
        return 0

    print(f"Reports in data/: {len(all_reports)}")
    print(f"Pending wiki ingest: {len(pending)}")
    if pending:
        print("\nPending:")
        for r in pending:
            s = f"{r['sentiment']:+.2f}" if r["sentiment"] is not None else "n/a"
            print(f"  {r['date']}/{r['ticker']}  sentiment={s}  {r['path']}")
        print("\nNext: python3 scripts/wiki_ingest.py --prompt")
    else:
        print("Wiki is up to date with data/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
