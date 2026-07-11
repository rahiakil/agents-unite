#!/usr/bin/env python3
"""agents-unite CLI — pip-installable entry point for repo scripts."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from agents_unite import __version__
from agents_unite.paths import repo_root, script_path


def _python(root: Path) -> str:
    venv = root / ".venv" / "bin" / "python"
    if venv.is_file():
        return str(venv)
    return os.environ.get("AGENTS_UNITE_PYTHON", sys.executable)


def _run(root: Path, script: str, *args: str, check: bool = True) -> int:
    env = {**os.environ, "REPO_ROOT": str(root), "AGENTS_UNITE_ROOT": str(root)}
    cmd = [_python(root), str(script_path(root, script)), *args]
    return subprocess.run(cmd, cwd=root, env=env, check=check).returncode


def _shell(root: Path, rel: str, *args: str) -> int:
    path = root / rel
    if not path.is_file():
        raise SystemExit(f"Missing: {path}")
    env = {**os.environ, "REPO_ROOT": str(root)}
    return subprocess.run(["bash", str(path), *args], cwd=root, env=env, check=False).returncode


def cmd_version(_: argparse.Namespace) -> int:
    print(f"agents-unite {__version__}")
    try:
        root = repo_root()
        print(f"repo: {root}")
    except SystemExit:
        pass
    return 0


def cmd_assign(args: argparse.Namespace) -> int:
    root = repo_root()
    argv = ["--json"]
    if args.date:
        argv.extend(["--date", args.date])
    if args.role:
        argv.extend(["--force-role", args.role])
    return _run(root, "assign_role.py", *argv, check=False)


def cmd_validate(args: argparse.Namespace) -> int:
    root = repo_root()
    target = args.path
    if not target.endswith("/"):
        target += "/"
    return _run(root, "validate_report.py", target, check=False)


def cmd_run(args: argparse.Namespace) -> int:
    root = repo_root()
    if args.assign:
        rc = _run(root, "run_agent.py", "--assign", check=False)
    else:
        rc = _shell(root, "scripts/run-agent.sh", "--run")
    return rc


def cmd_research(args: argparse.Namespace) -> int:
    """Direct human-triggered research for one or more tickers (bypasses daily assignment)."""
    root = repo_root()
    argv: list[str] = []
    if args.tickers:
        argv += ["--tickers", ",".join(t.strip().upper() for t in args.tickers)]
    else:
        argv += ["--count", str(args.count)]
    if args.date:
        argv += ["--date", args.date]
    if args.model:
        argv += ["--model", args.model]
    if args.contributor:
        argv += ["--contributor", args.contributor]
    if args.skip_existing:
        argv += ["--skip-existing"]
    if args.dry_run:
        argv += ["--dry-run"]
    if args.max_tokens:
        argv += ["--max-tokens", str(args.max_tokens)]
    return _run(root, "run_batch.py", *argv, check=False)


def cmd_coverage(args: argparse.Namespace) -> int:
    """Show which tickers are covered / uncovered for a date."""
    root = repo_root()
    argv = []
    if args.date:
        argv += ["--date", args.date]
    if args.uncovered:
        argv += ["--uncovered"]
    return _run(root, "coverage_report.py", *argv, check=False)


def cmd_daily(_: argparse.Namespace) -> int:
    return _shell(repo_root(), "scripts/daily-run.sh")


def cmd_configure(_: argparse.Namespace) -> int:
    return _run(repo_root(), "configure_llm.py", check=False)


def cmd_init(args: argparse.Namespace) -> int:
    root = repo_root(Path(args.directory) if args.directory else Path.cwd())
    os.environ["AGENTS_UNITE_ROOT"] = str(root)
    print(f"Initializing in {root}")
    config = root / ".agents-unite" / "config.yaml"
    example = root / "config" / "config.example.yaml"
    if not config.is_file() and example.is_file():
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Created {config}")
    cron_env = root / ".agents-unite" / "cron.env"
    cron_example = root / "config" / "cron.env.example"
    if not cron_env.is_file() and cron_example.is_file():
        cron_env.write_text(cron_example.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Created {cron_env} — add API keys for unattended cron")
    print("\nNext:")
    print(f"  cd {root}")
    print("  pip install -e '.[llm]'   # or: pip install 'agents-unite[llm]'")
    print("  agents-unite configure      # pick LLM (Ollama / OpenAI) + API key")
    print("  agents-unite research NVDA  # test one ticker")
    print("  agents-unite daily          # cron-style: assign → PR")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agents-unite",
        description="Git-native market research ledger — assign, run agents, validate, daily cron.",
        epilog=(
            "Common flows:\n"
            "  agents-unite init                       set up local config\n"
            "  agents-unite configure                  pick LLM + API key (after pip install)\n"
            "  agents-unite daily                      run today's assigned ticker + open PR (cron uses this)\n"
            "  agents-unite research NVDA              cover a specific ticker on demand\n"
            "  agents-unite research NVDA AMD GOOGL    cover several tickers now\n"
            "  agents-unite research --count 5         cover 5 least-covered tickers today\n"
            "  agents-unite coverage --uncovered       list tickers with no report today\n"
            "\nRun 'agents-unite <command> --help' for command-specific options."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    sub.add_parser("version", help="Print package and repo version").set_defaults(func=cmd_version)

    p_init = sub.add_parser("init", help="Create .agents-unite/config from examples")
    p_init.add_argument("directory", nargs="?", help="Repo directory (default: cwd)")
    p_init.set_defaults(func=cmd_init)

    sub.add_parser("configure", help="Interactive LLM + API key setup after pip install").set_defaults(
        func=cmd_configure
    )

    p_assign = sub.add_parser("assign", help="Assign today's role and ticker (JSON)")
    p_assign.add_argument("--date")
    p_assign.add_argument("--role", dest="role")
    p_assign.set_defaults(func=cmd_assign)

    p_run = sub.add_parser("run", help="Run investigation agent harness")
    p_run.add_argument("--assign", action="store_true", help="Assign + scaffold before run")
    p_run.set_defaults(func=cmd_run)

    p_research = sub.add_parser(
        "research",
        help="Directly research specific ticker(s) on demand (human-triggered)",
        description="Run the research agent for tickers you choose, e.g. to fill a coverage gap.",
        epilog=(
            "Examples:\n"
            "  agents-unite research NVDA\n"
            "  agents-unite research NVDA AMD GOOGL --model gemma4:latest\n"
            "  agents-unite research --count 5 --skip-existing\n"
            "  agents-unite research TSLA --date 2026-07-11 --dry-run"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_research.add_argument("tickers", nargs="*", help="Ticker symbols (e.g. NVDA AMD). Omit to use --count.")
    p_research.add_argument("--count", type=int, default=3, help="Least-covered tickers to pick when none given")
    p_research.add_argument("--date", help="YYYY-MM-DD (default: today)")
    p_research.add_argument("--model", help="Override llm_model (e.g. gemma4:latest, gpt-4o-mini)")
    p_research.add_argument("--contributor", help="GitHub username override")
    p_research.add_argument("--skip-existing", action="store_true", help="Skip tickers with valid reports")
    p_research.add_argument("--max-tokens", type=int, help="LLM max_tokens (default 8192 for batch)")
    p_research.add_argument("--dry-run", action="store_true", help="Show plan, no LLM call")
    p_research.set_defaults(func=cmd_research)

    p_cov = sub.add_parser("coverage", help="Show covered / uncovered tickers for a date")
    p_cov.add_argument("--date", help="YYYY-MM-DD (default: today)")
    p_cov.add_argument("--uncovered", action="store_true", help="List only tickers with no report")
    p_cov.set_defaults(func=cmd_coverage)

    sub.add_parser("daily", help="Full daily pipeline (assign → agent → validate → PR)").set_defaults(
        func=cmd_daily
    )

    p_val = sub.add_parser("validate", help="Validate a report directory")
    p_val.add_argument("path", help="e.g. data/2026-07-11/TICKER/")
    p_val.set_defaults(func=cmd_validate)

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
