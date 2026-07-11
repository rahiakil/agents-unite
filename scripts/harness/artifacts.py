from __future__ import annotations

import json
import re
from pathlib import Path

from harness.paths import REPO_ROOT

SYSTEM_PROMPT = """You are agents-unite research agent. You produce structured market research artifacts.

Rules:
- Use ONLY URLs from the provided web search results for sources. Do not invent URLs.
- No trading advice. Sentiment reporting only.
- Follow agents/prose-style.md: direct, specific, no AI filler.
- Output valid JSON only (no markdown outside JSON).

JSON schema:
{
  "report_markdown": "full report file including YAML frontmatter and required H1 sections",
  "sources": {
    "ticker": "SYMBOL",
    "date": "YYYY-MM-DD",
    "github_username": "user",
    "focus": "social|news|...",
    "collected_at": "ISO-8601 UTC",
    "sources": [
      {"type": "twitter|reddit|news|other", "url": "https://...", "title": "...", "snippet": "..."}
    ]
  }
}

For verify/consensus/weekly roles, use keys:
- verification_markdown OR consensus_markdown OR weekly_markdown (one primary file)
- sources optional for non-research roles
"""


def extract_json(text: str) -> dict:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fence:
        text = fence.group(1).strip()
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    start = text.find("{")
    if start < 0:
        raise ValueError("no JSON object in LLM response")
    chunk = text[start:]
    try:
        import json_repair  # type: ignore

        return json_repair.loads(chunk)
    except Exception:
        pass
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                chunk = text[start : i + 1]
                try:
                    return json.loads(chunk)
                except json.JSONDecodeError:
                    try:
                        import json_repair  # type: ignore

                        return json_repair.loads(chunk)
                    except Exception as exc:
                        raise ValueError(f"invalid JSON in LLM response: {exc}") from exc
    raise ValueError("unbalanced JSON in LLM response")


def write_outputs(meta: dict, data: dict) -> list[Path]:
    written: list[Path] = []
    output_dir = REPO_ROOT / meta.get("output_dir", "")
    output_dir.mkdir(parents=True, exist_ok=True)
    role = meta.get("daily_role", "research")

    if role in ("research", "submitter"):
        report = data.get("report_markdown") or data.get("report_md")
        sources = data.get("sources")
        if not report:
            raise ValueError("LLM response missing report_markdown")
        rp = output_dir / meta["report_filename"]
        rp.write_text(report.strip() + "\n", encoding="utf-8")
        written.append(rp)
        if sources:
            sp = output_dir / meta["sources_filename"]
            sp.write_text(json.dumps(sources, indent=2) + "\n", encoding="utf-8")
            written.append(sp)
        return written

    if role == "verify":
        text = data.get("verification_markdown") or data.get("weekly_markdown")
        path = output_dir / meta["verification_filename"]
    elif role == "consensus":
        text = data.get("consensus_markdown")
        path = output_dir / meta["consensus_filename"]
    elif role in ("patterns", "findings"):
        text = data.get("weekly_markdown") or data.get("patterns_markdown") or data.get("findings_markdown")
        path = output_dir / meta["weekly_filename"]
    else:
        raise ValueError(f"unsupported role: {role}")

    if not text:
        raise ValueError(f"LLM response missing content for role {role}")
    path.write_text(text.strip() + "\n", encoding="utf-8")
    written.append(path)
    return written
