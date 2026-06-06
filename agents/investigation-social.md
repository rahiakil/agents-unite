# Social Focus — {{TICKER}} ({{DATE}})

Role: **submitter** · Focus: **social** · Prompt hash: `{{PROMPT_HASH}}`

## Assignment

| Field | Value |
|-------|-------|
| Ticker | `{{TICKER}}` |
| Date | `{{DATE}}` |
| GitHub user | `{{GITHUB_USER}}` |
| Output | `{{REPORT_PATH}}`, `{{SOURCES_PATH}}` |

## Task

Research **Twitter/X and Reddit** for {{TICKER}} (last 24–72h):

1. r/wallstreetbets, r/stocks, X keyword clusters ($TICKER)
2. Volume estimates, tone breakdown, notable threads
3. Sentiment score from **social tone**
4. Sources must include twitter + reddit types when available

Skip long-form news — other contributors cover that.

## Frontmatter (required)

```yaml
---
ticker: {{TICKER}}
date: {{DATE}}
github_username: {{GITHUB_USER}}
contributor_hash: {{CONTRIBUTOR_HASH}}
daily_role: submitter
focus: social
prompt_hash: {{PROMPT_HASH}}
prompt_file: agents/investigation-social.md
sentiment_score: 0.0
detail_level: {{DETAIL_LEVEL}}
---
```

## Validate

```bash
python3 scripts/validate_report.py {{OUTPUT_DIR}}/
```
