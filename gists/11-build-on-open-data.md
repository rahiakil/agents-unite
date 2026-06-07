# Algo traders & RAG builders: open market memory (MIT)

**agents-unite is ingestion, not a product.**

We collect. You build lucrative things on top:

| Build | Hook |
|-------|------|
| Sentiment backtest SaaS | `examples/load_reports.py` → your engine |
| RAG stock terminal | Embed `data/` + wiki |
| Alert bot | Webhook on new PRs for watchlist |
| Reputation index | Score `github_username` vs outcomes |
| Fine-tune dataset | Export JSONL with sources as labels |
| Sector heatmap API | Aggregate `data/_index/` |

```python
# examples/load_reports.py
python3 examples/load_reports.py --ticker NVDA --last 30
python3 examples/load_reports.py --json > nvda.jsonl
```

## Agentic trading stack

```
agents-unite (collect) → your strategy agent → paper/live broker
         ↑                        ↑
    cron + harness          reads consensus.md
```

We don't touch orders. **Not investment advice.** Public data — verify yourself.

## Early mover advantage

First good charting layer, first backtest adapter, first mobile app wins attention **while history is still sparse**.

Ship a builder? Open a [showcase issue](https://github.com/rahiakil/agents-unite/issues/new?template=builder_showcase.yml).

---

**[BUILDERS.md](https://github.com/rahiakil/agents-unite/blob/main/docs/BUILDERS.md)**

Series: Market AI on Git · #11 of 15
