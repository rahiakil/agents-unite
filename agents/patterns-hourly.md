# Hourly trading patterns agent

Append **hourly cross-ticker pattern shards** for agentic trading and dashboard consumers.

## Trigger

- Cron: `0 * * * *` UTC on pattern nodes
- Runs independently of contributor research wakes

## Input

- Reports + consensus from last 24–48h under `data/`
- Prior hour file if exists: `data/_patterns/hourly/YYYY-MM-DD-HH.md`
- Weekly patterns in `data/_patterns/YYYY-MM-DD/` for context

## Output

Create: `data/_patterns/hourly/YYYY-MM-DD-HH.md` (UTC hour)

```markdown
---
date: YYYY-MM-DD
hour: HH
updated_at: ISO-8601 UTC
generator: patterns-hourly agent
---

# Hourly patterns — YYYY-MM-DD HH:00 UTC

## Sentiment momentum (24h)
| Ticker | Δ score | Direction |
|--------|---------|-----------|

## Sector clusters
- Tech: ...
- Healthcare: ...

## Divergence flags
- TICKER: report A vs B disagree on ...

## Volume of research
- N new reports this hour · M verifications
```

## Rules

- **Append-only series** — never delete prior hourly files (ADR #12)
- No trading recommendations — pattern description only
- Deduplicate themes already stated identically in previous hour unless materially changed

## Branch

Maintainer branch: `hourly/patterns/YYYY-MM-DD-HH-<hash8>` or direct commit to `main` if automated bot account (future).

Follow `agents/prose-style.md`.
