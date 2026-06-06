# Decisions Log

Locked product decisions from founder review (2026-06-06).

| Date | Decision | Rationale | Revisit? |
|------|----------|-----------|----------|
| 2026-06-06 | **Collisions: B + C** — allow multiple `report.<user>.md` + verifier writes `consensus.md` | Redundancy is a feature; GitHub CI cannot merge semantics | — |
| 2026-06-06 | **Date modes:** `utc_midnight` and `us_close` (user config) | Global contributors wake at different times | Per-user config in `.agents-unite/config.yaml` |
| 2026-06-06 | **Auto-PR** fully automated via `gh`; single-report paths merge when CI green | Low friction for 20k cron nodes | Verifier review always part of pipeline |
| 2026-06-06 | **Agent runtime:** user choice (Cursor, Hermes, OpenClaw, manual, etc.) | People already run agents on their box | — |
| 2026-06-06 | **Verifier pool:** opt-in; random daily role; user does not know until run | Fair rotation; prompt from repo code only | Stake/reputation gating later |
| 2026-06-06 | **Reputation:** tied to **GitHub username** | Auditable, ties to PR identity | — |
| 2026-06-06 | **Assignment:** hash + **coverage optimizer** (bias to zero-report tickers) | Avoid 10 people on MSFT, empty tickers ignored | Same-user-same-ticker equality **punted** (token burn fairness) |
| 2026-06-06 | **Multi-submitter focus split:** sentiment / news / social / trading | Divided labor when tickers collide | — |
| 2026-06-06 | **Cron failure:** retry once → alert verifiers (issue/file) | Resilience without silent skip | — |
| 2026-06-06 | **Immutable core:** contributors may **only push `data/`** | Path-guard CI blocks scripts/agents/prompts changes | CODEOWNERS for maintainers |
| 2026-06-06 | **Prompt trust:** `prompt_hash` + `prompt_file` in report frontmatter | Verifiable canonical prompt used | — |
| 2026-06-06 | **Token budget:** user picks `detail_level` at install (minimal/standard/deep) | Opt-in depth | — |
| 2026-06-06 | **Second brain / wiki:** deferred until real user data accumulates | Documented in WIKI.md; manual ingest OK | Start after few days of live data |
| 2026-06-06 | **Feedback:** GitHub issues welcome (`feedback` template) | Community-driven field suggestions | — |

## Deferred (documented, not implemented)

| Topic | Plan |
|-------|------|
| Proof-of-stake / min reputation to verify | Phase 4 |
| Per-IP caps, proof-of-human anti-Sybil | Future |
| Coordinated pump → outlier rejection automation | Verifier + MAD; full automation later |
| Same contributor always same ticker | **Rejected for now** — unfair token load |
| Wiki auto-ingest on every push | Manual / batch after data quality known |
