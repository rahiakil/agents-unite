#!/usr/bin/env python3
"""
Built-in agent harness: web search + LLM → report files.

Usage:
  python3 scripts/run_agent.py              # uses .agents-unite/prompt.md + run-meta.json
  python3 scripts/run_agent.py --assign     # assign + scaffold + run
  python3 scripts/run_agent.py --dry-run    # show plan, no LLM call
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = REPO_ROOT / ".agents-unite"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from agent_config import llm_configured, llm_settings  # noqa: E402
from llm_client import LLMError, chat_completion  # noqa: E402
from web_search import format_for_prompt, search  # noqa: E402

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


def load_meta(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    if "--- PROMPT ---" in raw:
        raw = raw.split("--- PROMPT ---", 1)[0]
    return json.loads(raw.strip())


def extract_json(text: str) -> dict:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fence:
        text = fence.group(1).strip()
    start = text.find("{")
    if start < 0:
        raise ValueError("no JSON object in LLM response")
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : i + 1])
    raise ValueError("unbalanced JSON in LLM response")


def build_search_query(meta: dict) -> str:
    role = meta.get("daily_role", "research")
    ticker = meta.get("ticker", "")
    date = meta.get("date", "")
    focus = meta.get("focus", "full")
    if role in ("patterns", "findings"):
        return f"stock market breaking news {date} sector themes"
    if role == "verify":
        return f"{ticker} stock news reddit twitter {date}"
    if role == "consensus":
        return f"{ticker} stock sentiment {date}"
    focus_hint = {"social": "reddit twitter", "news": "news earnings", "trading": "price volume", "sentiment": "sentiment"}.get(focus, "")
    return f"{ticker} stock {focus_hint} {date} market"


def gather_folder_context(output_dir: Path) -> str:
    if not output_dir.is_dir():
        return ""
    chunks: list[str] = []
    for path in sorted(output_dir.glob("*")):
        if path.suffix in (".md", ".json") and path.is_file():
            text = path.read_text(encoding="utf-8")
            if len(text) > 12000:
                text = text[:12000] + "\n... [truncated]"
            chunks.append(f"### {path.name}\n{text}")
    return "\n\n".join(chunks)


def write_outputs(meta: dict, data: dict) -> list[Path]:
    written: list[Path] = []
    output_dir = REPO_ROOT / meta.get("output_dir", "")
    output_dir.mkdir(parents=True, exist_ok=True)
    role = meta.get("daily_role", "research")

    if role == "research":
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


def run_llm(meta: dict, user_prompt: str, cfg: dict) -> dict:
    settings = llm_settings(cfg)
    if settings["provider"] != "ollama" and not settings["api_key"]:
        raise LLMError(
            f"No API key in ${settings['api_key_env']}. Set it or use llm_provider: ollama."
        )

    search_block = ""
    if settings["web_search"] and meta.get("daily_role") in ("research", "verify", "consensus", "patterns", "findings"):
        q = build_search_query(meta)
        results = search(q, provider=settings["web_search_provider"])
        if not results and settings["web_search_provider"] == "duckduckgo":
            print(
                "warning: no search results — pip install duckduckgo-search or set TAVILY_API_KEY",
                file=sys.stderr,
            )
        search_block = format_for_prompt(results)

    context = gather_folder_context(REPO_ROOT / meta.get("output_dir", ""))
    user_content = user_prompt
    if search_block:
        user_content = f"{search_block}\n\n---\n\n{user_prompt}"
    if context:
        user_content = f"## Existing files in output folder\n\n{context}\n\n---\n\n{user_content}"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    raw = chat_completion(
        provider=settings["provider"],
        model=settings["model"],
        api_key=settings["api_key"],
        base_url=settings["base_url"],
        messages=messages,
        temperature=settings["temperature"],
        max_tokens=settings["max_tokens"],
    )
    return extract_json(raw)


def assign_and_scaffold() -> tuple[dict, str]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "run_investigation.py"), "--scaffold", "--metadata"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "run_investigation failed")

    raw = proc.stdout
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    meta_path = STATE_DIR / "run-meta.json"
    meta_path.write_text(raw, encoding="utf-8")

    if "--- PROMPT ---" in raw:
        meta_text, prompt = raw.split("--- PROMPT ---", 1)
    else:
        meta_text, prompt = raw, ""
    prompt = prompt.lstrip()
    (STATE_DIR / "prompt.md").write_text(prompt, encoding="utf-8")
    return json.loads(meta_text.strip()), prompt


def validate_output(meta: dict) -> None:
    output = REPO_ROOT / meta.get("output_dir", "")
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "validate_report.py"), str(output) + "/"],
        cwd=REPO_ROOT,
    )
    if proc.returncode != 0:
        raise RuntimeError("validate_report.py failed")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run built-in LLM agent harness.")
    parser.add_argument("--assign", action="store_true", help="Assign role and scaffold before run")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without calling LLM")
    parser.add_argument("--skip-validate", action="store_true")
    parser.add_argument("--meta", type=Path, help="Path to run-meta.json")
    parser.add_argument("--prompt", type=Path, help="Path to prompt.md")
    args = parser.parse_args()

    from au_common import load_yaml_config, normalize_role

    cfg = load_yaml_config()

    if args.assign:
        meta, prompt = assign_and_scaffold()
    else:
        meta_path = args.meta or STATE_DIR / "run-meta.json"
        prompt_path = args.prompt or STATE_DIR / "prompt.md"
        if not meta_path.is_file() or not prompt_path.is_file():
            print("error: run ./scripts/run-agent.sh first or use --assign", file=sys.stderr)
            return 1
        meta = load_meta(meta_path)
        prompt = prompt_path.read_text(encoding="utf-8")

    role = normalize_role(meta.get("daily_role", "research"))
    meta = {**meta, "daily_role": role}

    if args.dry_run:
        print(f"LLM configured: {llm_configured(cfg)}")
        print(f"Search query: {build_search_query(meta)}")
        print(f"Prompt length: {len(prompt)} chars")
        return 0

    if not llm_configured(cfg):
        print(
            "error: no LLM configured. Set OPENAI_API_KEY or llm_provider: ollama in .agents-unite/config.yaml",
            file=sys.stderr,
        )
        return 1

    try:
        data = run_llm(meta, prompt, cfg)
        paths = write_outputs(meta, data)
        for p in paths:
            print(f"Wrote {p.relative_to(REPO_ROOT)}")
    except (LLMError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not args.skip_validate and role in ("research", "verify", "consensus", "submitter"):
        try:
            validate_output(meta)
            print("Validation OK")
        except RuntimeError:
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
