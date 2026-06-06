# News Focus — {{TICKER}} ({{DATE}})

Role: **submitter** · Focus: **news** · Prompt hash: `{{PROMPT_HASH}}`

## Assignment

| Field | Value |
|-------|-------|
| Ticker | `{{TICKER}}` |
| Date | `{{DATE}}` |
| GitHub user | `{{GITHUB_USER}}` |
| Output | `{{REPORT_PATH}}`, `{{SOURCES_PATH}}` |

## Task

Research **news and fundamentals** for {{TICKER}} (last 24–72h):

1. Headlines, earnings, guidance, analyst notes, SEC filings
2. **Notable Events** section — detailed (earnings dates, FDA, M&A)
3. Sentiment score based on **news tone** (not price prediction)
4. Price snapshot if reported in news

Skip deep social scraping — focus on journalism and filings.

## Frontmatter (required)

```yaml
---
ticker: {{TICKER}}
date: {{DATE}}
github_username: {{GITHUB_USER}}
contributor_hash: {{CONTRIBUTOR_HASH}}
daily_role: submitter
focus: news
prompt_hash: {{PROMPT_HASH}}
prompt_file: agents/investigation-news.md
sentiment_score: 0.0
detail_level: {{DETAIL_LEVEL}}
---
```

## Validate

```bash
python3 scripts/validate_report.py {{OUTPUT_DIR}}/
```
