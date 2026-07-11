#!/usr/bin/env python3
"""Run the built-in LLM agent on multiple tickers (batch research)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "harness"))

from assign_role import assign_role  # noqa: E402
from agent_config import llm_configured  # noqa: E402
from au_common import (  # noqa: E402
    coverage_counts,
    load_active_tickers,
    load_yaml_config,
    resolve_investigation_date,
)
from harness.artifacts import write_outputs  # noqa: E402
from llm_client import LLMError  # noqa: E402
from run_agent import run_llm, validate_output  # noqa: E402
from run_investigation import append_prose_style, build_paths, render_prompt, write_scaffold  # noqa: E402


def pick_uncovered(date: str, count: int) -> list[str]:
    tickers = load_active_tickers()
    counts = coverage_counts(date)
    zero = [t for t in tickers if counts.get(t, 0) == 0]
    if not zero:
        # fall back to least-covered today
        ranked = sorted(tickers, key=lambda t: counts.get(t, 0))
        zero = ranked[:count]
    return zero[:count]


def report_exists(assignment: dict) -> bool:
    out = REPO_ROOT / assignment["output_dir"]
    report = out / assignment["report_filename"]
    sources = out / assignment["sources_filename"]
    if not report.is_file() or not sources.is_file():
        return False
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "validate_report.py"), str(out) + "/"],
        cwd=REPO_ROOT,
        capture_output=True,
    )
    return proc.returncode == 0


def run_ticker(
    ticker: str,
    date: str,
    *,
    contributor: str | None,
    skip_existing: bool,
    dry_run: bool,
    cfg: dict | None = None,
) -> bool:
    assignment = assign_role(
        date,
        contributor,
        force_role="research",
        force_ticker=ticker,
        use_cache=False,
    )
    paths = build_paths(assignment)
    output_dir = REPO_ROOT / paths["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    if skip_existing and report_exists(assignment):
        print(f"skip {ticker}: valid report already exists at {paths['output_dir']}/")
        return True

    if dry_run:
        print(f"would run {ticker} -> {paths['output_dir']}/ (focus={assignment['focus']})")
        return True

    write_scaffold(assignment, output_dir)
    prompt_file = REPO_ROOT / assignment["prompt_file"]
    template = prompt_file.read_text(encoding="utf-8")
    prompt = append_prose_style(render_prompt(template, assignment, paths))
    meta = {**assignment, **paths}

    cfg = cfg or load_yaml_config()
    if not llm_configured(cfg):
        print("error: configure LLM in .agents-unite/config.yaml or set OPENAI_API_KEY", file=sys.stderr)
        return False

    try:
        data = run_llm(meta, prompt, cfg)
        written = write_outputs(meta, data)
        for p in written:
            print(f"  wrote {p.relative_to(REPO_ROOT)}")
        validate_output(meta)
        print(f"  OK {ticker}")
        return True
    except (LLMError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"  FAIL {ticker}: {exc}", file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch-run research agent on multiple tickers.",
        epilog="Examples:\n"
        "  ./run-batch.sh --tickers NVDA,AMD,GOOGL\n"
        "  ./run-batch.sh --count 5\n"
        "  ./run-batch.sh --count 3 --date 2026-07-11 --dry-run",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--tickers", help="Comma-separated tickers (e.g. NVDA,AMD,GOOGL)")
    parser.add_argument("--count", type=int, default=3, help="Uncovered tickers to pick when --tickers omitted")
    parser.add_argument("--date", help="YYYY-MM-DD (default: today per config)")
    parser.add_argument("--contributor", help="GitHub username override")
    parser.add_argument("--skip-existing", action="store_true", help="Skip tickers with valid reports")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--model", help="Override llm_model from config (e.g. gemma4:latest)")
    parser.add_argument("--max-tokens", type=int, default=8192, help="LLM max_tokens for batch runs")
    args = parser.parse_args()

    cfg_override = load_yaml_config()
    if args.model:
        cfg_override = {**cfg_override, "llm_model": args.model}
    cfg_override = {**cfg_override, "llm_max_tokens": args.max_tokens}

    date = args.date or resolve_investigation_date()
    if args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    else:
        tickers = pick_uncovered(date, args.count)

    if not tickers:
        print("error: no tickers to run", file=sys.stderr)
        return 1

    print(f"Batch research — date={date} tickers={','.join(tickers)}")
    ok = 0
    for ticker in tickers:
        print(f"\n[{ticker}]")
        if run_ticker(
            ticker,
            date,
            contributor=args.contributor,
            skip_existing=args.skip_existing,
            dry_run=args.dry_run,
            cfg=cfg_override,
        ):
            ok += 1

    print(f"\nDone: {ok}/{len(tickers)} succeeded")
    return 0 if ok == len(tickers) else 1


if __name__ == "__main__":
    raise SystemExit(main())
