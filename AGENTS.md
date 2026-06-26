# Agent Instructions — Agents Unite

This file guides AI agents (Cursor, Codex, Claude, etc.) working in this repository.

## Your job

When a user runs `./scripts/run-agent.sh`, they receive **one ticker assignment for today**. Your task:

1. Research **recent sentiment** (last 24–72 hours) for that ticker
2. Write `data/YYYY-MM-DD/TICKER/report.md` and `sources.json`
3. Stop when the schema is complete — do not over-research

## Token budget

- **Target:** fill the schema in 2–5 minutes of agent time
- **Sources:** 3–7 real URLs across Twitter/X, Reddit, and news
- **Report:** structured sections, not a research memo
- **Stop condition:** sentiment score is justified with cited sources

## Required output

### report.md sections (exact H1 headings)

1. `# Sentiment` — score (-1.0 to +1.0) + 2–4 sentence rationale
2. `# Key Themes` — 3–5 bullets
3. `# Sources` — brief summary (URLs go in sources.json)
4. `# Price Snapshot` — table with price, change %, volume
5. `# Notable Events` — earnings, catalysts, or "None identified"

YAML frontmatter required:

```yaml
---
ticker: SYMBOL
date: YYYY-MM-DD
contributor_hash: <from assignment>
sentiment_score: 0.0
---
```

### sources.json

- `type`: `twitter` | `reddit` | `news` | `other`
- Real URLs only — no placeholders in final output
- At least 3 sources across 2+ types when possible

## Workflow

```bash
./scripts/run-agent.sh                                    # get assignment
python3 scripts/validate_report.py data/DATE/TICKER/      # validate
python3 scripts/generate_readme.py                        # refresh live README
./scripts/commit-report.sh                                # commit if valid
```

## Prose quality (no AI slop)

Reports are **data**, not marketing copy. Follow [`agents/prose-style.md`](agents/prose-style.md) — derived from [stop-slop](https://github.com/hardikpandya/stop-slop).

- Direct, specific, short sentences in `# Sentiment`
- No filler phrases, jargon, or generic bullish/bearish fluff
- Every investigation prompt includes these rules automatically

Cursor users: project skill at [`.cursor/skills/stop-slop/`](.cursor/skills/stop-slop/SKILL.md) also applies when editing docs, README, and wiki.

## What NOT to do

- Do not pick your own ticker — use the assignment from `run-agent.sh`
- Do not give trading advice — sentiment reporting only
- Do not overwrite existing reports for the same date/ticker
- Do not remove README live markers (`<!-- LIVE:*:START/END -->`)
- Do not invent URLs — cite real posts and articles
- Do not use AI filler prose — see [`agents/prose-style.md`](agents/prose-style.md)

## Prompt template

The full agent prompt lives at [`agents/investigation.md`](agents/investigation.md). `run_investigation.py` fills in ticker, date, and output paths.

## Future modes

- **Consensus** ([`agents/consensus.md`](agents/consensus.md)): reconcile multiple reports for the same ticker
- **Hourly**: reports under `data/DATE/TICKER/HH/` (Phase 2)
- **Trading plays**: gated by contributor reputation (Phase 4)
- **Wiki ingest** ([`WIKI.md`](WIKI.md)): compile `data/` into `wiki/` second brain

## Cursor Cloud specific instructions

This repo is **Python stdlib-first**. The whole core pipeline (assign → scaffold → validate → stats → README → website) runs on the system `python3` with **no pip installs**. There are **no daemons/DB/web servers** — "running the app" means running CLI scripts in `scripts/` and inspecting Git output. Commands are documented in `README.md`, `Makefile`, and `CLAUDE.md`; prefer those.

- **No unit tests or linter configs exist.** The validation gate is `python3 scripts/validate_report.py [dir]` (also `make check`), and it's exactly what CI runs (`.github/workflows/validate-report.yml`). Treat that as the test/lint command.
- **Some scripts mutate tracked files.** `scripts/generate_readme.py` rewrites the `<!-- LIVE:* -->` blocks in `README.md`, and `scripts/aggregate.py` writes `data/_index/summary-<date>.md`. Running them dirties the working tree — `git checkout README.md` / remove the index file if you only meant to verify they run.
- **The `.venv` is optional and only for the LLM harness** (`./scripts/run-agent.sh --run`, `scripts/run_agent.py`). It is created by `./scripts/ensure-venv.sh llm` and needs the system `python3-venv` package (already provisioned in this environment). The harness also needs an API key (`OPENAI_API_KEY`, or `llm_provider: ollama`, etc.) — not set here, so `--run` will report "No agent configured." The manual workflow (scaffold via `run-agent.sh`, hand-fill `report.*.md` + `sources.*.json`, then validate) needs no key.
- **Config is gitignored.** `run-agent.sh` / `install-cron.sh` seed `.agents-unite/config.yaml` from `config/config.example.yaml`; `scripts/au-env.sh` auto-prefers `.venv` when present, else falls back to system `python3`.
