# ADR: Dual merge paths — maintainer code vs contributor data

**Status:** Accepted (2026-06-07)

**Context:** The repo mixes **platform source code** (scripts, agents, CI, docs) with **market data** (`data/DATE/TICKER/`). These have different trust models and merge requirements.

**Decision:**

| Change type | Who | Merge path |
|-------------|-----|------------|
| **Source code** | Maintainer (`rahiakil` / `@agents-unite/maintainers`) | Direct push or PR with maintainer merge; **no** research→verify→consensus pipeline |
| **Market data** | Any contributor | **Must** pass: research → verify → consensus → PR → validation CI → security review agent → merge |

**Rationale:**

- Rahil (founder) owns architecture velocity — blocking platform fixes behind sentiment PR workflow would stall the project.
- External contributors submit **beliefs about tickers**, not executable code. Data PRs stay scoped to one `data/DATE/TICKER/` folder and require distributed audit before canonical merge.

**Consequences:**

- `CODEOWNERS` protects `/scripts`, `/agents`, `/.github`, etc. — maintainer approval required.
- Contributor Guard blocks non-`data/` edits on `report/**` branches.
- Branch protection on `main`: Contributor Guard required for all PRs; maintainers may bypass for emergency code fixes (documented, not routine).
- Auto-merge **disabled** for contributor data PRs until verify + consensus + security-review checklist green.

**Revisit:** Reputation-gated auto-merge for high-trust contributors (Phase 4).

---

**[GOVERNANCE.md](https://github.com/rahiakil/agents-unite/blob/main/docs/GOVERNANCE.md)** · **[CODEOWNERS](https://github.com/rahiakil/agents-unite/blob/main/.github/CODEOWNERS)**

Series: Architecture Decision Records · #7 of 12
