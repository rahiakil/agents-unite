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

FOCUS_ROLES = ("sentiment", "news", "social", "trading", "full")
DATE_MODES = ("utc_midnight", "us_close")
DETAIL_LEVELS = ("minimal", "standard", "deep")

PROMPT_FILES = {
    "submitter": {
        "sentiment": "investigation-sentiment.md",
        "news": "investigation-news.md",
        "social": "investigation-social.md",
        "trading": "investigation-trading.md",
        "full": "investigation.md",
    },
    "verifier": {
        "default": "verify-report.md",
    },
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


def coverage_counts(investigation_date: str) -> dict[str, int]:
    """Count report files per ticker for a given date folder."""
    counts: dict[str, int] = {}
    day_dir = DATA_DIR / investigation_date
    if not day_dir.is_dir():
        return counts
    for ticker_dir in day_dir.iterdir():
        if not ticker_dir.is_dir() or ticker_dir.name.startswith("_"):
            continue
        n = len([p for p in ticker_dir.glob("report*.md") if p.name == "report.md" or p.name.startswith("report.")])
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


def prompt_path_for(role: str, focus: str) -> Path:
    if role == "verifier":
        name = PROMPT_FILES["verifier"]["default"]
    else:
        name = PROMPT_FILES["submitter"].get(focus, PROMPT_FILES["submitter"]["full"])
    return AGENTS_DIR / name


def make_branch_name(investigation_date: str, ticker: str, contributor: str | None = None) -> str:
    """Unique branch: report/DATE-TICKER-<userhash8>."""
    cid = contributor_id(contributor)
    user_hash = hashlib.sha256(cid.lower().encode("utf-8")).hexdigest()[:8]
    safe_ticker = ticker.upper().replace(".", "-")
    return f"report/{investigation_date}-{safe_ticker}-{user_hash}"
