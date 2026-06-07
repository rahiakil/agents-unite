# ADR: Research → verify → consensus

**Status:** Accepted (2026-06-06)

**Decision:** Ordered role pipeline — research → verify → consensus; weekly patterns + findings every ~7 days.

**Rationale:** Trust builds in stages. Raw research is noisy. Verifiers audit URLs and claims. Consensus reconciles multiple views. Weekly agents scan cross-ticker themes.

**Consequences:**

- `daily_role` in frontmatter records which hat you wore
- Verifiers cannot overwrite researcher files
- Consensus writes `consensus.md`; raw reports stay forever

**Revisit:** —

---

**[DECISIONS.md](https://github.com/rahiakil/agents-unite/blob/main/raw/DECISIONS.md)** · **[ROLES.md](https://github.com/rahiakil/agents-unite/blob/main/docs/ROLES.md)**

Series: Architecture Decision Records · #1 of 6
