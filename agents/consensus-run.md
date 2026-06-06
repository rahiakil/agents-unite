# Consensus — {{TICKER}} ({{DATE}})

Role: **consensus** · Prompt hash: `{{PROMPT_HASH}}`

**Pipeline position:** Runs **after** verifiers have written `verification*.md` with `verdict: approved`. You merge verified research into one canonical view.

## Assignment

| Field | Value |
|-------|-------|
| Ticker | `{{TICKER}}` |
| Date | `{{DATE}}` |
| GitHub user | `{{GITHUB_USER}}` |
| Output | `{{CONSENSUS_PATH}}` |

## Task

1. Read all `report*.md` + `sources*.json` in `{{OUTPUT_DIR}}/`
2. Read all `verification*.md` — **only incorporate reports verifiers approved**
3. Compute weighted sentiment (median; drop MAD outliers if n ≥ 3)
4. Merge themes; preserve disagreement in **Divergence**
5. Write `consensus.md`

## consensus.md format

```yaml
---
ticker: {{TICKER}}
date: {{DATE}}
github_username: {{GITHUB_USER}}
daily_role: consensus
prompt_hash: {{PROMPT_HASH}}
prompt_file: agents/consensus-run.md
consensus_score: 0.0
confidence: low | medium | high
reports_reviewed: 0
verifications_reviewed: 0
method: weighted_median
---
```

Sections: **Summary**, **Consensus Score**, **Agreement**, **Divergence**, **Source coverage**, **Price snapshot**, **Notable events**

## Scoring

1. Collect `sentiment_score` from **approved** reports only
2. Drop outliers beyond 2 MAD from median (if n ≥ 3)
3. **Consensus score** = weighted median (weight 1.0 per report in v1)
4. **Confidence**: high if n ≥ 3 and spread ≤ 0.4; medium if n = 2; else low

## Validate

```bash
python3 scripts/validate_report.py {{OUTPUT_DIR}}/
```
