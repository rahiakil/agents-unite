#!/usr/bin/env python3
"""Shared utilities for agents-unite scripts."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / ".agents-unite" / "config.yaml"
UNIVERSE_PATH = REPO_ROOT / "tickers" / "universe.json"
DATA_DIR = REPO_ROOT / "data"
AGENTS_DIR = REPO_ROOT / "agents"
ASSIGNMENT_CACHE = REPO_ROOT / ".agents-unite"

FOCUS_ROLES = ("sentiment", "news", "social", "trading", "full")
DAILY_ROLES = ("research", "verify", "consensus", "pr_open", "security_review")
OPS_ROLES = ("summary_update", "patterns_hourly")
WEEKLY_ROLES = ("patterns", "findings")
DATE_MODES = ("utc_midnight", "us_close")
DETAIL_LEVELS = ("minimal", "standard", "deep")
DEFAULT_MAINTAINERS = ("rahiakil",)

# Role lottery when roles_opt_in / verifier_opt_in (see assign_role.py)
VERIFY_CHANCE = 0.18
CONSENSUS_CHANCE = 0.12  # cumulative after verify band
PR_OPEN_CHANCE = 0.08  # cumulative; maintainer nodes only
SECURITY_REVIEW_CHANCE = 0.05  # cumulative; maintainer nodes only

PROMPT_FILES = {
    "research": {
        "sentiment": "investigation-sentiment.md",
        "news": "investigation-news.md",
        "social": "investigation-social.md",
        "trading": "investigation-trading.md",
        "full": "investigation.md",
    },
    "submitter": {  # legacy alias
        "sentiment": "investigation-sentiment.md",
        "news": "investigation-news.md",
        "social": "investigation-social.md",
        "trading": "investigation-trading.md",
        "full": "investigation.md",
    },
    "verify": {"default": "verify-report.md"},
    "verifier": {"default": "verify-report.md"},
    "consensus": {"default": "consensus-run.md"},
    "patterns": {"default": "patterns-weekly.md"},
    "findings": {"default": "findings-weekly.md"},
    "pr_open": {"default": "pr-open.md"},
    "security_review": {"default": "security-review.md"},
    "summary_update": {"default": "summary-update.md"},
    "patterns_hourly": {"default": "patterns-hourly.md"},
}


def load_yaml_config() -> dict:
    """Load .agents-unite/config.yaml if present."""
    path = CONFIG_PATH
    if not path.is_file():
        return {}
    try:
        import yaml  # type: ignore
    except ImportError:
        return _parse_simple_yaml(path.read_text(encoding="utf-8"))
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def _parse_simple_yaml(text: str) -> dict:
    """Minimal YAML subset when PyYAML unavailable."""
    cfg: dict = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        val = val.strip().strip("'\"")
        if val.lower() in ("true", "false"):
            cfg[key.strip()] = val.lower() == "true"
        else:
            cfg[key.strip()] = val
    return cfg


def github_username() -> str | None:
    cfg = load_yaml_config()
    user = cfg.get("github_username") or os.environ.get("AGENTS_UNITE_GITHUB_USER")
    if user:
        return str(user).strip()
    try:
        result = subprocess.run(
            ["gh", "api", "user", "-q", ".login"],
            capture_output=True,
            text=True,
            check=False,
            cwd=REPO_ROOT,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except OSError:
        pass
    return None


def contributor_id(explicit: str | None = None) -> str:
    """Stable contributor id — GitHub username preferred for reputation."""
    cfg = load_yaml_config()
    raw = (
        explicit
        or os.environ.get("AGENTS_UNITE_CONTRIBUTOR")
        or cfg.get("contributor_id")
        or github_username()
        or _git_user_email()
        or "anonymous"
    )
    return str(raw).strip()


def contributor_hash(identifier: str | None = None) -> str:
    return hashlib.sha256(contributor_id(identifier).lower().encode("utf-8")).hexdigest()


def _git_user_email() -> str | None:
    try:
        result = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True,
            text=True,
            check=False,
            cwd=REPO_ROOT,
        )
    except OSError:
        return None
    email = result.stdout.strip()
    return email or None


def resolve_investigation_date(mode: str | None = None, now: datetime | None = None) -> str:
    """
    Resolve folder date for reports.

    - utc_midnight: calendar date in UTC
    - us_close: US equity session date (America/New_York) — user-configurable wake-up alignment
    """
    cfg = load_yaml_config()
    mode = mode or cfg.get("date_mode") or os.environ.get("AGENTS_UNITE_DATE_MODE") or "utc_midnight"
    if mode not in DATE_MODES:
        raise ValueError(f"date_mode must be one of {DATE_MODES}, got {mode!r}")

    if now is None:
        now = datetime.now(timezone.utc)

    if mode == "utc_midnight":
        return now.astimezone(timezone.utc).date().isoformat()

    return now.astimezone(ZoneInfo("America/New_York")).date().isoformat()


def load_active_tickers(universe_path: Path = UNIVERSE_PATH) -> list[str]:
    with universe_path.open(encoding="utf-8") as f:
        data = json.load(f)
    tickers = sorted(
        {
            entry["ticker"].upper()
            for entry in data["tickers"]
            if entry.get("active", True)
        }
    )
    if not tickers:
        raise ValueError(f"No active tickers in {universe_path}")
    return tickers


def _is_committed_report(report_path: Path) -> bool:
    """Count only substantive reports toward coverage (ignore empty scaffolds)."""
    if not report_path.is_file():
        return False
    text = report_path.read_text(encoding="utf-8")
    if len(text.strip()) < 400:
        return False
    if "contributor_hash: null" in text or "sentiment_score: 0.0" in text.split("---", 2)[1] if text.startswith("---") else False:
        # Still default scaffold
        if text.count("\n") < 25:
            return False
    return True


def coverage_counts(investigation_date: str) -> dict[str, int]:
    """Count substantive report files per ticker for a given date folder."""
    counts: dict[str, int] = {}
    day_dir = DATA_DIR / investigation_date
    if not day_dir.is_dir():
        return counts
    for ticker_dir in day_dir.iterdir():
        if not ticker_dir.is_dir() or ticker_dir.name.startswith("_"):
            continue
        n = sum(
            1
            for p in ticker_dir.glob("report*.md")
            if p.name == "report.md" or p.name.startswith("report.")
            if _is_committed_report(p)
        )
        if n:
            counts[ticker_dir.name.upper()] = n
    return counts


def hash_fraction(seed: str) -> float:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return int(digest, 16) / (2**256)


def weighted_pick(items: list[str], weights: list[float], seed: str) -> tuple[str, int]:
    if len(items) != len(weights):
        raise ValueError("items and weights length mismatch")
    total = sum(weights)
    if total <= 0:
        idx = int(hash_fraction(seed) * len(items)) % len(items)
        return items[idx], idx
    target = hash_fraction(seed) * total
    upto = 0.0
    for i, (item, w) in enumerate(zip(items, weights)):
        upto += w
        if target <= upto:
            return item, i
    return items[-1], len(items) - 1


def normalize_role(role: str) -> str:
    """Map legacy role names to current vocabulary."""
    aliases = {"submitter": "research", "verifier": "verify"}
    return aliases.get(role, role)


def is_weekly_role_day(investigation_date: str, contributor: str | None = None) -> bool:
    """Each contributor gets a weekly role every 7 days (hash-staggered)."""
    cid = contributor_id(contributor)
    chash = contributor_hash(contributor)
    try:
        y, m, d = (int(x) for x in investigation_date.split("-"))
        day_index = date(y, m, d).toordinal()
    except ValueError:
        return False
    offset = int(hash_fraction(f"{cid}:{chash}:week") * 7)
    return (day_index + offset) % 7 == 0


def maintainer_usernames() -> set[str]:
    cfg = load_yaml_config()
    raw = cfg.get("maintainers") or DEFAULT_MAINTAINERS
    if isinstance(raw, str):
        raw = [raw]
    return {str(u).strip().lower() for u in raw if str(u).strip()}


def is_maintainer(contributor: str | None = None) -> bool:
    return contributor_id(contributor).lower() in maintainer_usernames()


def find_verify_target() -> tuple[str, str] | None:
    """Pick date/ticker with reports but no verification yet (backlog scan)."""
    candidates: list[tuple[int, str, str]] = []
    if not DATA_DIR.is_dir():
        return None
    for ticker_dir in sorted(DATA_DIR.glob("*/*/")):
        if not ticker_dir.is_dir():
            continue
        day = ticker_dir.parent.name
        ticker = ticker_dir.name
        if day.startswith("_") or ticker.startswith("_"):
            continue
        reports = [p for p in ticker_dir.glob("report*.md") if p.name == "report.md" or p.name.startswith("report.")]
        if not reports:
            continue
        verifications = list(ticker_dir.glob("verification*.md"))
        if verifications:
            continue
        candidates.append((len(reports), day, ticker))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    _, day, ticker = candidates[0]
    return day, ticker


def find_consensus_target() -> tuple[str, str] | None:
    """Pick date/ticker with reports + verifications ready for consensus."""
    candidates: list[tuple[int, str, str]] = []
    if not DATA_DIR.is_dir():
        return None
    for ticker_dir in sorted(DATA_DIR.glob("*/*/")):
        if not ticker_dir.is_dir():
            continue
        day = ticker_dir.parent.name
        ticker = ticker_dir.name
        if day.startswith("_") or ticker.startswith("_"):
            continue
        reports = [p for p in ticker_dir.glob("report*.md") if p.name == "report.md" or p.name.startswith("report.")]
        verifications = list(ticker_dir.glob("verification*.md"))
        consensus = ticker_dir / "consensus.md"
        if len(reports) < 1 or len(verifications) < 1:
            continue
        if consensus.is_file() and len(consensus.read_text(encoding="utf-8").strip()) > 400:
            continue
        candidates.append((len(reports) + len(verifications), day, ticker))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    _, day, ticker = candidates[0]
    return day, ticker


def prompt_path_for(role: str, focus: str) -> Path:
    role = normalize_role(role)
    if role in (
        "verify",
        "consensus",
        "patterns",
        "findings",
        "pr_open",
        "security_review",
        "summary_update",
        "patterns_hourly",
    ):
        key = "default"
        bucket = role if role in PROMPT_FILES else "verify"
        name = PROMPT_FILES[bucket][key]
    else:
        bucket = "research" if role == "research" else role
        name = PROMPT_FILES.get(bucket, PROMPT_FILES["research"]).get(
            focus, PROMPT_FILES["research"]["full"]
        )
    return AGENTS_DIR / name


def make_branch_name(
    investigation_date: str,
    ticker: str,
    contributor: str | None = None,
    *,
    role: str = "research",
) -> str:
    """Unique branch: report/… for ticker roles, weekly/… for patterns/findings."""
    cid = contributor_id(contributor)
    user_hash = hashlib.sha256(cid.lower().encode("utf-8")).hexdigest()[:8]
    role = normalize_role(role)
    if role in WEEKLY_ROLES:
        return f"weekly/{role}/{investigation_date}-{user_hash}"
    if role == "summary_update":
        return f"ops/summary/{investigation_date}-{user_hash}"
    if role == "patterns_hourly":
        hour = datetime.now(timezone.utc).strftime("%H")
        return f"hourly/patterns/{investigation_date}-{hour}-{user_hash}"
    if role == "security_review":
        return f"ops/security/{investigation_date}-{user_hash}"
    if role == "pr_open":
        safe_ticker = ticker.upper().replace(".", "-")
        return f"report/{investigation_date}-{safe_ticker}-{user_hash}"
    safe_ticker = ticker.upper().replace(".", "-")
    return f"report/{investigation_date}-{safe_ticker}-{user_hash}"


def prompt_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def assignment_cache_path(investigation_date: str, contributor: str | None = None) -> Path:
    cid = contributor_id(contributor)
    slug = hashlib.sha256(cid.lower().encode()).hexdigest()[:8]
    return ASSIGNMENT_CACHE / f"assignment-{investigation_date}-{slug}.json"


def load_assignment_cache(investigation_date: str, contributor: str | None = None) -> dict | None:
    path = assignment_cache_path(investigation_date, contributor)
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else None


def save_assignment_cache(assignment: dict) -> None:
    ASSIGNMENT_CACHE.mkdir(parents=True, exist_ok=True)
    path = assignment_cache_path(str(assignment["date"]), str(assignment.get("contributor_id")))
    with path.open("w", encoding="utf-8") as f:
        json.dump(assignment, f, indent=2)
        f.write("\n")
