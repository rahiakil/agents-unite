# ADR: Multi-agent orchestration — six wake roles

**Status:** Accepted (2026-06-07)

**Context:** A single “run agent” cron is insufficient. When agents wake, the pool splits into specialized jobs across the contributor fleet.

**Decision:** Each wake cycle may assign one of these **agent roles** (prompt = immutable `.md` in `agents/`):

| # | Role | Agent prompt | Output / action |
|---|------|--------------|-----------------|
| 1 | **research** | `investigation*.md` | `report.<user>.md` + `sources.<user>.json` |
| 2 | **verify** | `verify-report.md` | `verification.<user>.md` (approved / needs_revision / rejected) |
| 3 | **consensus** | `consensus-run.md` | `consensus.md` |
| 4 | **pr_open** | `pr-open.md` | Push branch, open/update GitHub PR, fill template |
| 5 | **security_review** | `security-review.md` | Comment on PR: scope, secrets, path violations, markdown safety |
| 6 | **summary / patterns** | `summary-update.md`, `patterns-hourly.md` | Update live summaries + hourly trading patterns (post-merge) |

**Rationale:**

- Research without verify is noise. Verify without consensus leaves disagreement unresolved.
- PR creation and security review are **separate agents** so researchers never self-approve scope.
- Summaries and patterns are **downstream markdown** — cheap to merge once data is canonical.

**Consequences:**

- `assign_role.py` gains lottery weights for `pr_open` and `security_review` (maintainer nodes only for security on code PRs).
- Contributor nodes: research | verify | consensus | pr_open (data branches only).
- All outputs are markdown/JSON under `data/` or PR comments — no binary blobs.
- Failed agent run → retry once → issue filed (`failed-runs` label).

**Revisit:** Dedicated security bot GitHub App vs contributor-run security agent.

---

**[ROLES.md](https://github.com/rahiakil/agents-unite/blob/main/docs/ROLES.md)** · **[AGENT_SCHEDULING.md](https://github.com/rahiakil/agents-unite/blob/main/docs/AGENT_SCHEDULING.md)**

Series: Architecture Decision Records · #8 of 12
