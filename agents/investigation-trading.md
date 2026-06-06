# Trading Data Focus — {{TICKER}} ({{DATE}})

Role: **submitter** · Focus: **trading** · Prompt hash: `{{PROMPT_HASH}}`

## Assignment

| Field | Value |
|-------|-------|
| Ticker | `{{TICKER}}` |
| Date | `{{DATE}}` |
| GitHub user | `{{GITHUB_USER}}` |
| Output | `{{REPORT_PATH}}`, `{{SOURCES_PATH}}` |

## Task

Research **market data and trading context** for {{TICKER}}:

1. **Price Snapshot** — detailed table: OHLC, volume vs avg, 52w range, market cap
2. Options flow / unusual activity if publicly discussed
3. Technical context (MA levels, RSI) if sources cite them
4. Sentiment score reflecting **market positioning tone** in sources

Not trading advice — report what sources say about positioning.

## Frontmatter (required)

```yaml
---
ticker: {{TICKER}}
date: {{DATE}}
github_username: {{GITHUB_USER}}
contributor_hash: {{CONTRIBUTOR_HASH}}
daily_role: submitter
focus: trading
prompt_hash: {{PROMPT_HASH}}
prompt_file: agents/investigation-trading.md
sentiment_score: 0.0
detail_level: {{DETAIL_LEVEL}}
---
```

## Validate

```bash
python3 scripts/validate_report.py {{OUTPUT_DIR}}/
```
