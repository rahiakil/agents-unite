#!/usr/bin/env python3
"""Assign daily role: research, verify, consensus, or weekly patterns/findings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from assign_ticker import assign_ticker  # noqa: E402
from au_common import (  # noqa: E402
    CONSENSUS_CHANCE,
    FOCUS_ROLES,
    PR_OPEN_CHANCE,
    SECURITY_REVIEW_CHANCE,
    VERIFY_CHANCE,
    WEEKLY_ROLES,
    contributor_hash,
    contributor_id,
    find_consensus_target,
    find_verify_target,
    hash_fraction,
    is_maintainer,
    is_weekly_role_day,
    load_assignment_cache,
    load_yaml_config,
    make_branch_name,
    normalize_role,
    prompt_hash,
    prompt_path_for,
    resolve_investigation_date,
    save_assignment_cache,
)


def _roles_opt_in(cfg: dict) -> bool:
    if "roles_opt_in" in cfg:
        return bool(cfg["roles_opt_in"])
    return bool(cfg.get("verifier_opt_in", False))


def _pick_daily_role(seed_base: str, roles_opt_in: bool, contributor: str | None = None) -> str:
    if not roles_opt_in:
        return "research"
    roll = hash_fraction(f"{seed_base}:role")
    cutoff = 0.0
    cutoff += VERIFY_CHANCE
    if roll < cutoff:
        return "verify"
    cutoff += CONSENSUS_CHANCE
    if roll < cutoff:
        return "consensus"
    if is_maintainer(contributor):
        cutoff += PR_OPEN_CHANCE
        if roll < cutoff:
            return "pr_open"
        cutoff += SECURITY_REVIEW_CHANCE
        if roll < cutoff:
            return "security_review"
    return "research"


def _pick_weekly_role(seed_base: str) -> str:
    return "patterns" if hash_fraction(f"{seed_base}:weekly") < 0.5 else "findings"


def _report_slug(contributor: str) -> str:
    import re

    slug = re.sub(r"[^a-zA-Z0-9_-]", "-", contributor.lower()).strip("-")
    return slug[:64] or "anonymous"


def assign_role(
    investigation_date: str | None = None,
    contributor: str | None = None,
    *,
    date_mode: str | None = None,
    force_role: str | None = None,
    use_cache: bool = True,
) -> dict:
    cfg = load_yaml_config()
    cid = contributor_id(contributor)
    chash = contributor_hash(contributor)

    if investigation_date is None:
        investigation_date = resolve_investigation_date(date_mode)

    if use_cache and force_role is None:
        cached = load_assignment_cache(investigation_date, contributor)
        if cached:
            role = normalize_role(str(cached.get("daily_role", "research")))
            ticker = str(cached.get("ticker", "MARKET"))
            cached["daily_role"] = role
            cached["branch"] = make_branch_name(
                str(cached["date"]), ticker, str(cached.get("contributor_id", cid)), role=role
            )
            return cached

    roles_opt_in = _roles_opt_in(cfg)
    seed_base = f"{investigation_date}:{chash}"
    slug = _report_slug(cid)

    weekly = is_weekly_role_day(investigation_date, contributor)
    if force_role:
        daily_role = normalize_role(force_role)
        weekly = daily_role in WEEKLY_ROLES
    elif weekly:
        daily_role = _pick_weekly_role(seed_base)
    else:
        daily_role = _pick_daily_role(seed_base, roles_opt_in, contributor)

    focus = "full"
    ticker = "MARKET"
    assignment_date = investigation_date

    if daily_role == "research":
        focus_idx = int(hash_fraction(f"{seed_base}:focus") * len(FOCUS_ROLES)) % len(FOCUS_ROLES)
        focus = FOCUS_ROLES[focus_idx]
        ticker_assignment = assign_ticker(investigation_date, contributor, date_mode=date_mode)
        assignment_date = str(ticker_assignment["date"])
        ticker = str(ticker_assignment["ticker"])
        base_fields = {k: v for k, v in ticker_assignment.items() if k not in ("daily_role",)}
    elif daily_role == "consensus":
        target = find_consensus_target()
        if target:
            assignment_date, ticker = target
        else:
            ticker_assignment = assign_ticker(investigation_date, contributor, date_mode=date_mode)
            assignment_date = str(ticker_assignment["date"])
            ticker = str(ticker_assignment["ticker"])
        base_fields = {"date": assignment_date, "ticker": ticker, "contributor_id": cid, "contributor_hash": chash}
    elif daily_role == "verify":
        target = find_verify_target()
        if target:
            assignment_date, ticker = target
            base_fields = {"date": assignment_date, "ticker": ticker, "contributor_id": cid, "contributor_hash": chash}
        else:
            ticker_assignment = assign_ticker(investigation_date, contributor, date_mode=date_mode)
            assignment_date = str(ticker_assignment["date"])
            ticker = str(ticker_assignment["ticker"])
            base_fields = {k: v for k, v in ticker_assignment.items() if k not in ("daily_role",)}
        focus = "verify"
    elif daily_role in ("pr_open", "security_review"):
        cached = load_assignment_cache(investigation_date, contributor)
        if cached and cached.get("output_dir"):
            assignment_date = str(cached.get("date", investigation_date))
            ticker = str(cached.get("ticker", "MARKET"))
            base_fields = {
                "date": assignment_date,
                "ticker": ticker,
                "contributor_id": cid,
                "contributor_hash": chash,
            }
        else:
            ticker_assignment = assign_ticker(investigation_date, contributor, date_mode=date_mode)
            assignment_date = str(ticker_assignment["date"])
            ticker = str(ticker_assignment["ticker"])
            base_fields = {k: v for k, v in ticker_assignment.items() if k not in ("daily_role",)}
    elif daily_role == "summary_update":
        base_fields = {"date": investigation_date, "ticker": "INDEX", "contributor_id": cid, "contributor_hash": chash}
    elif daily_role == "patterns_hourly":
        base_fields = {"date": investigation_date, "ticker": "HOURLY", "contributor_id": cid, "contributor_hash": chash}
    elif daily_role in WEEKLY_ROLES:
        base_fields = {"date": investigation_date, "ticker": daily_role.upper(), "contributor_id": cid, "contributor_hash": chash}
    else:
        ticker_assignment = assign_ticker(investigation_date, contributor, date_mode=date_mode)
        assignment_date = str(ticker_assignment["date"])
        ticker = str(ticker_assignment["ticker"])
        base_fields = {k: v for k, v in ticker_assignment.items() if k not in ("daily_role",)}
        focus = "verify"

    prompt_file = prompt_path_for(daily_role, focus if daily_role == "research" else "default")
    phash = prompt_hash(prompt_file) if prompt_file.is_file() else None

    output_dir = _output_dir(daily_role, assignment_date, ticker)

    result = {
        **base_fields,
        "date": assignment_date,
        "ticker": ticker,
        "daily_role": daily_role,
        "focus": focus if daily_role == "research" else daily_role,
        "roles_opt_in": roles_opt_in,
        "verifier_opt_in": roles_opt_in,
        "is_weekly": daily_role in WEEKLY_ROLES,
        "prompt_file": str(prompt_file.relative_to(REPO_ROOT)),
        "prompt_hash": phash,
        "report_slug": slug,
        "report_filename": f"report.{slug}.md" if daily_role == "research" else None,
        "sources_filename": f"sources.{slug}.json" if daily_role == "research" else None,
        "verification_filename": f"verification.{slug}.md" if daily_role == "verify" else None,
        "consensus_filename": "consensus.md" if daily_role == "consensus" else None,
        "weekly_filename": (
            f"{daily_role}.{slug}.md" if daily_role in WEEKLY_ROLES else None
        ),
        "detail_level": cfg.get("detail_level", "standard"),
        "agent_runtime": cfg.get("agent_runtime", "manual"),
        "output_dir": output_dir,
        "branch": make_branch_name(assignment_date, ticker, cid, role=daily_role),
    }
    save_assignment_cache(result)
    return result


def _output_dir(role: str, investigation_date: str, ticker: str) -> str:
    if role == "patterns":
        return f"data/_patterns/{investigation_date}"
    if role == "findings":
        return f"data/_findings/{investigation_date}"
    if role == "summary_update":
        return f"data/_index"
    if role == "patterns_hourly":
        from datetime import datetime, timezone

        hour = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H")
        return f"data/_patterns/hourly/{hour}"
    if role == "security_review":
        return f"data/_index"
    if role in ("pr_open", "verify", "consensus", "research"):
        return f"data/{investigation_date}/{ticker}"
    return f"data/{investigation_date}/{ticker}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Assign daily role and focus.")
    parser.add_argument("--date")
    parser.add_argument("--date-mode", choices=["utc_midnight", "us_close"])
    parser.add_argument("--contributor")
    parser.add_argument(
        "--force-role",
        choices=[
            "research",
            "verify",
            "consensus",
            "pr_open",
            "security_review",
            "summary_update",
            "patterns_hourly",
            "patterns",
            "findings",
            "submitter",
            "verifier",
        ],
    )
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
