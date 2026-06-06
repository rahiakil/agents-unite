#!/usr/bin/env python3
"""Main entry: assign role, ticker, render agent prompt, scaffold files."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from assign_role import assign_role  # noqa: E402
from au_common import contributor_id, prompt_hash  # noqa: E402


def render_prompt(template: str, assignment: dict, paths: dict) -> str:
    replacements = {
        "{{TICKER}}": assignment["ticker"],
        "{{DATE}}": assignment["date"],
        "{{OUTPUT_DIR}}": paths["output_dir"],
        "{{REPORT_PATH}}": paths.get("report_path", ""),
        "{{SOURCES_PATH}}": paths.get("sources_path", ""),
        "{{CONSENSUS_PATH}}": paths.get("consensus_path", ""),
        "{{CONTRIBUTOR_HASH}}": assignment["contributor_hash"][:12],
        "{{GITHUB_USER}}": assignment.get("contributor_id") or "anonymous",
        "{{PROMPT_HASH}}": assignment.get("prompt_hash") or "",
        "{{DETAIL_LEVEL}}": assignment.get("detail_level", "standard"),
    }
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return rendered


def build_paths(assignment: dict) -> dict[str, str]:
    base = Path("data") / assignment["date"] / assignment["ticker"]
    out: dict[str, str] = {"output_dir": str(base)}

    if assignment["daily_role"] == "submitter":
        out["report_path"] = str(base / assignment["report_filename"])
        out["sources_path"] = str(base / assignment["sources_filename"])
    else:
        out["consensus_path"] = str(base / assignment["consensus_filename"])

    return out


def ensure_output_dir(assignment: dict, dry_run: bool) -> Path:
    output_dir = REPO_ROOT / "data" / assignment["date"] / assignment["ticker"]
    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def write_scaffold(assignment: dict, output_dir: Path) -> None:
    if assignment["daily_role"] == "verifier":
        consensus = output_dir / "consensus.md"
        if not consensus.exists():
            consensus.write_text(
                f"""---
ticker: {assignment['ticker']}
date: {assignment['date']}
github_username: {assignment.get('contributor_id', 'anonymous')}
daily_role: verifier
prompt_hash: {assignment.get('prompt_hash', '')}
consensus_score: 0.0
confidence: low
reports_reviewed: 0
---

# Summary

Pending verification.

# Consensus Score

# Agreement

# Disagreements

# Source audit

# Rejected claims
""",
                encoding="utf-8",
            )
        return

    report_path = output_dir / assignment["report_filename"]
    sources_path = output_dir / assignment["sources_filename"]

    if not report_path.exists():
        report_path.write_text(
            f"""---
ticker: {assignment['ticker']}
date: {assignment['date']}
github_username: {assignment.get('contributor_id', 'anonymous')}
contributor_hash: {assignment['contributor_hash'][:12]}
daily_role: submitter
focus: {assignment['focus']}
prompt_hash: {assignment.get('prompt_hash', '')}
prompt_file: {assignment.get('prompt_file', '')}
sentiment_score: 0.0
detail_level: {assignment.get('detail_level', 'standard')}
---

# Sentiment

Sentiment score: 0.0

# Key Themes

- 

# Sources

# Price Snapshot

| Field | Value |
|-------|-------|
| Price | |
| Change % | |

# Notable Events

- None identified
""",
            encoding="utf-8",
        )

    if not sources_path.exists():
        sources_path.write_text(
            json.dumps(
                {
                    "ticker": assignment["ticker"],
                    "date": assignment["date"],
                    "github_username": assignment.get("contributor_id"),
                    "focus": assignment["focus"],
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                    "sources": [],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Assign role/ticker and emit agent prompt.")
    parser.add_argument("--date")
    parser.add_argument("--date-mode", choices=["utc_midnight", "us_close"])
    parser.add_argument("--contributor")
    parser.add_argument("--force-role", choices=["submitter", "verifier"])
    parser.add_argument("--scaffold", action="store_true")
    parser.add_argument("--metadata", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        assignment = assign_role(
            args.date,
            args.contributor,
            date_mode=args.date_mode,
            force_role=args.force_role,
        )
        prompt_file = REPO_ROOT / assignment["prompt_file"]
        template = prompt_file.read_text(encoding="utf-8")
        # Verify hash matches
        expected = prompt_hash(prompt_file)
        if assignment.get("prompt_hash") and assignment["prompt_hash"] != expected:
            print("warning: prompt hash drift detected", file=sys.stderr)
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    paths = build_paths(assignment)
    output_dir = ensure_output_dir(assignment, args.dry_run)

    if args.scaffold and not args.dry_run:
        write_scaffold(assignment, output_dir)

    prompt = render_prompt(template, assignment, paths)

    if args.metadata:
        meta = {**assignment, **paths}
        print(json.dumps(meta, indent=2))
        print("\n--- PROMPT ---\n")

    print(prompt)

    if not args.dry_run:
        print(
            f"\n---\nRole: {assignment['daily_role']} / {assignment['focus']}\n"
            f"Next: python3 scripts/validate_report.py {paths['output_dir']}/",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
