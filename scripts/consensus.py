#!/usr/bin/env python3
"""Weighted-median consensus with MAD outlier rejection.

Implements the scoring rules in docs/CONSENSUS.md and agents/consensus-run.md.
No LLM. Theme lines are copied from the reports that remain after the filter.

Weight mode:
- equal: 1.0 per report (v2)
- caller-supplied weights: stake * reputation * recency (v3)

The weighted median is the smallest score whose cumulative weight reaches
half the total. Even-count MAD uses the average of the two central values.
When n < 3 the MAD filter is skipped. If the filter would drop every score,
the unfiltered median is the fallback and confidence is low.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from au_common import prompt_hash, report_slug, sources_filename_for_report  # noqa: E402
from validate_report import (  # noqa: E402
    extract_sentiment_score,
    parse_frontmatter,
    validate_submitter_report,
)
from verify_report import eligibility_vote, parse_report_verdicts  # noqa: E402

CONSENSUS_PROMPT = REPO_ROOT / "agents" / "consensus-run.md"


def median(values: list[float]) -> float:
    ordered = sorted(values)
    count = len(ordered)
    mid = count // 2
    if count % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def mad_filter(scores: list[float], *, k: float = 2.0) -> tuple[list[int], float, float, bool]:
    """Return kept indexes, median, MAD, and whether the filter fell back.

    Drop when |x - median| > k * MAD and n >= 3. A zero MAD keeps only the
    center. An empty keep-set falls back to every score.
    """
    if len(scores) < 3:
        return list(range(len(scores))), median(scores) if scores else 0.0, 0.0, False
    center = median(scores)
    width = median([abs(score - center) for score in scores])
    kept = [i for i, score in enumerate(scores) if not (abs(score - center) > k * width)]
    if not kept:
        return list(range(len(scores))), center, width, True
    return kept, center, width, False


def weighted_median(scores: list[float], weights: list[float]) -> float:
    if not scores:
        raise ValueError("weighted_median requires at least one score")
    pairs = sorted(zip(scores, weights), key=lambda item: (item[0], -item[1]))
    total = sum(weight for _score, weight in pairs if weight > 0)
    if total <= 0:
        return median(scores)
    half = total / 2.0
    running = 0.0
    for score, weight in pairs:
        if weight <= 0:
            continue
        running += weight
        if running >= half:
            return score
    return pairs[-1][0]


def confidence_label(scores: list[float]) -> str:
    count = len(scores)
    if count == 0:
        return "low"
    spread = max(scores) - min(scores) if count else 0.0
    if count >= 3 and spread <= 0.4:
        return "high"
    if count == 2 or (count >= 2 and spread <= 0.7):
        return "medium"
    return "low"


def _themes(text: str) -> list[str]:
    lines = []
    in_themes = False
    for line in text.splitlines():
        heading = line.strip().lower()
        if heading.startswith("#"):
            in_themes = heading.lstrip("#").strip() == "key themes"
            continue
        if in_themes and line.strip().startswith("- "):
            lines.append(line.strip()[2:].strip())
    return lines


def _load_sources(report_path: Path) -> list[dict]:
    name = sources_filename_for_report(report_path.name)
    if not name:
        return []
    path = report_path.parent / name
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    sources = data.get("sources") if isinstance(data, dict) else None
    return [item for item in sources if isinstance(item, dict)] if isinstance(sources, list) else []


def load_valid_reports(directory: Path) -> list[dict]:
    """Schema-valid reports in a ticker directory."""
    found: list[dict] = []
    for path in sorted(directory.glob("report*.md")):
        slug = report_slug(path.name)
        if slug is None:
            continue
        errors = validate_submitter_report(path)
        if errors:
            continue
        text = path.read_text(encoding="utf-8")
        score, score_errors = extract_sentiment_score(text)
        if score is None or score_errors:
            continue
        fm = parse_frontmatter(text)
        username = fm.get("github_username") or slug or path.stem
        found.append(
            {
                "path": path,
                "username": username,
                "slug": slug or username,
                "score": float(score),
                "themes": _themes(text),
                "sources": _load_sources(path),
                "focus": fm.get("focus", ""),
            }
        )
    return found


def verification_votes(directory: Path) -> dict[str, list[str]] | None:
    files = sorted(directory.glob("verification.*.md"))
    if not files:
        return None
    votes: dict[str, list[str]] = {}
    for path in files:
        parsed = parse_report_verdicts(path.read_text(encoding="utf-8"))
        for slug, verdict in parsed.items():
            votes.setdefault(slug, []).append(eligibility_vote(verdict))
    return votes


def approved_usernames(reports: list[dict], votes: dict[str, list[str]] | None) -> list[dict]:
    if votes is None:
        return list(reports)
    kept = []
    for report in reports:
        keys = {report["username"], report["slug"]}
        ballots: list[str] = []
        for key in keys:
            ballots.extend(votes.get(key, []))
        if not ballots:
            continue
        approvals = sum(1 for vote in ballots if vote == "approved")
        rejections = len(ballots) - approvals
        if approvals > rejections:
            kept.append(report)
    return kept


def aggregate(reports: list[dict], weights: dict[str, float] | None = None) -> dict:
    """MAD filter then weighted median. `weights` keys are usernames."""
    if not reports:
        return {
            "consensus_score": None,
            "confidence": "low",
            "report_count": 0,
            "kept": [],
            "dropped": [],
            "fell_back": False,
            "method": "weighted_median",
        }
    scores = [float(item["score"]) for item in reports]
    used_weights = []
    for item in reports:
        if weights is None:
            used_weights.append(1.0)
        else:
            used_weights.append(float(weights.get(item["username"], weights.get(item["slug"], 1.0))))
    kept_idx, _center, _width, fell_back = mad_filter(scores)
    kept = [reports[i] for i in kept_idx]
    dropped = [reports[i] for i in range(len(reports)) if i not in set(kept_idx)]
    kept_scores = [scores[i] for i in kept_idx]
    kept_weights = [used_weights[i] for i in kept_idx]
    if fell_back:
        score = median(scores)
        confidence = "low"
        kept = list(reports)
        dropped = []
        kept_scores = scores
    else:
        score = weighted_median(kept_scores, kept_weights)
        confidence = confidence_label(kept_scores)
    return {
        "consensus_score": round(float(score), 4),
        "confidence": confidence,
        "report_count": len(kept),
        "input_count": len(reports),
        "kept": kept,
        "dropped": dropped,
        "fell_back": fell_back,
        "method": "weighted_median",
        "spread": round(max(kept_scores) - min(kept_scores), 4) if kept_scores else 0.0,
    }


def _deduped_sources(reports: list[dict]) -> list[dict]:
    best: dict[str, dict] = {}
    for report in reports:
        for source in report["sources"]:
            url = str(source.get("url") or "")
            if not url:
                continue
            key = url.strip().rstrip("/").lower()
            current = best.get(key)
            snippet = str(source.get("snippet") or source.get("title") or "")
            if current is None or len(snippet) > len(str(current.get("snippet") or "")):
                chosen = dict(source)
                chosen["contributor"] = report["username"]
                best[key] = chosen
    return list(best.values())


def render_consensus(
    *,
    ticker: str,
    day: str,
    leader: str,
    result: dict,
) -> str:
    score = result["consensus_score"]
    score_text = "0.0" if score is None else f"{score:.4f}"
    kept = result.get("kept") or []
    dropped = result.get("dropped") or []
    themes: dict[str, int] = {}
    for report in kept:
        for theme in report.get("themes") or []:
            themes[theme] = themes.get(theme, 0) + 1
    agreed = [theme for theme, count in sorted(themes.items()) if count * 2 >= max(1, len(kept))]
    split = [theme for theme, count in sorted(themes.items()) if theme not in agreed]
    sources = _deduped_sources(kept)
    phash = prompt_hash(CONSENSUS_PROMPT) if CONSENSUS_PROMPT.is_file() else ""
    prompt_file = "agents/consensus-run.md"
    contributors = ", ".join(sorted({item["username"] for item in kept})) or "none"
    agreement = "\n".join(f"- {theme}" for theme in agreed) or "- No theme is shared by half the kept reports."
    divergence_lines = [f"- {theme}" for theme in split]
    if dropped:
        divergence_lines.append(
            "- Outliers dropped: " + ", ".join(f"{item['username']} ({item['score']:.2f})" for item in dropped)
        )
    if result.get("fell_back"):
        divergence_lines.append("- Every score was an outlier. The unfiltered median is the fallback.")
    divergence = "\n".join(divergence_lines) or "- Scores sit in a tight band."
    source_lines = "\n".join(
        f"- {item.get('type', 'other')}: {item.get('url')}" for item in sources[:12]
    ) or "- No sources carried forward."
    body = f"""---
ticker: {ticker}
date: {day}
github_username: {leader}
daily_role: consensus
prompt_hash: {phash}
prompt_file: {prompt_file}
consensus_score: {score_text}
confidence: {result.get('confidence', 'low')}
report_count: {result.get('report_count', 0)}
method: weighted_median
contributors: {contributors}
---

# Summary

{leader} published the weighted median for {ticker} on {day}. {result.get('report_count', 0)} reports remained after the MAD filter. Confidence is {result.get('confidence', 'low')}.

# Consensus Score

Consensus score: {score_text}

# Agreement

{agreement}

# Divergence

{divergence}

# Source coverage

{len(sources)} unique URLs after dedupe.

{source_lines}

# Price snapshot

| Field | Value |
|-------|-------|
| Reports kept | {result.get('report_count', 0)} |
| Reports dropped | {len(dropped)} |

# Notable events

- None identified
"""
    return body


def consensus_from_dir(
    directory: Path,
    *,
    weights: dict[str, float] | None = None,
    leader: str = "consensus-bot",
) -> dict:
    reports = load_valid_reports(directory)
    votes = verification_votes(directory)
    approved = approved_usernames(reports, votes)
    result = aggregate(approved, weights)
    day = directory.parent.name
    ticker = directory.name
    text = render_consensus(ticker=ticker, day=day, leader=leader, result=result)
    result["markdown"] = text
    result["approved_usernames"] = [item["username"] for item in approved]
    return result


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Compute weighted-median consensus for one ticker directory.")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--leader", default="consensus-bot")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = consensus_from_dir(args.directory, leader=args.leader)
    if args.write and result.get("markdown"):
        (args.directory / "consensus.md").write_text(result["markdown"], encoding="utf-8")
    if args.json:
        public = {k: v for k, v in result.items() if k not in {"kept", "dropped", "markdown"}}
        public["kept"] = [item["username"] for item in result.get("kept") or []]
        public["dropped"] = [item["username"] for item in result.get("dropped") or []]
        print(json.dumps(public, indent=2))
    else:
        print(result.get("consensus_score"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
