#!/usr/bin/env python3
"""Validate submitter reports and verifier consensus files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from au_common import AGENTS_DIR, prompt_hash  # noqa: E402

DATA_DIR = REPO_ROOT / "data"

REQUIRED_REPORT_SECTIONS = [
    "sentiment",
    "key themes",
    "sources",
    "price snapshot",
    "notable events",
]

CONSENSUS_SECTIONS = [
    "summary",
    "consensus score",
    "agreement",
    "disagreements",
    "source audit",
]

SENTIMENT_PATTERN = re.compile(
    r"sentiment\s*(?:score)?\s*[:=]\s*(-?(?:0(?:\.\d+)?|1(?:\.0+)?))\b",
    re.IGNORECASE,
)
CONSENSUS_PATTERN = re.compile(
    r"consensus\s*(?:score)?\s*[:=]\s*(-?(?:0(?:\.\d+)?|1(?:\.0+)?))\b",
    re.IGNORECASE,
)
FRONTMATTER_SENTIMENT = re.compile(
    r"^sentiment_score:\s*(-?(?:0(?:\.\d+)?|1(?:\.0+)?))\s*$",
    re.MULTILINE,
)
FRONTMATTER_CONSENSUS = re.compile(
    r"^consensus_score:\s*(-?(?:0(?:\.\d+)?|1(?:\.0+)?))\s*$",
    re.MULTILINE,
)
PROMPT_HASH_FM = re.compile(r"^prompt_hash:\s*(\S+)\s*$", re.MULTILINE)
PROMPT_FILE_FM = re.compile(r"^prompt_file:\s*(\S+)\s*$", re.MULTILINE)


def validate_score(score: float, context: str) -> list[str]:
    if not -1.0 <= score <= 1.0:
        return [f"{context}: score {score} must be between -1.0 and 1.0"]
    return []


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


def validate_prompt_provenance(text: str) -> list[str]:
    errors: list[str] = []
    fm = parse_frontmatter(text)
    ph = fm.get("prompt_hash")
    pf = fm.get("prompt_file")
    if not ph and not pf:
        return []  # legacy demo reports grandfathered
    if not ph or not pf:
        errors.append("missing prompt_hash or prompt_file in frontmatter (required for new reports)")
        return errors
    path = REPO_ROOT / pf
    if not path.is_file():
        errors.append(f"prompt_file not found: {pf}")
        return errors
    expected = prompt_hash(path)
    if ph != expected:
        errors.append(f"prompt_hash mismatch: got {ph}, expected {expected} for {pf}")
    return errors


def validate_report_sections(text: str, sections: list[str]) -> list[str]:
    errors: list[str] = []
    lowered = text.lower()
    for section in sections:
        pattern = rf"^#{{1,3}}\s+{re.escape(section)}\b"
        if not re.search(pattern, lowered, re.MULTILINE):
            errors.append(f"missing required section: '{section.title()}'")
    return errors


def validate_sources_json(path: Path, *, min_sources: int = 1) -> list[str]:
    errors: list[str] = []
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        return [f"{path.name} invalid JSON: {exc}"]

    if not isinstance(data, dict):
        return [f"{path.name} must be a JSON object"]

    for key in ("ticker", "date", "sources"):
        if key not in data:
            errors.append(f"{path.name} missing key: {key}")

    sources = data.get("sources")
    if not isinstance(sources, list):
        return errors + [f"{path.name} 'sources' must be an array"]

    if len(sources) < min_sources:
        errors.append(f"{path.name} needs at least {min_sources} source(s)")

    for i, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"sources[{i}] must be object")
            continue
        if not source.get("url"):
            errors.append(f"sources[{i}] missing url")
        st = source.get("type")
        if st not in {"twitter", "reddit", "news", "other"}:
            errors.append(f"sources[{i}] invalid type: {st!r}")
    return errors


def validate_submitter_report(report_path: Path) -> list[str]:
    errors: list[str] = []
    text = report_path.read_text(encoding="utf-8")
    if len(text.strip()) < 200:
        errors.append(f"{report_path.name} too short")

    fm = parse_frontmatter(text)
    if fm.get("daily_role") and fm["daily_role"] != "submitter":
        errors.append("daily_role must be submitter")

    match = FRONTMATTER_SENTIMENT.search(text)
    if match:
        errors.extend(validate_score(float(match.group(1)), "sentiment_score"))
    elif not SENTIMENT_PATTERN.search(text):
        errors.append("missing sentiment_score")

    errors.extend(validate_report_sections(text, REQUIRED_REPORT_SECTIONS))
    errors.extend(validate_prompt_provenance(text))

    slug = report_path.name.replace("report.", "").replace(".md", "")
    if slug == "report":
        sources_path = report_path.parent / "sources.json"
    else:
        sources_path = report_path.parent / f"sources.{slug}.json"
        if not sources_path.is_file():
            sources_path = report_path.parent / "sources.json"

    if not sources_path.is_file():
        errors.append(f"missing sources file for {report_path.name}")
    else:
        errors.extend(validate_sources_json(sources_path))

    return errors


def validate_consensus(consensus_path: Path) -> list[str]:
    errors: list[str] = []
    text = consensus_path.read_text(encoding="utf-8")
    if len(text.strip()) < 150:
        errors.append("consensus.md too short")

    match = FRONTMATTER_CONSENSUS.search(text)
    if match:
        errors.extend(validate_score(float(match.group(1)), "consensus_score"))
    else:
        errors.append("missing consensus_score")

    errors.extend(validate_report_sections(text, CONSENSUS_SECTIONS))
    errors.extend(validate_prompt_provenance(text))
    return errors


def validate_report_dir(report_dir: Path) -> list[str]:
    if not report_dir.is_dir():
        return [f"directory not found: {report_dir}"]

    errors: list[str] = []
    reports = sorted(report_dir.glob("report*.md"))
    consensus = report_dir / "consensus.md"

    if not reports and not consensus.is_file():
        return [f"no report*.md or consensus.md in {report_dir}"]

    for rp in reports:
        errors.extend(validate_submitter_report(rp))

    if consensus.is_file():
        errors.extend(validate_consensus(consensus))

    return errors


def parse_report_sentiment(text: str) -> tuple[float | None, list[str]]:
    """Public API for stats/aggregate scripts."""
    errors: list[str] = []
    match = FRONTMATTER_SENTIMENT.search(text)
    if match:
        score = float(match.group(1))
        errors.extend(validate_score(score, "frontmatter"))
        return score, errors
    match = SENTIMENT_PATTERN.search(text)
    if match:
        score = float(match.group(1))
        errors.extend(validate_score(score, "body"))
        return score, errors
    return None, ["missing sentiment score"]


def _resolve_report_dir(path: Path) -> Path | None:
    candidates = [path, REPO_ROOT / path] if not path.is_absolute() else [path]
    for candidate in candidates:
        if candidate.name.startswith("report") and candidate.suffix == ".md":
            return candidate.parent.resolve()
        if candidate.name == "consensus.md":
            return candidate.parent.resolve()
        if candidate.is_dir():
            if list(candidate.glob("report*.md")) or (candidate / "consensus.md").is_file():
                return candidate.resolve()
    return None


def discover_report_dirs(paths: list[str] | None) -> list[Path]:
    if paths:
        dirs: list[Path] = []
        for raw in paths:
            resolved = _resolve_report_dir(Path(raw))
            if resolved:
                dirs.append(resolved)
        return sorted(set(dirs))

    if not DATA_DIR.is_dir():
        return []
    dirs = set()
    for p in DATA_DIR.glob("*/*/report*.md"):
        if p.parent.parent.name.startswith("_"):
            continue
        dirs.add(p.parent.resolve())
    for p in DATA_DIR.glob("*/*/consensus.md"):
        if p.parent.parent.name.startswith("_"):
            continue
        dirs.add(p.parent.resolve())
    return sorted(dirs)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate agents-unite reports.")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--changed-only", action="store_true")
    args = parser.parse_args()

    if args.changed_only and not args.paths:
        print("No paths; skipping.")
        return 0

    report_dirs = discover_report_dirs(args.paths if args.paths else None)
    if not report_dirs:
        print("No reports found.")
        return 0

    all_errors: list[str] = []
    for report_dir in report_dirs:
        errors = validate_report_dir(report_dir)
        if errors:
            all_errors.append(f"\n{report_dir.relative_to(REPO_ROOT)}:")
            all_errors.extend(f"  - {e}" for e in errors)
        else:
            print(f"OK: {report_dir.relative_to(REPO_ROOT)}")

    if all_errors:
        print("Validation failed:", file=sys.stderr)
        print("\n".join(all_errors), file=sys.stderr)
        return 1

    print(f"Validated {len(report_dirs)} directory(ies).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
