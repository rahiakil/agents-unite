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

`scripts/daily-run.sh`: retry once on failure, then open a verifier alert issue. Config: `retry_on_failure: true`.

See [CONFIG.md](CONFIG.md) for install and `GH_TOKEN`.
