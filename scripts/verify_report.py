#!/usr/bin/env python3
"""Structural verifier for one report directory.

The paper's threat model says CI checks shape, not truth. This module is the
cheap verifier described in docs/TRUST.md and agents/verify-report.md:

- placeholder and reserved hosts are fabricated
- optional known-url set catches URLs that are not in the cited book
- collected_at older than 7 days is stale
- instruction-override phrases are prompt injection
- schema failures are rejected

It does not fetch the network. A HEAD check is still future work.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

from au_common import report_slug, sources_filename_for_report

PLACEHOLDER_HOSTS = {
    "example.com",
    "example.org",
    "example.net",
    "localhost",
    "placeholder",
}
RESERVED_SUFFIXES = (".invalid", ".example", ".localhost", ".test")
INJECTION_PHRASES = (
    "ignore previous instructions",
    "ignore all previous",
    "ignore prior instructions",
    "you are now",
    "system prompt",
    "disregard the above",
    "exfiltrate",
)
STALE_DAYS = 7


def normalize_url(url: str) -> str:
    raw = url.strip()
    parsed = urlparse(raw)
    if not parsed.scheme or not parsed.netloc:
        return raw.lower().rstrip("/")
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    path = parsed.path.rstrip("/")
    return f"{parsed.scheme.lower()}://{host}{path}"


def injection_reasons(text: str) -> list[str]:
    lowered = text.lower()
    hits = [phrase for phrase in INJECTION_PHRASES if phrase in lowered]
    if not hits:
        return []
    return [f"prompt_injection:{hits[0]}"]


def _host(url: str) -> str:
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def classify_url(
    url: str,
    *,
    known_urls: set[str] | None = None,
    collected_at: str | None = None,
    report_date: str | None = None,
) -> str | None:
    """Return a reason token, or None when the URL is acceptable."""
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return "bad_url"
    host = _host(url)
    if host in PLACEHOLDER_HOSTS or host.endswith(RESERVED_SUFFIXES):
        return "fabricated_url"
    if known_urls is not None and normalize_url(url) not in known_urls:
        return "unknown_url"
    if collected_at and report_date:
        age = _age_days(collected_at, report_date)
        if age is not None and age > STALE_DAYS:
            return "stale_source"
    return None


def _age_days(collected_at: str, report_date: str) -> int | None:
    try:
        report = date.fromisoformat(report_date[:10])
    except ValueError:
        return None
    token = collected_at.strip()
    try:
        if "T" in token:
            collected = datetime.fromisoformat(token.replace("Z", "+00:00")).date()
        else:
            collected = date.fromisoformat(token[:10])
    except ValueError:
        return None
    return (report - collected).days


def verify_sources(
    sources_path: Path,
    *,
    known_urls: set[str] | None = None,
    report_date: str | None = None,
) -> list[str]:
    try:
        data = json.loads(sources_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"sources_json:{exc.msg}"]
    if not isinstance(data, dict):
        return ["sources_json:not_object"]
    collected = data.get("collected_at")
    reasons: list[str] = []
    sources = data.get("sources")
    if not isinstance(sources, list):
        return ["sources_json:sources_not_list"]
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            reasons.append(f"sources[{index}]:not_object")
            continue
        url = str(source.get("url") or "")
        reason = classify_url(
            url,
            known_urls=known_urls,
            collected_at=str(collected) if collected else None,
            report_date=report_date,
        )
        if reason:
            reasons.append(f"sources[{index}]:{reason}")
    return reasons


def verdict_for_report(
    report_path: Path,
    *,
    known_urls: set[str] | None = None,
    schema_errors: list[str] | None = None,
) -> dict:
    """Return verdict, reasons, and the slug for one report file."""
    text = report_path.read_text(encoding="utf-8")
    reasons: list[str] = []
    if schema_errors:
        reasons.extend(schema_errors)
    reasons.extend(injection_reasons(text))
    sources_name = sources_filename_for_report(report_path.name)
    sources_path = report_path.parent / sources_name if sources_name else None
    report_date = _front_value(text, "date")
    if sources_path and sources_path.is_file():
        reasons.extend(
            verify_sources(sources_path, known_urls=known_urls, report_date=report_date)
        )
    elif sources_path is not None:
        reasons.append("missing_sources")
    hard_tokens = ("fabricated", "injection", "unknown_url", "bad_url", "sources_json", "missing_sources")
    stale_only = bool(reasons) and all("stale_source" in reason for reason in reasons)
    if not reasons:
        verdict = "approved"
    elif stale_only and not schema_errors:
        verdict = "needs_revision"
    elif any(any(token in reason for token in hard_tokens) for reason in reasons) or schema_errors:
        verdict = "rejected"
    else:
        verdict = "rejected"
    slug = report_slug(report_path.name) or ""
    username = _front_value(text, "github_username") or slug
    return {
        "slug": username or slug,
        "file_slug": slug,
        "verdict": verdict,
        "reasons": reasons,
    }


def _front_value(text: str, key: str) -> str | None:
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    prefix = f"{key}:"
    for line in parts[1].splitlines():
        if line.strip().lower().startswith(prefix):
            return line.split(":", 1)[1].strip()
    return None


def eligibility_vote(verdict: str) -> str:
    """needs_revision does not enter consensus. Only approved does."""
    return "approved" if verdict == "approved" else "rejected"


_VERDICT_RE = re.compile(r"([A-Za-z0-9_-]+)=(approved|rejected|needs_revision)")


def parse_report_verdicts(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    raw = ""
    for line in parts[1].splitlines():
        if line.strip().lower().startswith("report_verdicts:"):
            raw = line.split(":", 1)[1].strip()
            break
    return {slug: verdict for slug, verdict in _VERDICT_RE.findall(raw)}
