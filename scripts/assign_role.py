#!/usr/bin/env python3
"""Assign daily role: submitter vs verifier, and submitter focus."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from assign_ticker import assign_ticker  # noqa: E402
from au_common import (  # noqa: E402
    FOCUS_ROLES,
    contributor_hash,
    contributor_id,
    hash_fraction,
    load_yaml_config,
    prompt_hash,
    prompt_path_for,
    resolve_investigation_date,
)

VERIFIER_CHANCE = 0.25  # when opted in — user does not know until run


def assign_role(
    investigation_date: str | None = None,
    contributor: str | None = None,
    *,
    date_mode: str | None = None,
    force_role: str | None = None,
) -> dict:
    cfg = load_yaml_config()
    cid = contributor_id(contributor)
    chash = contributor_hash(contributor)

    if investigation_date is None:
        investigation_date = resolve_investigation_date(date_mode)

    verifier_opt_in = bool(cfg.get("verifier_opt_in", False))
    seed_base = f"{investigation_date}:{chash}"

    if force_role in ("submitter", "verifier"):
        daily_role = force_role
    elif verifier_opt_in:
        daily_role = "verifier" if hash_fraction(f"{seed_base}:role") < VERIFIER_CHANCE else "submitter"
    else:
        daily_role = "submitter"

    focus_seed = f"{seed_base}:focus"
    focus_idx = int(hash_fraction(focus_seed) * len(FOCUS_ROLES)) % len(FOCUS_ROLES)
    focus = FOCUS_ROLES[focus_idx]
    if daily_role == "verifier":
        focus = "verify"

    ticker_assignment = assign_ticker(investigation_date, contributor, date_mode=date_mode)

    prompt_file = prompt_path_for(daily_role, focus if daily_role == "submitter" else "default")
    phash = prompt_hash(prompt_file) if prompt_file.is_file() else None

    slug = _report_slug(cid)

    return {
        **ticker_assignment,
        "daily_role": daily_role,
        "focus": focus,
        "verifier_opt_in": verifier_opt_in,
        "prompt_file": str(prompt_file.relative_to(REPO_ROOT)),
        "prompt_hash": phash,
        "report_slug": slug,
        "report_filename": f"report.{slug}.md" if daily_role == "submitter" else None,
        "sources_filename": f"sources.{slug}.json" if daily_role == "submitter" else None,
        "consensus_filename": "consensus.md" if daily_role == "verifier" else None,
        "detail_level": cfg.get("detail_level", "standard"),
        "agent_runtime": cfg.get("agent_runtime", "manual"),
    }


def _report_slug(contributor: str) -> str:
    """Filesystem-safe slug from GitHub username."""
    import re

    slug = re.sub(r"[^a-zA-Z0-9_-]", "-", contributor.lower()).strip("-")
    return slug[:64] or "anonymous"


def main() -> int:
    parser = argparse.ArgumentParser(description="Assign daily role and focus.")
    parser.add_argument("--date")
    parser.add_argument("--date-mode", choices=["utc_midnight", "us_close"])
    parser.add_argument("--contributor")
    parser.add_argument("--force-role", choices=["submitter", "verifier"])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        result = assign_role(
            args.date,
            args.contributor,
            date_mode=args.date_mode,
            force_role=args.force_role,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['daily_role']}:{result['focus']}:{result['ticker']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
