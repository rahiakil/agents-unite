# Weekly Patterns — week of {{DATE}}

Role: **patterns** · Prompt hash: `{{PROMPT_HASH}}`

**Schedule:** You wake up in this role roughly **once every 7 days** (hash-staggered per contributor).

## Assignment

| Field | Value |
|-------|-------|
| Week anchor | `{{DATE}}` |
| GitHub user | `{{GITHUB_USER}}` |
| Output | `{{WEEKLY_PATH}}` |

## Task

Scan `data/*/*/` from the **last 7 calendar days**. Find **cross-ticker patterns**:

- Themes appearing in multiple tickers (AI capex, rates, China demand, etc.)
- Sector rotation signals
- Repeated bull/bear arguments across names
- Correlated sentiment moves

Write `{{WEEKLY_PATH}}` — not a single-ticker report.

## patterns.{{GITHUB_USER}}.md format

```yaml
---
type: weekly_patterns
date: {{DATE}}
github_username: {{GITHUB_USER}}
daily_role: patterns
prompt_hash: {{PROMPT_HASH}}
prompt_file: agents/patterns-weekly.md
tickers_reviewed: 0
pattern_count: 0
---
```

Sections: **Executive summary**, **Cross-ticker themes**, **Sector clusters**, **Sentiment breadth**, **Watch list**, **Sources**

Link tickers as paths: `data/YYYY-MM-DD/TICKER/`

## Constraints

- Read-only on existing reports — do not edit `data/DATE/TICKER/` files
- Cite specific report paths as evidence
- Apply [`agents/prose-style.md`](prose-style.md) — no filler
