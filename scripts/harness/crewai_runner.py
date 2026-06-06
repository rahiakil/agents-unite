#!/usr/bin/env python3
"""CrewAI harness — multi-agent crew runs the daily assignment prompt."""

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
from harness.paths import STATE_DIR  # noqa: E402
from harness.state import assign_and_scaffold, resolve_state  # noqa: E402


def run_crewai(user_content: str, cfg: dict) -> str:
    try:
        from crewai import Agent, Crew, Process, Task
    except ImportError as exc:
        raise RuntimeError(
            "CrewAI not installed. Run: pip install -r requirements-harness.txt"
        ) from exc

    settings = llm_settings(cfg)
    if settings["api_key"]:
        os.environ.setdefault("OPENAI_API_KEY", settings["api_key"])

    researcher = Agent(
        role="Market Sentiment Researcher",
        goal="Produce a schema-valid agents-unite report with real cited sources",
        backstory=(
            "You collect social and news tone for one ticker. "
            "You write structured markdown and JSON. No trading advice."
        ),
        verbose=True,
        allow_delegation=False,
    )
    reviewer = Agent(
        role="Schema Verifier",
        goal="Ensure output is valid JSON with report_markdown and sources keys",
        backstory="You check structure and strip filler prose before submission.",
        verbose=False,
        allow_delegation=False,
    )

    research_task = Task(
        description=(
            f"{SYSTEM_PROMPT}\n\n---\n\nAssignment:\n{user_content}\n\n"
            "Return JSON only with report_markdown and sources."
        ),
        expected_output="Valid JSON object with report_markdown and sources",
        agent=researcher,
    )
    review_task = Task(
        description="Review the prior output. Fix JSON structure if needed. Return JSON only.",
        expected_output="Valid JSON object with report_markdown and sources",
        agent=reviewer,
        context=[research_task],
    )

    crew = Crew(
        agents=[researcher, reviewer],
        tasks=[research_task, review_task],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff()
    return str(result.raw if hasattr(result, "raw") else result)


def validate_output(meta: dict) -> None:
    output = REPO_ROOT / meta.get("output_dir", "")
    proc = __import__("subprocess").run(
        [sys.executable, str(REPO_ROOT / "scripts" / "validate_report.py"), str(output) + "/"],
        cwd=REPO_ROOT,
    )
    if proc.returncode != 0:
        raise RuntimeError("validate_report.py failed")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CrewAI harness for agents-unite.")
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
        raw = run_crewai(user_content, cfg)
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
