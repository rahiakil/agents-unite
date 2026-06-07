# Millions run market AI alone. Nobody publishes it. History vanishes.

Every day, millions of people ask ChatGPT, Claude, Cursor, or local models:

> "What's the sentiment on NVDA?"
> "Scan Reddit for TSLA."
> "Summarize earnings chatter."

They burn tokens. They get a answer. **Then they close the tab.**

No URL archive. No version history. No way for anyone else to query what people believed on March 12 vs June 6. The work is **private, ephemeral, and lost**.

## The scale problem

- ~4,000 US tickers worth tracking daily
- ~25¢–$2 of LLM tokens per thorough research pass
- **Solo cost to cover the market:** thousands of dollars *per day*
- **Solo timing:** one timezone misses overnight Reddit spikes, foreign open, after-hours filings

Millions do this in parallel, **paying twice for the same ticker**, never sharing results.

## What if the output were public?

Imagine every agent run landing in one Git repo:

```
data/2026-06-06/NVDA/report.alice.md
data/2026-06-06/NVDA/report.bob.md
data/2026-06-06/NVDA/sources.alice.json
```

Suddenly you have **history**. Fork it. Backtest it. Train on it. Ask: *what did agents believe before the last 20 earnings misses?*

That's not a chat session. That's **market memory**.

---

**[agents-unite](https://github.com/rahiakil/agents-unite)** — crowdsourced agentic LLM research in one repo.

Next in series: *Burn pennies, read thousands.*
