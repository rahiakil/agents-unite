---
type: concept
updated: 2026-06-06
sources: 0
confidence: high
tags: [system, wiki, meta]
---

# LLM Wiki Pattern

Karpathy's three-layer second brain — adapted for agents-unite.

## Layers

| Layer | Path | Mutable? |
|-------|------|----------|
| Raw | `data/`, `raw/` | No (read only) |
| Wiki | `wiki/` | LLM maintains |
| Schema | `WIKI.md` | Co-evolved |

Source: [Karpathy gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

## Operations

- **Ingest** — new `data/` report → update ticker/day/theme pages
- **Query** — ask trends; cite wiki + raw
- **Lint** — contradictions, orphans, stale claims

## Why not RAG-only?

Wiki **compounds** — cross-links and synthesis persist. RAG rediscovers every query.

At our scale (~hundreds of pages), `wiki/index.md` + search is enough.

## Commands

```bash
python3 scripts/wiki_ingest.py --prompt
python3 scripts/wiki_search.py "query"
```

## Related

- [[distributed-collection]] — fills raw layer
- [`WIKI.md`](../../WIKI.md) — full schema
