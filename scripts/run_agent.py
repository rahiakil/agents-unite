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
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "harness"))

from agent_config import llm_configured, llm_settings  # noqa: E402
from au_common import load_yaml_config, normalize_role  # noqa: E402
from harness.artifacts import SYSTEM_PROMPT, extract_json, write_outputs  # noqa: E402
from harness.context import build_search_query, build_user_content  # noqa: E402
from harness.paths import STATE_DIR  # noqa: E402
from harness.state import assign_and_scaffold, resolve_state  # noqa: E402
from llm_client import LLMError, chat_completion  # noqa: E402


def run_llm(meta: dict, user_prompt: str, cfg: dict) -> dict:
    settings = llm_settings(cfg)
    if settings["provider"] != "ollama" and not settings["api_key"]:
        raise LLMError(
            f"No API key in ${settings['api_key_env']}. Set it or use llm_provider: ollama."
        )

    user_content = build_user_content(meta, user_prompt, cfg)
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

    cfg = load_yaml_config()

    try:
        if args.assign:
            meta, prompt = assign_and_scaffold()
        else:
            meta, prompt = resolve_state(args.meta, args.prompt)
    except FileNotFoundError:
        print("error: run ./scripts/run-agent.sh first or use --assign", file=sys.stderr)
        return 1

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
