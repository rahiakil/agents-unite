# ADR: Contributors may only push data/

**Status:** Accepted (2026-06-06)

**Decision:** Immutable core — contributors may **only edit `data/`** in PRs. Path-guard CI blocks scripts, agents, prompts, and workflow changes.

**Rationale:** 20,000 cron nodes cannot silently rewrite assignment logic or validation rules. Maintainers use CODEOWNERS for core changes.

**Layers:**

| Guard | Blocks |
|-------|--------|
| `contributor-guard.yml` | Non-data edits from report branches |
| `ci-integrity.yml` | Cloud anchor on guard scripts |
| `prompt_hash` | Proves canonical prompt use |

**Revisit:** —

---

**[DECISIONS.md](https://github.com/rahiakil/agents-unite/blob/main/raw/DECISIONS.md)** · **[TRUST.md](https://github.com/rahiakil/agents-unite/blob/main/docs/TRUST.md)**

Series: Architecture Decision Records · #3 of 6
