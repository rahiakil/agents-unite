"""CLI for the seeded proof run and the daily archive run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sim.archive import append_run, load_events
from sim.harness import run_simulation
from sim.summarize import check_summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the agents-unite trust study.")
    parser.add_argument("--days", type=int, default=6)
    parser.add_argument("--seed", type=int, default=20261121)
    parser.add_argument("--start", default=None)
    parser.add_argument("--provider", default="rule")
    parser.add_argument("--llm-cap", type=int, default=0)
    parser.add_argument("--universe", choices=["liquid", "all"], default="liquid")
    parser.add_argument("--outdir", type=Path, default=None)
    parser.add_argument("--history", type=Path, default=None)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--daily", action="store_true", help="One day, auto provider, append to --history.")
    args = parser.parse_args(argv)
    provider = args.provider
    llm_cap = args.llm_cap
    days = args.days
    if args.daily:
        days = 1
        if provider == "rule" and args.provider == "rule":
            provider = "auto"
        if llm_cap == 0:
            llm_cap = 11
    summary = run_simulation(
        seed=args.seed,
        days=days,
        start=args.start,
        provider_name=provider,
        llm_cap=llm_cap,
        universe=args.universe,
        outdir=args.outdir,
    )
    if args.history is not None:
        outdir = args.outdir or Path(__file__).resolve().parent
        events = load_events(outdir / "attempts.jsonl")
        path = append_run(args.history, events, summary["run_id"])
        print(f"archived {path}")
    problems = check_summary(summary) if args.check else []
    print(
        json.dumps(
            {
                "chain_attempts": summary["chain_attempts"],
                "false_accepts": summary["false_accepts"],
                "false_rejects": summary["false_rejects"],
                "consensus_mae": summary["consensus_mae"],
                "problems": problems,
            },
            indent=2,
        )
    )
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
