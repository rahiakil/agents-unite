#!/usr/bin/env python3
"""OpenAI Swarm harness — triage + research agents for daily assignment."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "harness"))

from agent_config import llm_configured, llm_settings  # noqa: E402
from au_common import load_yaml_config, normalize_role  # noqa: E402
from harness.artifacts import SYSTEM_PROMPT, extract_json, write_outputs  # noqa: E402
from harness.context import build_user_content  # noqa: E402
from harness.state import assign_and_scaffold, resolve_state  # noqa: E402


def run_swarm(user_content: str, cfg: dict) -> str:
    try:
        from swarm import Agent, Swarm
    except ImportError as exc:
        raise RuntimeError(
            "OpenAI Swarm not installed. Run: pip install -r requirements-harness.txt"
        ) from exc

    settings = llm_settings(cfg)
    if settings["api_key"]:
        os.environ.setdefault("OPENAI_API_KEY", settings["api_key"])

    model = settings["model"]

    researcher = Agent(
        name="Researcher",
        instructions=(
            f"{SYSTEM_PROMPT}\n\n"
            "You are the research specialist. Return JSON only with report_markdown and sources."
        ),
        model=model,
    )

    def transfer_to_researcher() -> Agent:
        return researcher

    triage = Agent(
        name="Triage",
        instructions=(
            "Hand off market research requests to the Researcher agent immediately. "
            "The user message is a daily ticker assignment."
        ),
        functions=[transfer_to_researcher],
    )

    client = Swarm()
    response = client.run(
        agent=researcher,
        messages=[{"role": "user", "content": user_content}],
        model_override=model,
    )
    if not response.messages:
        raise RuntimeError("Swarm returned no messages")
    return str(response.messages[-1].get("content", ""))


def validate_output(meta: dict) -> None:
    output = REPO_ROOT / meta.get("output_dir", "")
    proc = __import__("subprocess").run(
        [sys.executable, str(REPO_ROOT / "scripts" / "validate_report.py"), str(output) + "/"],
        cwd=REPO_ROOT,
    )
    if proc.returncode != 0:
        raise RuntimeError("validate_report.py failed")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run OpenAI Swarm harness for agents-unite.")
    parser.add_argument("--assign", action="store_true")
    parser.add_argument("--skip-validate", action="store_true")
    parser.add_argument("--meta", type=Path)
    parser.add_argument("--prompt", type=Path)
    args = parser.parse_args()

    cfg = load_yaml_config()
    if not llm_configured(cfg):
        print("error: set OPENAI_API_KEY or configure llm_provider in config", file=sys.stderr)
        return 1

    try:
        if args.assign:
            meta, prompt = assign_and_scaffold()
        else:
            meta, prompt = resolve_state(args.meta, args.prompt)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    role = normalize_role(meta.get("daily_role", "research"))
    meta = {**meta, "daily_role": role}

    try:
        user_content = build_user_content(meta, prompt, cfg)
        raw = run_swarm(user_content, cfg)
        data = extract_json(raw)
        paths = write_outputs(meta, data)
        for p in paths:
            print(f"Wrote {p.relative_to(REPO_ROOT)}")
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
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
