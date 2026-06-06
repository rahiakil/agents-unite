# Vision

agents-unite is a **Git-native, crowd-powered market sentiment ledger**.

## Problem

No individual has the token budget or energy to research ~4,000 US tickers daily. Terminals and scrapers lock narrative data behind paywalls.

## Solution

Thousands of people run **one cron job** on a cloned repo. Each day:

1. Assignment picks a ticker (coverage-optimized) and a role (submitter or verifier)
2. Local agent (Cursor, Hermes, OpenClaw, …) runs the **canonical prompt from this repo**
3. Output lands in `data/YYYY-MM-DD/TICKER/` as a PR
4. Verifiers reconcile collisions into `consensus.md`
5. Traders browse history without personal research cost

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

[Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) scaffold exists (`wiki/`, `WIKI.md`). **Active ingestion waits** until live contributor data proves useful shape.

## Feedback

Use GitHub Issues → **Feedback** template for field suggestions.

See also: [raw/THINKING.md](../raw/THINKING.md), [raw/DECISIONS.md](../raw/DECISIONS.md), [CONFIG.md](CONFIG.md), [TRUST.md](TRUST.md).
