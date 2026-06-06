# Vision

agents-unite is a **Git-native, crowd-powered market sentiment ledger** — **one repo where thousands of agents contribute agentic LLM research so no one has to cover the market alone.**

## Problem

No one can LLM-research ~4,000 US tickers daily on their own. The tickers eat the token budget first. Even with unlimited spend, **timing breaks solo runs**: sessions in one timezone miss overnight social spikes, foreign open, and after-hours filings. Terminals and scrapers add paywalls on top.

## Solution

Thousands of installs run **one cron job** on the same repo. Each day, globally:

1. Assignment picks a ticker (coverage-optimized) and a role (submitter or verifier)
2. A local harness (built-in LLM, Cursor, Hermes, OpenClaw, …) runs the **canonical prompt from this repo**
3. The agent files network findings for that ticker (social, news, trading focus) into `data/YYYY-MM-DD/TICKER/` as a PR
4. Verifiers reconcile collisions into `consensus.md`
5. **Everyone reads the distributed ledger** — sentiment today, historical archive tomorrow, without re-spending tokens on names others already covered

## What accumulates

| Horizon | What you get |
|---------|----------------|
| **Day 1** | One structured report + sources for your ticker |
| **Weeks** | Cross-ticker sentiment pulse, live README, coverage map |
| **Months+** | Longitudinal Git history: train models, mine patterns, backtest, embed for RAG — **how you use `data/` is your choice** |

The maintenance cost is **crowdsourced**. The upside is **shared**.

## Roles

| Role | Knows in advance? | Output |
|------|-------------------|--------|
| **Submitter** | No (if verifier opt-in) | `report.<github_user>.md` + `sources.<user>.json` |
| **Verifier** | No | `consensus.md` |

Submitter **focus** (random): `sentiment` | `news` | `social` | `trading` | `full`

When 10 people land on MSFT, they produce **complementary slices** — not 10 duplicate memos.

## Trust model

- **Immutable core:** contributors cannot modify `scripts/`, `agents/`, prompts (path-guard CI)
- **Prompt provenance:** reports include `prompt_hash` matching repo template
- **Reputation:** GitHub username on every artifact
- **Verification:** always required in pipeline; auto-merge only after CI + consensus path

## Date folders

User config (`.agents-unite/config.yaml`):

- `utc_midnight` — global UTC calendar date
- `us_close` — US session date (America/New_York)

## Scale target

20,000 installs × ~15% daily active ≈ **3,000 reports/day** ≈ 75% universe coverage.

Coverage optimizer weights tickers with **zero reports today** 10× over overcrowded names.

## Phases

| Phase | Deliverable |
|-------|-------------|
| **1 (now)** | Cron, assignment, multi-report, verifier prompts, path guard |
| **2** | Hourly shards, URL verification |
| **3** | Automated consensus batch, reputation |
| **4** | Stake-gated strategies, proof-of-human |

## Second brain

[Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) scaffold exists (`wiki/`, `WIKI.md`). **Active ingestion waits** until live contributor data proves useful shape. Pipeline: [RAG_AND_SYNTHESIS.md](RAG_AND_SYNTHESIS.md).

## Doc index

Full technical map: [docs/README.md](README.md) — timing, data quality, consensus, RAG, scientific methods.

## Feedback

Use GitHub Issues → **Feedback** template for field suggestions.

See also: [raw/THINKING.md](../raw/THINKING.md), [raw/DECISIONS.md](../raw/DECISIONS.md), [CONFIG.md](CONFIG.md), [TRUST.md](TRUST.md).
