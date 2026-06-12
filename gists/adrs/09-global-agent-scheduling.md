# ADR: Global staggered scheduling — verifiers need not wait

**Status:** Accepted (2026-06-07)

**Context:** Verifiers should not only wake when “their” ticker is ready. A worldwide fleet means slots are available 24/7.

**Decision:**

1. **Default cron** remains user-local (`schedule` in `.agents-unite/config.yaml`) — e.g. `0 6 * * *` in contributor timezone.
2. **Role assignment is hash-staggered** — verify/consensus/pr_open roles distributed across contributors and UTC hours, not synchronized globally.
3. **Verifier pool scans backlog** — on verify wake, `find_verify_target()` prefers `data/DATE/TICKER/` with reports lacking `verification*.md`, anywhere in the repo.
4. **No “verifier-only” fixed hour** — any contributor whose cron fires may draw verify role (~20% if opted in).

**Rationale:**

- US-close vs UTC-midnight already desynchronizes date folders ([TIMING.md](https://github.com/rahiakil/agents-unite/blob/main/docs/TIMING.md)).
- Staggered wakes ≈ continuous audit without a central scheduler.
- Matches “people use it whenever” — agents-unite is not a single batch job at 4pm ET.

**Consequences:**

- Assignment cache is per `(date, contributor_hash)` — not global mutex.
- Future: optional `verify_backlog` issue when reports sit >24h unverified.
- Hourly summary/pattern agents run on **maintainer cron** or dedicated nodes (see ADR #10).

**Revisit:** Central queue (Redis/SQS) if contributor count exceeds git-scan practicality.

---

Series: Architecture Decision Records · #9 of 12
