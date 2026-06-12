# ADR: Hourly summaries and trading patterns after merge

**Status:** Accepted (2026-06-07)

**Context:** Once data PRs merge, downstream artifacts must refresh without waiting for the next daily research wake.

**Decision:**

| Artifact | Path | Cadence | Agent |
|----------|------|---------|-------|
| **Live README pulse** | README live sections | On every push to `main` touching `data/` | CI (`update-readme.yml`) + optional agent polish |
| **Ticker/day summary shard** | `data/_index/YYYY-MM-DD.md` | Within 1h of merge | `summary-update.md` |
| **Trading patterns** | `data/_patterns/hourly/YYYY-MM-DD-HH.md` | **Every hour** | `patterns-hourly.md` |
| **Weekly cross-ticker** | `data/_patterns/YYYY-MM-DD/` | ~1× per 7 days (staggered) | `patterns-weekly.md` (existing) |

**Rationale:**

- Intraday sentiment shifts matter for agentic trading builders ([BUILDERS.md](https://github.com/rahiakil/agents-unite/blob/main/docs/BUILDERS.md)).
- Summaries are derived views — safe to overwrite; **raw reports are never edited** (append-only ledger).
- Hourly pattern files are markdown — easy diff, easy revert.

**Consequences:**

- Merge to `main` triggers summary agent within same hour (cron `0 * * * *` on pattern nodes).
- Pattern history **accumulates** — hourly files are not deleted in weekly cleanup (see ADR #12).
- README auto-update may fail independently; hourly agent backfills `_index/`.

**Revisit:** Phase 2 official “hourly shards” in [VISION.md](https://github.com/rahiakil/agents-unite/blob/main/docs/VISION.md).

---

Series: Architecture Decision Records · #10 of 12
