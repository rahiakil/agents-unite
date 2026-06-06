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
from au_common import contributor_id, load_assignment_cache, prompt_hash, save_assignment_cache  # noqa: E402


PROSE_STYLE_PATH = REPO_ROOT / "agents" / "prose-style.md"


def append_prose_style(prompt: str) -> str:
    """Append anti-slop writing rules to every investigation prompt."""
    if not PROSE_STYLE_PATH.is_file():
        return prompt
    style = PROSE_STYLE_PATH.read_text(encoding="utf-8").strip()
    return f"{prompt.rstrip()}\n\n---\n\n{style}\n"


def render_prompt(template: str, assignment: dict, paths: dict) -> str:
    replacements = {
        "{{TICKER}}": assignment["ticker"],
        "{{DATE}}": assignment["date"],
        "{{OUTPUT_DIR}}": paths["output_dir"],
        "{{REPORT_PATH}}": paths.get("report_path", ""),
        "{{SOURCES_PATH}}": paths.get("sources_path", ""),
        "{{CONSENSUS_PATH}}": paths.get("consensus_path", ""),
        "{{VERIFICATION_PATH}}": paths.get("verification_path", ""),
        "{{WEEKLY_PATH}}": paths.get("weekly_path", ""),
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
    role = assignment.get("daily_role", "research")
    out_dir = assignment.get("output_dir") or f"data/{assignment['date']}/{assignment['ticker']}"
    out: dict[str, str] = {"output_dir": out_dir}

    if role == "research":
        base = Path(out_dir)
        out["report_path"] = str(base / assignment["report_filename"])
        out["sources_path"] = str(base / assignment["sources_filename"])
    elif role == "verify":
        base = Path(out_dir)
        out["verification_path"] = str(base / assignment["verification_filename"])
    elif role == "consensus":
        base = Path(out_dir)
        out["consensus_path"] = str(base / assignment["consensus_filename"])
    elif role in ("patterns", "findings"):
        base = Path(out_dir)
        out["weekly_path"] = str(base / assignment["weekly_filename"])

    return out


def ensure_output_dir(assignment: dict, dry_run: bool) -> Path:
    out = assignment.get("output_dir") or f"data/{assignment['date']}/{assignment['ticker']}"
    output_dir = REPO_ROOT / out
    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def write_scaffold(assignment: dict, output_dir: Path) -> None:
    role = assignment.get("daily_role", "research")
    slug = assignment.get("report_slug", "anonymous")

    if role == "verify":
        vpath = output_dir / assignment["verification_filename"]
        if not vpath.exists():
            vpath.write_text(
                f"""---
ticker: {assignment['ticker']}
date: {assignment['date']}
github_username: {assignment.get('contributor_id', 'anonymous')}
daily_role: verify
prompt_hash: {assignment.get('prompt_hash', '')}
prompt_file: {assignment.get('prompt_file', '')}
verdict: needs_revision
reports_reviewed: 0
sources_audited: 0
confidence: low
---

# Summary

Pending verification.

# Reports reviewed

# Source audit

# Issues found

# Verdict rationale
""",
                encoding="utf-8",
            )
        return

    if role == "consensus":
        consensus = output_dir / "consensus.md"
        if not consensus.exists():
            consensus.write_text(
                f"""---
ticker: {assignment['ticker']}
date: {assignment['date']}
github_username: {assignment.get('contributor_id', 'anonymous')}
daily_role: consensus
prompt_hash: {assignment.get('prompt_hash', '')}
consensus_score: 0.0
confidence: low
reports_reviewed: 0
verifications_reviewed: 0
method: weighted_median
---

# Summary

Pending consensus.

# Consensus Score

# Agreement

# Divergence

# Source coverage

# Price snapshot

# Notable events
""",
                encoding="utf-8",
            )
        return

    if role in ("patterns", "findings"):
        wpath = output_dir / assignment["weekly_filename"]
        if not wpath.exists():
            wpath.write_text(
                f"""---
type: weekly_{role}
date: {assignment['date']}
github_username: {assignment.get('contributor_id', 'anonymous')}
daily_role: {role}
prompt_hash: {assignment.get('prompt_hash', '')}
---

# Summary

Pending weekly {role} scan.
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
daily_role: research
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

    if not args.dry_run:
        save_assignment_cache({**assignment, **paths})

    if args.scaffold and not args.dry_run:
        write_scaffold(assignment, output_dir)

    prompt = append_prose_style(render_prompt(template, assignment, paths))

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
