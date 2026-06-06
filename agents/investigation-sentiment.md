# Sentiment Focus — {{TICKER}} ({{DATE}})

Role: **submitter** · Focus: **sentiment** · Prompt hash: `{{PROMPT_HASH}}`

Read only. Do not modify files outside your output path.

## Assignment

| Field | Value |
|-------|-------|
| Ticker | `{{TICKER}}` |
| Date | `{{DATE}}` |
| GitHub user | `{{GITHUB_USER}}` |
| Output | `{{REPORT_PATH}}`, `{{SOURCES_PATH}}` |

## Task

Research **sentiment only** for {{TICKER}} (last 24–72h):

1. Social tone (Reddit, X) — bullish/bearish ratio, dominant narratives
2. Assign **sentiment_score** −1.0 to +1.0 with 2–4 sentence rationale
3. **Key Themes** — 3–5 bullets
4. Minimal price snapshot (last close + change % if easy)
5. Skip deep news/trading data — other contributors cover those

## Frontmatter (required)

```yaml
---
ticker: {{TICKER}}
date: {{DATE}}
github_username: {{GITHUB_USER}}
contributor_hash: {{CONTRIBUTOR_HASH}}
daily_role: submitter
focus: sentiment
prompt_hash: {{PROMPT_HASH}}
prompt_file: agents/investigation-sentiment.md
sentiment_score: 0.0
detail_level: {{DETAIL_LEVEL}}
---
```

## Sources

At least 3 sources, ≥2 types. URLs in `sources.json` only.

## Validate

```bash
python3 scripts/validate_report.py {{OUTPUT_DIR}}/
```
