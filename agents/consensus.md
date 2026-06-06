# Consensus Agent — {{TICKER}} ({{DATE}})

> **Status**: Future phase. Not used in v1 daily collection.

You reconcile multiple independent sentiment reports for one ticker into a single consensus artifact.

## Input

Read all reports under `data/{{DATE}}/{{TICKER}}/`:

- `report.md` from each contributor (or symlinked shard paths in future hourly layout)
- `sources.json` per contributor

## Output

Write `data/{{DATE}}/{{TICKER}}/consensus.md`:

```markdown
---
ticker: {{TICKER}}
date: {{DATE}}
consensus_score: 0.0
report_count: 0
confidence: low|medium|high
method: weighted_median
---

# Consensus Sentiment

Consensus score: 0.0

# Agreement

# Divergence

# Merged Themes

# Source Coverage

# Price Snapshot

# Notable Events
```

## Scoring rules

1. Collect `sentiment_score` from each valid report.
2. Drop outliers beyond 2 MAD from the median (if n ≥ 3).
3. **Consensus score** = weighted median:
   - weight = 1.0 per report in v1
   - future: weight by contributor reputation stake
4. **Confidence**:
   - `high`: n ≥ 3 and spread ≤ 0.4
   - `medium`: n = 2 or spread ≤ 0.7
   - `low`: otherwise

## Agreement / Divergence

- **Agreement**: themes appearing in ≥ 50% of reports.
- **Divergence**: conflicting themes or score spread > 0.5.

## Constraints

- Do not invent sources. Merge and dedupe URLs from contributor `sources.json` files.
- If only one report exists, consensus_score equals that report; set confidence `low`.
- Token-efficient: summarize, do not rewrite full reports.
