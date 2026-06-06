# raw/

**Immutable source layer** for the [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern.

| Layer | Path | Who writes |
|-------|------|------------|
| Raw sources | `raw/` (here), `data/` | Humans + contributors |
| Wiki | [`wiki/`](../wiki/) | LLM maintains |
| Schema | [`WIKI.md`](../WIKI.md) | Co-evolved rules |

**Rule:** LLM agents **read** raw files during wiki ingest. They do **not** edit them.

## Files in this folder

| File | Purpose |
|------|---------|
| [`THINKING.md`](THINKING.md) | Product vision, tensions, open questions |
| [`DECISIONS.md`](DECISIONS.md) | Decisions log (fill as we agree) |
| [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md) | Unresolved forks |

When thinking stabilizes → ingest into `wiki/concepts/` via `python3 scripts/wiki_ingest.py` (for `data/`) or manual wiki update (for `raw/`).

Promoted specs live in `docs/`. Compiled knowledge lives in `wiki/`.
