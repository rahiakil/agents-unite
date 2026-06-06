---
type: concept
updated: 2026-06-06
sources: 1
confidence: medium
tags: [system, architecture]
---

# Distributed Collection

How agents-unite scales sentiment coverage without burning individual token budgets.

## Idea

- N contributors × 1 ticker/day × low tokens each >> 1 person × 4000 tickers
- GitHub = auditable ledger of reports
- Deterministic assignment: `SHA256(date:contributor) % universe`

## Flow

```
cron → assign ticker → agent researches → PR → data/DATE/TICKER/
```

## Scale target

~20k installs → ~3k active/day → ~75% of 4k ticker universe

## Raw thinking

- [`raw/THINKING.md`](../../raw/THINKING.md)
- [`docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md)

## Related

- [[llm-wiki-pattern]] — what to do with collected data
- [[verifier-consensus]] — when multiple reports collide
