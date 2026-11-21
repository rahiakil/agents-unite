"""Append-only study archive.

Each run writes a new file under history/runs. Existing JSONL files are never opened for write.
`summary.json` is a derived rollup and may be replaced.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from sim.summarize import build_summary


def load_events(path: Path) -> list[dict]:
    files: list[Path]
    if path.is_file():
        files = [path]
    else:
        files = sorted(path.rglob("*.jsonl"))
    events: list[dict] = []
    for file in files:
        for line in file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))
    return events


def append_run(history: Path, events: list[dict], run_id: str) -> Path:
    runs = history / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    target = runs / f"{stamp}-{run_id}.jsonl"
    suffix = 0
    while target.exists():
        suffix += 1
        target = runs / f"{stamp}-{run_id}-{suffix}.jsonl"
    fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
    summary = build_summary(load_events(history))
    (history / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return target
