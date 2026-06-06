# RAG, Knowledge Graph & Synthesis

How raw daily reports become **retrievable collective memory** — and eventually **consensus-aware research**.

**Status:** Phase 1 stores raw markdown on Git. Phases 2–4 add embeddings, graph, and synthesis. This doc describes the intended pipeline and how it connects to consensus.

## The pipeline

```
Ticker assignment
      ↓
Daily reports (PRs → data/DATE/TICKER/)
      ↓
Embeddings + index
      ↓
Knowledge graph (wiki/)
      ↓
Consensus engine
      ↓
LLM synthesis → research briefs
```

PRs are the ** ingestion layer**. Everything downstream reads `data/` without modifying it.

## Layer 1 — Raw ledger (now)

- Immutable markdown + JSON in `data/`
- Git history = audit trail of what people believed and when
- [LLM Wiki](../WIKI.md): Karpathy pattern — agents compile `wiki/` from raw sources

```bash
python3 scripts/wiki_ingest.py --prompt   # next pending report → wiki pages
python3 scripts/wiki_search.py "NVDA capex"
```

## Layer 2 — Embeddings & semantic agreement (planned)

When many analyses independently say:

> Revenue growth slowing because hyperscaler capex is flattening

their embeddings should **cluster**. That cluster strength becomes a **semantic consensus signal** — richer than averaging scalar sentiment scores.

| Signal | Method |
|--------|--------|
| Scalar agreement | Weighted median of `sentiment_score` — [CONSENSUS.md](CONSENSUS.md) |
| Theme agreement | Embedding cosine similarity across Key Themes sections |
| Source overlap | Jaccard on normalized URLs across `sources.json` files |

High cluster density + high reputation weight → elevated confidence in `consensus.md`.

## Layer 3 — Market memory graph

Nodes (wiki pages + future graph store):

```
Ticker · Quarter · Earnings · Theme · Competitor · Macro factor · Article · Analysis · Contributor
```

Example relationships:

```
NVDA ── linked to ── AI capex
     ── linked to ── AMD, TSMC
     ── linked to ── hyperscaler spending
```

After years of daily commits, this becomes a **longitudinal knowledge graph** — the moat is history, not code.

Browse seed graph: [`wiki/index.md`](../wiki/index.md)

## Layer 4 — RAG for future agents

Future agents query:

> "Show every bearish signal identified before the last 20 earnings disappointments."

Retrieval path:

1. Hybrid search over `wiki/` + embedded chunks of `data/`
2. Filter by ticker, date range, contributor reputation
3. Rank by semantic relevance + recency + accuracy weight
4. Synthesize with citations to raw paths (`data/2025-11-01/NVDA/report.user.md`)

Tools at scale: local hybrid search (e.g. [qmd](https://github.com/tobi/qmd)) — see [WIKI.md](../WIKI.md).

## Layer 5 — LLM synthesis

Output types (future):

| Artifact | Input | Output |
|----------|-------|--------|
| Daily brief | All reports for DATE | `data/_index/summary-DATE.md` (partial today) |
| Ticker rollup | All dates for TICKER | `wiki/tickers/TICKER.md` |
| Consensus | N reports same folder | `consensus.md` |
| Research report | Graph + RAG retrieval | `wiki/synthesis/*.md` |

Prompts: `agents/wiki-ingest.md`, `agents/consensus.md`, future `agents/synthesis.md`.

## Connection to consensus scoring

Consensus is **not** simple voting:

1. **Validate** — schema pass only
2. **Outlier reject** — MAD filter when n ≥ 3
3. **Weighted median** — reputation-weighted in v3+
4. **Semantic cluster** — theme embedding agreement (v3+)
5. **Confidence label** — `high` / `medium` / `low` from spread + n

Verifiers write human-readable reconciliation in `consensus.md`; batch jobs can pre-compute scores.

See [CONSENSUS.md](CONSENSUS.md), [METHODS.md](METHODS.md).
