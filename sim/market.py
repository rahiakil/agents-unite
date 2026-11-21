#!/usr/bin/env python3
"""Load real batch and ledger inputs for the study.

Search order, later rows win on the same (date, ticker):

1. sim/fixtures/batch-*.json committed snapshots
2. data/ in the repo (main ledger)
3. any extra directory passed in (the sim-data history/market folder)

A snapshot stores close, change, volume, and the headline or post list.
Personas read those. They do not invent a price when a real row exists.

`python3 -m sim.market refresh` rebuilds a snapshot from a git ref that
holds data/YYYY-MM-DD/TICKER/ batch files.
"""

from __future__ import annotations

import io
import json
import subprocess
import tarfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "sim" / "fixtures"
UNIVERSE_PATH = REPO_ROOT / "tickers" / "universe.json"

LABELS = {
    "bullish": 1.0,
    "positive": 1.0,
    "bearish": -1.0,
    "negative": -1.0,
    "neutral": 0.0,
}
POSITIVE_WORDS = ("beat", "surge", "rally", "upgrade", "record", "growth", "jump", "soar")
NEGATIVE_WORDS = (
    "drop",
    "miss",
    "plunge",
    "probe",
    "selloff",
    "sell-off",
    "lawsuit",
    "rout",
    "turmoil",
    "downgrade",
    "cut",
    "fall",
    "slump",
    "probe",
)
ALLOWED_TYPES = {"twitter", "reddit", "news", "other"}


def sectors_by_ticker() -> dict[str, str]:
    if not UNIVERSE_PATH.is_file():
        return {}
    data = json.loads(UNIVERSE_PATH.read_text(encoding="utf-8"))
    return {
        str(item.get("ticker", "")).upper(): str(item.get("sector") or "")
        for item in data.get("tickers") or []
    }


def _num(raw: str) -> float | None:
    text = raw.strip().replace(",", "").replace("%", "").replace("~", "").replace("$", "")
    if not text or text.upper() in {"N/A", "NA", "NONE"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_price_table(text: str) -> dict[str, float | None]:
    found: dict[str, str] = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[0]) <= {"-", ":"}:
            continue
        found[cells[0].lower()] = cells[1]
    return {
        "close": _num(found.get("close", "")) or _num(found.get("price", "")),
        "prev_close": _num(found.get("prev close", "")),
        "change_pct": _num(found.get("change %", "")),
        "volume": _num(found.get("volume", "")),
    }


def _front_score(text: str) -> float | None:
    for line in text.splitlines():
        if line.startswith("sentiment_score:"):
            return _num(line.split(":", 1)[1])
    return None


def map_type(raw: str | None) -> str:
    token = (raw or "").strip().lower()
    if token in {"twitter", "x", "tweet"}:
        return "twitter"
    if token == "reddit":
        return "reddit"
    if token == "news":
        return "news"
    return "other"


def lexicon_tone(text: str) -> float | None:
    lowered = text.lower()
    pos = sum(1 for word in POSITIVE_WORDS if word in lowered)
    neg = sum(1 for word in NEGATIVE_WORDS if word in lowered)
    if pos == neg == 0:
        return None
    if pos + neg == 0:
        return None
    return (pos - neg) / (pos + neg)


def source_tone(source: dict) -> float | None:
    label = str(source.get("sentiment") or "").lower()
    if label in LABELS:
        return LABELS[label]
    return lexicon_tone(" ".join(str(source.get(key) or "") for key in ("title", "snippet", "summary")))


def mean_tone(sources: list[dict], types: set[str] | None = None) -> float | None:
    values = []
    for source in sources:
        if types is not None and source.get("type") not in types:
            continue
        tone = source.get("tone")
        if tone is None:
            tone = source_tone(source)
        if tone is not None:
            values.append(float(tone))
    if not values:
        return None
    return sum(values) / len(values)


def _normalize_source(raw: dict) -> dict | None:
    url = str(raw.get("url") or "").strip()
    if not url:
        return None
    item = {
        "type": map_type(str(raw.get("type") or "other")),
        "url": url[:500],
        "title": str(raw.get("title") or raw.get("snippet") or "")[:240],
        "sentiment": str(raw.get("sentiment") or "").lower(),
    }
    tone = source_tone(item)
    if tone is not None:
        item["tone"] = round(tone, 4)
    if item["type"] not in ALLOWED_TYPES:
        item["type"] = "other"
    return item


def row_from_files(report_text: str, sources_doc: dict | None, *, date: str, ticker: str, origin: str) -> dict:
    prices = parse_price_table(report_text)
    sources = []
    if isinstance(sources_doc, dict):
        for raw in sources_doc.get("sources") or []:
            if isinstance(raw, dict):
                item = _normalize_source(raw)
                if item:
                    sources.append(item)
    news = mean_tone(sources, {"news"})
    social = mean_tone(sources, {"twitter", "reddit"})
    return {
        "date": date,
        "ticker": ticker.upper(),
        "origin": origin,
        "close": prices["close"],
        "prev_close": prices["prev_close"],
        "change_pct": prices["change_pct"],
        "volume": prices["volume"],
        "ledger_sentiment": _front_score(report_text),
        "news_tone": None if news is None else round(news, 4),
        "social_tone": None if social is None else round(social, 4),
        "sources": sources,
        "sector": "",
    }


def rows_from_tree(root: Path, *, origin: str) -> list[dict]:
    rows: dict[tuple[str, str], dict] = {}
    if not root.is_dir():
        return []
    for report in root.glob("data/*/*/report*.md"):
        if report.parent.parent.name.startswith("_"):
            continue
        parts = report.parts
        try:
            data_at = parts.index("data")
        except ValueError:
            continue
        if len(parts) < data_at + 4:
            continue
        date = parts[data_at + 1]
        ticker = parts[data_at + 2]
        if date.startswith("_") or ticker.startswith("_"):
            continue
        sources_doc = None
        slug = ""
        name = report.name
        if name.startswith("report.") and name.endswith(".md"):
            slug = name[len("report.") : -len(".md")]
        candidates = []
        if slug:
            candidates.append(report.parent / f"sources.{slug}.json")
        candidates.append(report.parent / "sources.json")
        for candidate in candidates:
            if candidate.is_file():
                try:
                    sources_doc = json.loads(candidate.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    sources_doc = None
                break
        row = row_from_files(
            report.read_text(encoding="utf-8"),
            sources_doc,
            date=date,
            ticker=ticker,
            origin=origin,
        )
        key = (row["date"], row["ticker"])
        # Prefer the row with more sources when several reports share a folder.
        current = rows.get(key)
        if current is None or len(row["sources"]) > len(current["sources"]):
            rows[key] = row
    return list(rows.values())


def _attach_sectors(rows: list[dict]) -> None:
    sectors = sectors_by_ticker()
    for row in rows:
        row["sector"] = sectors.get(row["ticker"], "")


def load_snapshot_file(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("tickers") if isinstance(data, dict) else data
    if not isinstance(rows, list):
        return []
    cleaned = []
    for row in rows:
        if not isinstance(row, dict) or not row.get("ticker") or not row.get("date"):
            continue
        row = dict(row)
        row["ticker"] = str(row["ticker"]).upper()
        row.setdefault("origin", "snapshot")
        row.setdefault("sources", [])
        cleaned.append(row)
    return cleaned


def load_panel(*extra_dirs: Path) -> dict[tuple[str, str], dict]:
    """Merge fixtures, the main data/ tree, and optional extra market dirs."""
    panel: dict[tuple[str, str], dict] = {}

    def put(rows: list[dict]) -> None:
        for row in rows:
            panel[(row["date"], row["ticker"])] = row

    if FIXTURE_DIR.is_dir():
        for path in sorted(FIXTURE_DIR.glob("batch-*.json")):
            put(load_snapshot_file(path))
    put(rows_from_tree(REPO_ROOT, origin="data"))
    for extra in extra_dirs:
        if extra is None:
            continue
        if extra.is_file() and extra.suffix == ".json":
            put(load_snapshot_file(extra))
            continue
        for path in sorted(Path(extra).glob("batch-*.json")):
            put(load_snapshot_file(path))
        put(rows_from_tree(Path(extra), origin="history"))
    _attach_sectors(list(panel.values()))
    return panel


def write_snapshot(rows: list[dict], path: Path, *, source: str) -> None:
    _attach_sectors(rows)
    payload = {
        "version": 1,
        "source": source,
        "ticker_count": len(rows),
        "tickers": sorted(rows, key=lambda row: (row["date"], row["ticker"])),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def snapshot_from_git(ref: str, dest: Path) -> int:
    """Build a compact snapshot from a git ref that contains data/."""
    archive = subprocess.run(
        ["git", "archive", ref, "data"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as bundle:
            bundle.extractall(tmp)
        rows = rows_from_tree(Path(tmp), origin="batch")
    write_snapshot(rows, dest, source=ref)
    return len(rows)


def liquid_tickers(panel: dict[tuple[str, str], dict], day: str, limit: int = 8) -> list[str]:
    """High-volume names on `day` that also have at least two real sources."""
    preferred = ["NVDA", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "TSLA", "AMD", "AVGO", "JPM"]
    rows = [row for (date, _ticker), row in panel.items() if date == day and len(row.get("sources") or []) >= 2]
    by_ticker = {row["ticker"]: row for row in rows}
    chosen = [ticker for ticker in preferred if ticker in by_ticker]
    if len(chosen) < limit:
        rest = sorted(by_ticker, key=lambda ticker: (-(by_ticker[ticker].get("volume") or 0), ticker))
        for ticker in rest:
            if ticker not in chosen:
                chosen.append(ticker)
            if len(chosen) >= limit:
                break
    return chosen[:limit]


def latest_market_date(panel: dict[tuple[str, str], dict]) -> str | None:
    dates = sorted({date for date, _ticker in panel})
    return dates[-1] if dates else None


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Refresh or inspect the market panel.")
    parser.add_argument("command", choices=["refresh", "summary"])
    parser.add_argument("--ref", default="origin/batch-2026-11-20")
    parser.add_argument("--dest", type=Path, default=FIXTURE_DIR / "batch-2026-11-20.json")
    args = parser.parse_args()
    if args.command == "refresh":
        count = snapshot_from_git(args.ref, args.dest)
        print(f"wrote {count} tickers to {args.dest}")
        return 0
    panel = load_panel()
    print(json.dumps({"rows": len(panel), "latest": latest_market_date(panel)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
