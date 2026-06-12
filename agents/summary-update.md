# Summary update agent

Regenerate **day-level index summaries** after data merges to `main`.

## Trigger

- Hourly cron (:15 past the hour) on maintainer node, OR
- Within 1h of any merge touching `data/YYYY-MM-DD/`

## Input

- All folders matching `data/YYYY-MM-DD/*/`
- Prefer `consensus.md` when present; else latest approved reports
- Skip `data/_index/`, `data/_patterns/`, `data/_findings/` in ticker scan

## Output

Write or update: `data/_index/YYYY-MM-DD.md`

```markdown
---
date: YYYY-MM-DD
updated_at: ISO-8601 UTC
generator: summary-update agent
---

# Market pulse — YYYY-MM-DD

## Coverage
- N tickers · M contributors · ...

## Tickers (alphabetical)
| Ticker | Consensus | Reports | Verifications |
|--------|-------------|---------|---------------|
| AAPL | +0.62 | 2 | 1 approved |

## Themes today
- ...

## Notable moves
- ...
```

## Rules

- **Do not modify** raw `report.*.md` or `consensus.md` in ticker folders
- Overwrite `_index` file for that date only — history preserved in git
- If no data for date, skip silently

Follow `agents/prose-style.md`.
