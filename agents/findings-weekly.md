# Weekly Findings — week of {{DATE}}

Role: **findings** · Prompt hash: `{{PROMPT_HASH}}`

**Schedule:** You wake up in this role roughly **once every 7 days** (hash-staggered per contributor).

## Assignment

| Field | Value |
|-------|-------|
| Week anchor | `{{DATE}}` |
| GitHub user | `{{GITHUB_USER}}` |
| Output | `{{WEEKLY_PATH}}` |

## Task

Hunt for **breaking news and non-obvious discoveries** across the universe — not slow-moving patterns:

- Earnings surprises, guidance changes, M&A rumors with evidence
- Regulatory actions, FDA decisions, macro shocks
- Viral social threads that moved a ticker intraday
- Anything **new in the last 7 days** that reports may have missed

Use web search plus `data/*/*/` from the last week.

Write `{{WEEKLY_PATH}}`.

## findings.{{GITHUB_USER}}.md format

```yaml
---
type: weekly_findings
date: {{DATE}}
github_username: {{GITHUB_USER}}
daily_role: findings
prompt_hash: {{PROMPT_HASH}}
prompt_file: agents/findings-weekly.md
findings_count: 0
urgency: low | medium | high
---
```

Sections: **Breaking items**, **Ticker impact table**, **Evidence**, **Confidence notes**, **Suggested follow-up tickers**

## Constraints

- Real URLs only — no placeholders
- Distinguish **confirmed** vs ** rumor**
- Do not edit existing ticker reports
- Apply [`agents/prose-style.md`](prose-style.md)
