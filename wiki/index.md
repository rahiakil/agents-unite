# Wiki Index

> Catalog of the agents-unite second brain. Updated by the LLM on ingest.  
> See [`WIKI.md`](../WIKI.md) for maintainer rules.

**Last updated:** 2026-06-06

---

## Synthesis

| Page | Summary |
|------|---------|
| [overview.md](overview.md) | Rolling market mood and cross-ticker thesis |
| [log.md](log.md) | Chronological ingest / query / lint timeline |

---

## Tickers

| Ticker | Latest score | Date | Mood |
|--------|--------------|------|------|
| [AAPL](tickers/AAPL.md) | +0.62 | 2026-06-05 | 🟢 bullish |
| [NVDA](tickers/NVDA.md) | +0.84 | 2026-06-05 | 🟢 bullish |
| [TSLA](tickers/TSLA.md) | −0.28 | 2026-06-05 | 🔴 bearish |

---

## Days

| Date | Reports | Avg sentiment |
|------|---------|---------------|
| [2026-06-05](days/2026-06-05.md) | 3 | +0.39 |

---

## Themes

| Theme | Summary |
|-------|---------|
| [ai-capex](themes/ai-capex.md) | Hyperscaler AI spend, GPU supply, NVDA linkage |
| [on-device-ai](themes/on-device-ai.md) | Edge AI, WWDC, consumer upgrade cycles |

---

## Concepts (system + market)

| Concept | Summary |
|---------|---------|
| [distributed-collection](concepts/distributed-collection.md) | One agent, one ticker, git as ledger |
| [verifier-consensus](concepts/verifier-consensus.md) | Multi-report reconciliation, proof-of-stake sketch |
| [llm-wiki-pattern](concepts/llm-wiki-pattern.md) | Karpathy second brain — raw → wiki → query |

---

## Raw sources (read only — do not edit via wiki)

| Path | Role |
|------|------|
| `data/YYYY-MM-DD/TICKER/` | Daily contributor sentiment reports |
| `raw/THINKING.md` | Product vision scratchpad |
| `docs/CONSENSUS.md` | Future consensus spec |

---

## Quick commands

```bash
python3 scripts/wiki_ingest.py              # pending ingests
python3 scripts/wiki_ingest.py --prompt     # next ingest prompt
python3 scripts/wiki_search.py "NVDA"       # search wiki
```
