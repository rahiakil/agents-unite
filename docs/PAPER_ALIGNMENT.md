# Paper vs public repository

This compares the Agents Unite paper (Parag Paul, RIG AI; references this repo) with the current **Phase 1** implementation on `main`.

## Summary

The public repo **implements the core loop** the paper describes: deterministic daily assignment, immutable prompts, contributor PRs to `data/YYYY-MM-DD/TICKER/`, CI validation, and documented verifier/consensus governance. Several **Phase 2–4** items in the paper are **roadmap or partial** — the paper itself marks many evaluations as future work (Appendix A).

## Implemented

| Paper element | Repo evidence |
|---------------|---------------|
| One agent, one ticker/day, PR to shared ledger | `scripts/daily-run.sh`, `scripts/assign_role.py`, `data/` |
| Deterministic assignment (hash lottery) | `scripts/assign_ticker.py`, `scripts/au_common.py` |
| Focus diversity (sentiment, news, social, trading, full) | `agents/*.md`, assignment JSON |
| Immutable prompts + `prompt_hash` in CI | `.github/workflows/validate-report.yml`, `scripts/validate_report.py` |
| Contributor Guard / protected paths | `.github/workflows/contributor-guard.yml` |
| GitHub as database, no central server | Architecture throughout |
| `examples/load_reports.py` for backtests | `examples/load_reports.py` |
| Dual merge paths (maintainer code vs contributor data) | `docs/GOVERNANCE.md`, ADR #7 |
| Verifier / consensus **roles and prompts** | `agents/verify-run.md`, `agents/consensus-run.md`, `assign_role.py` |
| Reputation file (Phase 1 schema) | `contributors/reputation.json` |

## Partial

| Paper element | Gap |
|---------------|-----|
| Verifier cascade (cheap yes/no + cross-encoder) | Prompts exist; automated cheap verifier not wired |
| Weighted median + MAD outlier rejection | `scripts/consensus.py` computes it. The study harness calls it. No CI job writes `consensus.md` into `data/` yet |
| Reputation-weighted median | `scripts/reputation.py`. Weight is stake (1) times reputation times recency. Production `contributors/reputation.json` ships empty |
| Coverage-aware role allocation from CI manifest | Ticker coverage optimizer yes; full sector/geography manifest incomplete |
| Hourly summary / pattern agents | Prompts + `run-hourly-ops.sh`; no GitHub Actions schedule yet |
| Evaluation plan (Appendix A) | Not run — paper correctly labels as future empirical work |

## Planned / not in repo

| Paper element | Status |
|---------------|--------|
| Raft-style leader election for a shard | `scripts/leader_election.py` (argmin SHA256). The study uses hour `close`. No hourly production job yet |
| Reputation-weighted consensus in trading | Study harness only. Trading gates in `docs/TRADING.md` are still future |
| Columnar snapshots (Parquet/DuckDB) | Not implemented |
| Provenance sidecar per report | Not standardized in schema yet |
| Production efficacy claims | Paper defers to future benchmark paper |

## Threat model (Section 9)

The paper lists open gaps (prompt injection, Sybil, CI-only gate). The repo **aligns with that honesty**: CI validates structure, not truth; human review and verifier diversity are load-bearing and documented in `docs/GOVERNANCE.md`.

## Study for the second paper

`sim/` is a separate longitudinal study. It runs persona agents through the same assignment and validators, then records consensus error, reputation, and detection latency. Seeded proof: `python3 -m sim --days 6 --provider rule --check`. Schema: `sim/SCHEMA.md`. Daily archive: `.github/workflows/sim-daily.yml` pushes `sim-data`. That study is the input for a learnings paper. It does not change the claims of the ledger paper.

## Recommendation

- **Paper:** Keep Phase 2–4 language as proposed/future; cite `docs/PAPER_ALIGNMENT.md` or ADR index for implementation status.
- **Repo:** Prioritize `scripts/consensus.py`, scheduled hourly ops, and Appendix A benchmarks when claiming production efficacy.
