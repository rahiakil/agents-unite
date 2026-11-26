"""Learnings report for a date range. Used on a 15-day cadence."""

from __future__ import annotations

import argparse
from pathlib import Path

from sim.archive import load_events
from sim.summarize import build_summary, render_results


def filter_events(events: list[dict], start: str | None, end: str | None) -> list[dict]:
    chosen = []
    for event in events:
        day = event.get("day")
        if not day:
            chosen.append(event)
            continue
        if start and day < start:
            continue
        if end and day > end:
            continue
        chosen.append(event)
    return chosen


def distinct_days(events: list[dict]) -> list[str]:
    return sorted({event["day"] for event in events if event.get("day")})


def write_report(events: list[dict], dest: Path, *, start: str | None, end: str | None) -> Path:
    summary = build_summary(events)
    summary["seed"] = "archive"
    summary["provider"] = "mixed"
    summary["model"] = "mixed"
    summary["n_agents"] = len({event.get("contributor") for event in events if event.get("contributor")})
    summary["days"] = len(distinct_days(events))
    summary["start"] = start or (distinct_days(events)[:1] or [""])[0]
    summary["market_asof"] = "see attempts"
    body = render_results(summary)
    note = [
        "",
        "## Paper 2 notes",
        "",
        "This file is the learnings rollup for the archived runs in the selected dates.",
        "Forward-return pairs stay at zero until a later market snapshot contains the next close for that ticker.",
        "Persona, prompt id, prompt hash, focus mode, provider, and model are on every submission row.",
        "Simulated usernames start with sim-. Human reports on main do not, and they do not carry simulated: true.",
        "",
    ]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(body + "\n".join(note), encoding="utf-8")
    return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write a learnings report from the study archive.")
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--from", dest="start", default=None)
    parser.add_argument("--to", dest="end", default=None)
    parser.add_argument("--every", type=int, default=0, help="Write only when distinct days is a multiple of this number.")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    events = filter_events(load_events(args.history), args.start, args.end)
    days = distinct_days(events)
    if args.every and not args.force and (not days or len(days) % args.every != 0):
        print(f"learnings not due: {len(days)} distinct days, cadence {args.every}")
        return 0
    end = args.end or (days[-1] if days else "empty")
    dest = args.out or (args.history / "learnings" / f"{end}.md")
    path = write_report(events, dest, start=args.start, end=args.end)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
