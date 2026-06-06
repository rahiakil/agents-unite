# Verifier — {{TICKER}} ({{DATE}})

Role: **verifier** · Prompt hash: `{{PROMPT_HASH}}`

You did not choose this role — assignment is random for opted-in contributors.

## Assignment

| Field | Value |
|-------|-------|
| Ticker | `{{TICKER}}` |
| Date | `{{DATE}}` |
| GitHub user | `{{GITHUB_USER}}` |
| Output | `{{CONSENSUS_PATH}}` |

## Task

1. Read **all** submitter reports in `{{OUTPUT_DIR}}/`:
   - `report*.md` and matching `sources*.json`
2. **Verify sources**: flag URLs that look fabricated (404, wrong domain, no real page)
3. **Check numbers**: earnings/price claims should appear in cited sources
4. **Reconcile sentiment**: weighted view; preserve disagreement — do not flatten
5. Write `consensus.md` (canonical layer for this ticker/day)

## consensus.md format

```yaml
---
ticker: {{TICKER}}
date: {{DATE}}
github_username: {{GITHUB_USER}}
daily_role: verifier
prompt_hash: {{PROMPT_HASH}}
prompt_file: agents/verify-report.md
consensus_score: 0.0
confidence: low | medium | high
reports_reviewed: 3
outliers_rejected: 0
---
```

Sections: **Summary**, **Consensus Score**, **Agreement**, **Disagreements**, **Source audit**, **Rejected claims**

## Outlier policy (document only for now)

- Scores >2 MAD from median → note as outlier, do not delete raw reports
- Coordinated pump patterns → flag in Disagreements (future: automated rejection)

## Validate

```bash
python3 scripts/validate_report.py {{OUTPUT_DIR}}/
```
