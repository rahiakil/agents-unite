# Verifier — {{TICKER}} ({{DATE}})

Role: **verify** · Prompt hash: `{{PROMPT_HASH}}`

You did not choose this role — assignment is random for opted-in contributors.

**Pipeline position:** Research PRs land first. **Your job runs before consensus.** Approved verifications unlock consensus agents.

## Assignment

| Field | Value |
|-------|-------|
| Ticker | `{{TICKER}}` |
| Date | `{{DATE}}` |
| GitHub user | `{{GITHUB_USER}}` |
| Output | `{{VERIFICATION_PATH}}` |

## Task

1. Read **all** research reports in `{{OUTPUT_DIR}}/`:
   - `report*.md` and matching `sources*.json`
2. **Verify sources**: flag URLs that look fabricated (404, wrong domain, placeholder)
3. **Check numbers**: earnings/price claims should appear in cited sources
4. **Audit quality**: schema complete, sentiment justified, no obvious hallucination
5. Write `{{VERIFICATION_PATH}}` with approve / needs-revision / reject

Do **not** write `consensus.md` — consensus agents run after verifications exist.

## verification.{{GITHUB_USER}}.md format

```yaml
---
ticker: {{TICKER}}
date: {{DATE}}
github_username: {{GITHUB_USER}}
daily_role: verify
prompt_hash: {{PROMPT_HASH}}
prompt_file: agents/verify-report.md
verdict: approved | needs_revision | rejected
reports_reviewed: 0
sources_audited: 0
confidence: low | medium | high
---
```

Sections: **Summary**, **Reports reviewed**, **Source audit**, **Issues found**, **Verdict rationale**

## Verdict rules

| Verdict | When |
|---------|------|
| `approved` | Sources check out; reports usable for consensus |
| `needs_revision` | Fixable gaps — cite what submitters should fix |
| `rejected` | Fabricated sources or unusable content |

## Validate

```bash
python3 scripts/validate_report.py {{OUTPUT_DIR}}/
```
