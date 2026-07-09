# Timing & Assignment

How agents-unite decides **when** a report belongs and **which ticker** each contributor gets.

## Daily mission window

Each contributor runs **once per day** (typical cron: `0 6 * * *` UTC). One run → one ticker → one PR.

The goal is small, completable work:

> Today's mission: **TSLA**. Spend a few cents of tokens. Summarize what the market is saying. Submit a PR.

## Date folders (`data/YYYY-MM-DD/`)

The folder date is **not** always "today on your wall clock." It is configurable per user in `.agents-unite/config.yaml`:

| Mode | Rule | Best for |
|------|------|----------|
| `utc_midnight` | UTC calendar date | Global contributors |
| `us_close` | US equity session date (America/New_York) | US traders waking up to "today's market" |

Implementation: `scripts/au_common.py` → `resolve_investigation_date()`.

Same contributor + same date mode + same calendar day → **same assignment** globally (deterministic hash).

## Ticker assignment

1. Load active tickers from `tickers/universe.json` (sorted).
2. `contributor_hash = SHA256(normalized GitHub username or email)`.
3. `index = SHA256("{date}:{contributor_hash}") % N`.
4. **Coverage optimizer:** tickers with zero substantive reports today get **10× weight** so the collective fills gaps instead of pile-on.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full algorithm.

## Role assignment (submitter vs verifier)

If `verifier_opt_in: true`, ~25% of days you are randomly a **verifier** — you do not know until cron runs. Verifiers audit existing reports and write `consensus.md`.

Submitters get a random **focus**: sentiment, news, social, trading, or full — so ten people on the same ticker produce **complementary slices**, not ten duplicate memos.

## Branch naming encodes timing + identity

Report PRs use:

```
report/YYYY-MM-DD-TICKER-<userhash8>
```

Example: `report/2026-06-06-GE-5cd8be5d`

CI parses the branch and **rejects** any file outside `data/YYYY-MM-DD/TICKER/`. See [DATA_QUALITY.md](DATA_QUALITY.md).

## Assignment stability

Empty scaffolds do not count toward coverage (avoid re-assignment mid-run). Once assigned, `.agents-unite/assignment-{date}-{hash}.json` locks ticker for the day.

## Future: hourly shards

Phase 2 adds intraday paths: `data/DATE/TICKER/HH/`. Consensus and Raft leader election per hour — see [CONSENSUS.md](CONSENSUS.md).

## Cron resilience

`scripts/daily-run.sh`: retry once on failure, then log and optionally open a GitHub issue.

| Setting | Default | Purpose |
|---------|---------|---------|
| `retry_on_failure` | `true` | One retry after 30s |
| `notify_on_failure` | `true` | Open `daily-run failed: DATE` issue via `gh` |

### Local cron vs GitHub Actions

**Daily agent runs are local cron**, not GitHub Actions. CI only validates PRs after you push.

```
crontab → daily-run.sh → assign → agent → validate → commit → gh pr create
```

Install: `./scripts/install-cron.sh` or add:

```cron
0 6 * * * cd /path/to/agents-unite && ./scripts/daily-run.sh >> .agents-unite/cron.log 2>&1
```

Logs: `.agents-unite/cron.log`, `.agents-unite/daily-run.log`, `.agents-unite/failed-runs.log`

### Common cron failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| `cursor CLI not found` | PATH in cron | `scripts/au-env.sh` adds `~/.local/bin`; or set PATH in crontab |
| `Authentication required… CURSOR_API_KEY` | Cursor CLI in headless cron | Use `agent_adapter: llm` + Ollama, or put `CURSOR_API_KEY` in `.agents-unite/cron.env` |
| `No agent_command set` | `agent_adapter: manual` | Set `agent_adapter: llm` or `auto` with API key |
| Issues #N "daily-run failed" | Agent step failed 2× | Fix auth; set `notify_on_failure: false` to stop issue spam |
| Validation failed | Empty sources / scaffold | Agent did not complete; check LLM timeout |

Secrets for cron: copy `config/cron.env.example` → `.agents-unite/cron.env`

See [CONFIG.md](CONFIG.md) for install and `GH_TOKEN`.
