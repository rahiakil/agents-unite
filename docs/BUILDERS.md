# Build on agents-unite

**For algo traders, agentic trading systems, RAG pipelines, and quant researchers** who want an open, growing market memory layer — not another closed terminal.

> Markets Change. Memory Compounds.

## What you get

| Asset | Path | Use |
|-------|------|-----|
| Daily reports | `data/YYYY-MM-DD/TICKER/report*.md` | NLP, sentiment, RAG chunks |
| Structured sources | `sources*.json` | URL graphs, citation audit |
| Consensus | `consensus.md` | Canonical daily signal per ticker |
| Verifications | `verification*.md` | Quality-weighting, reputation |
| Universe | `tickers/universe.json` | Coverage map, sector filters |
| Live stats | README + `data/_index/` | Dashboards, monitoring |

**License:** MIT — fork, commercialize downstream tools, ship products. Data is public; verify claims yourself. Not investment advice.

## Quick consume (Python)

```bash
pip install -r requirements-llm.txt   # optional pyyaml only for config
python3 examples/load_reports.py --ticker NVDA --last 30
python3 examples/load_reports.py --json > nvda_sentiment.jsonl
```

See [`examples/load_reports.py`](../examples/load_reports.py).

## Build ideas (lucrative / high-value downstream)

These are **not** in-repo products — they're what the ecosystem can ship on top of free data:

| Idea | Who pays | Hook into agents-unite |
|------|----------|------------------------|
| **Sentiment backtest SaaS** | Quants | `load_reports.py` → signal series → your backtest engine |
| **Agent orchestration host** | Teams | Run our harness + your API keys at scale |
| **RAG terminal for stocks** | Prosumer | Embed `data/` + wiki in vector DB |
| **Contributor reputation index** | Funds | Track `github_username` vs later price moves |
| **Sector heatmap API** | Media / apps | Aggregate README live stats + `_index/` |
| **Alert bot** | Traders | Webhook on new PRs for watchlist tickers |
| **Fine-tune dataset** | ML shops | Export JSONL with sources as labels |
| **Verification marketplace** | Platforms | Stake on `verification*.md` accuracy |

**Moat for builders:** early integrations become the default tooling as history grows. First good charting layer, first good backtest adapter, first mobile app — wins attention while data is still sparse.

## Agentic trading stack

```
agents-unite (collect)  →  your strategy agent  →  paper/live broker API
        ↑                           ↑
   cron + harness              reads data/ + consensus
```

1. **Collect** — contributors (or your cron) fill `data/`
2. **Verify / consensus** — quality layer ([ROLES.md](ROLES.md))
3. **Your agent** — LangGraph, AutoGen, custom: reads latest `consensus.md` + reports
4. **Execute** — your risk layer; we don't touch orders

Adapters: [HARNESS.md](HARNESS.md) · plug your runtime via `scripts/adapters/`

## Algo trading / quant patterns

### Signal from sentiment time series

```python
from examples.load_reports import load_reports

rows = load_reports(ticker="AAPL", last_n_days=60)
scores = [r["sentiment_score"] for r in rows if r["sentiment_score"] is not None]
# z-score, momentum, cross with your price feed
```

### Event study

Join report dates to your price CSV; measure forward returns when `sentiment_score` crosses thresholds. Contributor disagreement (`consensus.md` Divergence) = natural regime flag.

### Alternative data bundle

Export nightly:

```bash
python3 examples/load_reports.py --json --since 2025-01-01 > export/sentiment.jsonl
```

Ship to S3, BigQuery, or DuckDB — your infra.

### Multi-agent ensemble

Weight reports by `contributor_hash` after you score historical accuracy — precursor to Phase 4 reputation ([TRADING.md](TRADING.md)).

## RAG / LLM apps

```text
Chunk: data/DATE/TICKER/report.user.md
Metadata: ticker, date, sentiment_score, source URLs from JSON
Retrieve: "bearish social before earnings misses" → hybrid search
```

Wiki layer: [WIKI.md](../WIKI.md) · `wiki/` for compiled memory.

## GitHub integrations

| Integration | How |
|-------------|-----|
| **Watch repo** | New PRs = new data points |
| **GitHub Action** | Pull `data/` on schedule ([example in examples/](../examples/github-action-sync.yml)) |
| **Fork + private signals** | Public data, proprietary strategy on top |
| **Builder showcase issue** | Get listed below |

## Showcase (add yours)

Open a [builder showcase issue](../.github/ISSUE_TEMPLATE/builder_showcase.yml) with:

- Project name + link
- What you built (backtest, bot, dashboard, dataset export)
- How you use `data/`

*No projects listed yet — be the first.*

## SEO / discovery

Taglines and keywords: [TAGLINES.md](TAGLINES.md)  
GitHub topics: [.github/TOPICS.md](../.github/TOPICS.md)

## Contribute upstream

| Contribution | Path |
|--------------|------|
| New agent adapter | `scripts/adapters/` |
| Export / ETL script | `examples/` |
| Schema extension | issue first — keep core stable |
| Daily report | `data/` via PR |

[CONTRIBUTING.md](../CONTRIBUTING.md) · [HARNESS.md](HARNESS.md)
