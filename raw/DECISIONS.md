# Decisions Log

Locked product decisions from founder review (2026-06-06).

| Date | Decision | Rationale | Revisit? |
|------|----------|-----------|----------|
| 2026-06-06 | **Role pipeline:** research → verify → consensus; weekly patterns + findings every ~7 days | Ordered trust; breaking news + cross-ticker scans | — |
| 2026-06-06 | **Collisions: B + C** — allow multiple `report.<user>.md`; verifiers write `verification.*.md`; consensus agents write `consensus.md` | Redundancy is a feature; GitHub CI cannot merge semantics | — |
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
| 2026-06-07 | **Dual merge paths:** Rahil/maintainers merge platform code; contributor data through full pipeline | Code velocity vs data trust | — |
| 2026-06-07 | **Six agent roles:** research, verify, consensus, pr_open, security_review, summary/patterns hourly | Specialized wakes; markdown-only outputs | Wire in `assign_role.py` |
| 2026-06-07 | **Global stagger:** verifiers scan backlog; no single verifier hour | 24/7 contributor timezones | — |
| 2026-06-07 | **Hourly:** `_index` summaries + `_patterns/hourly/` trading patterns | Post-merge freshness for builders | Maintainer cron nodes |
| 2026-06-07 | **Corrections via GitHub:** data-correction + record-amendment issues; no silent edits | Auditable financial memory | Amendment schema in validator |
| 2026-06-07 | **Research gists #7–12** | Growth, distribution, onboarding, ecosystem, reputation, OSS benchmarks | Publish via publish-gists.sh |

## Deferred (documented, not implemented)

| Topic | Plan |
|-------|------|
| Proof-of-stake / min reputation to verify | Phase 4 |
| Per-IP caps, proof-of-human anti-Sybil | Future |
| Coordinated pump → outlier rejection automation | Verifier + MAD; full automation later |
| Same contributor always same ticker | **Rejected for now** — unfair token load |
| Wiki auto-ingest on every push | Manual / batch after data quality known |
| `pr_open` / `security_review` in assign_role lottery | Wired in `assign_role.py` for maintainers |
| Hourly pattern cron workflow | `scripts/run-hourly-ops.sh` + maintainer cron |
| Amendment file validation in CI | Schema for `amendment.*.md` |
