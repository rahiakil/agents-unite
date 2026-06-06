# Data Quality & Uniqueness

How agents-unite keeps the ledger **trustworthy**, **scoped**, and **hard to game locally**.

## Design principle

> Cloud CI is the trust anchor. Local hooks are optional; GitHub Actions is not.

A contributor cannot merge changes to validators, prompts, or workflows. They can only add raw reports under one date/ticker folder per branch.

## Contributor scope (CI)

On every push to `report/**` and every PR to `main`, **Contributor Guard** runs:

| Check | What it enforces |
|-------|------------------|
| Branch format | `report/DATE-TICKER-HASH8` |
| Path scope | Only `data/DATE/TICKER/*` |
| File types | `report*.md`, `sources*.json`, `consensus.md` only |
| Report required | Empty commits fail |
| Identity bind | Branch hash = `SHA256(github_username)[:8]` in frontmatter |
| Content schema | `validate_report.py` — sections, sentiment, sources |

Script: `scripts/validate_contributor_scope.py`  
Workflow: `.github/workflows/contributor-guard.yml`

## Report validation

`scripts/validate_report.py` checks:

- YAML frontmatter: `ticker`, `date`, `sentiment_score` (−1…+1)
- Required sections: Sentiment, Key Themes, Sources, Price Snapshot, Notable Events
- Companion `sources.json` or `sources.<user>.json` with typed URLs (`twitter`, `reddit`, `news`, `other`)
- **Prompt provenance:** `prompt_hash` + `prompt_file` must match immutable templates in `agents/`

Legacy demo reports without prompt fields are grandfathered; **new** reports must include provenance.

## Uniqueness rules

| Dimension | Rule |
|-----------|------|
| One branch per submission | `report/DATE-TICKER-USERHASH` |
| One report file per user per ticker per day | `report.<github_slug>.md` |
| Collisions allowed | Multiple users → same ticker/day → different filenames |
| Verifier output | Single `consensus.md` per folder when reconciled |

## Protected paths (immutable core)

Contributors **cannot** modify via PR:

- `scripts/`, `agents/`, `.github/workflows/`
- `docs/`, `raw/`, `wiki/`, `tickers/`, `config/`

Enforced by Contributor Guard + [CODEOWNERS](../.github/CODEOWNERS) for maintainers.

**CI Integrity** (`.github/workflows/ci-integrity.yml`) verifies guard scripts remain wired on `main` — tampering with workflow YAML is caught in the cloud.

## Anti-manipulation (current + roadmap)

| Threat | Mitigation today | Planned |
|--------|------------------|---------|
| Fake URLs | Verifier audit | CI HEAD check on URLs |
| Prompt tampering | `prompt_hash` + path guard | — |
| Sybil accounts | — | Rate limits, proof-of-human |
| Coordinated pump | — | MAD outlier drop in consensus |
| Local validator bypass | Cloud CI on push/PR | Branch protection required checks |

## Data layout

```
data/2026-06-06/NVDA/
├── report.alice.md
├── sources.alice.json
├── report.bob.md
├── sources.bob.json
└── consensus.md          # verifier / batch job
```

Raw files are **immutable after merge** — wiki and analytics read; they do not rewrite history.

See [TRUST.md](TRUST.md), [CONSENSUS.md](CONSENSUS.md).
