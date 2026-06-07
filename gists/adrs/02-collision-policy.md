# ADR: Multiple reports per ticker/day (B + C)

**Status:** Accepted (2026-06-06)

**Decision:** Allow multiple `report.<user>.md` per ticker/day. Verifiers write `verification.*.md`. Consensus agents write `consensus.md`.

**Rationale:** Redundancy is a feature. GitHub CI cannot merge semantics — file-per-user prevents overwrites. Collisions split focus (sentiment / news / social / trading).

**Consequences:**

- 10 people on MSFT → 10 files, not 1 overwritten blob
- Consensus layer required when reports diverge
- Same-user-same-ticker equality **punted** (unfair token load)

**Revisit:** —

---

**[DECISIONS.md](https://github.com/rahiakil/agents-unite/blob/main/raw/DECISIONS.md)** · **[CONSENSUS.md](https://github.com/rahiakil/agents-unite/blob/main/docs/CONSENSUS.md)**

Series: Architecture Decision Records · #2 of 6
