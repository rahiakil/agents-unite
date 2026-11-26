"""SQLite and JSONL storage for one study run."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    seed INTEGER,
    provider TEXT,
    model TEXT,
    days INTEGER,
    n_agents INTEGER
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    run_id TEXT,
    record_type TEXT,
    day TEXT,
    contributor TEXT,
    persona TEXT,
    behavior TEXT,
    ticker TEXT,
    stage TEXT,
    passed INTEGER,
    failure_reason TEXT,
    latency_ms REAL,
    payload TEXT
);
"""


class Metrics:
    def __init__(self, outdir: Path, run_id: str, seed: int) -> None:
        self.outdir = outdir
        self.run_id = run_id
        self.seed = seed
        self.events: list[dict] = []
        outdir.mkdir(parents=True, exist_ok=True)

    def add(self, record: dict) -> None:
        record = dict(record)
        record.setdefault("run_id", self.run_id)
        record.setdefault("seed", self.seed)
        self.events.append(record)

    def flush(self, *, provider: str, model: str, days: int, n_agents: int) -> None:
        jsonl = self.outdir / "attempts.jsonl"
        with jsonl.open("w", encoding="utf-8") as handle:
            for event in self.events:
                handle.write(json.dumps(event, sort_keys=True) + "\n")
        db_path = self.outdir / "metrics.db"
        if db_path.exists():
            db_path.unlink()
        conn = sqlite3.connect(db_path)
        conn.executescript(SCHEMA)
        conn.execute(
            "INSERT INTO runs (run_id, seed, provider, model, days, n_agents) VALUES (?, ?, ?, ?, ?, ?)",
            (self.run_id, self.seed, provider, model, days, n_agents),
        )
        conn.executemany(
            """
            INSERT INTO events (
                run_id, record_type, day, contributor, persona, behavior, ticker,
                stage, passed, failure_reason, latency_ms, payload
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    event.get("run_id"),
                    event.get("record_type"),
                    event.get("day"),
                    event.get("contributor"),
                    event.get("persona"),
                    event.get("behavior"),
                    event.get("ticker"),
                    event.get("stage"),
                    None if event.get("passed") is None else int(bool(event.get("passed"))),
                    event.get("failure_reason") or "",
                    event.get("latency_ms"),
                    json.dumps(event, sort_keys=True),
                )
                for event in self.events
            ],
        )
        conn.commit()
        conn.close()
