# Onboarding — zero to first PR in 15 minutes

FinanceDatabase wins contributors with **CSV edits**. agents-unite must match that simplicity.

## Current friction

| Step | Pain | Fix |
|------|------|-----|
| Clone + venv | Moderate | `./scripts/setup.sh` one shot ✅ |
| API key | High | Document Ollama path prominently |
| `gh auth` | Medium | Manual PR URL fallback in docs |
| Understand roles | High | Single-page "first run" in website join flow |
| Validation fail | High | Better error messages + fix hints |

## Target flow

```bash
git clone https://github.com/rahiakil/agents-unite.git
cd agents-unite && ./scripts/setup.sh
# Ollama OR export OPENAI_API_KEY=...
./scripts/run-agent.sh --run
./scripts/commit-report.sh
gh pr create   # or browser URL
```

## Ideas to implement

1. **`good first issue`** — "Add report for ticker X from universe zero-coverage list"
2. **Demo mode** — `--dry-run` shows assignment without LLM cost
3. **Pre-filled PR body** from `pr-open` agent
4. **Video/GIF** on website join page (30s screen recording)
5. **Discord bot** (future) — posts daily "uncovered tickers" list

## Compare: FinanceDatabase

> "Anyone, even without coding, can contribute via CSV."

agents-unite equivalent:

> "Anyone with an agent and 10 minutes can contribute via one PR."

---

Series: Market Research Methods · #9 of 12
