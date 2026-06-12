# ADR: Data corrections and amendments via GitHub

**Status:** Accepted (2026-06-07)

**Context:** Users will find wrong summaries, bad consensus, or stale records. Corrections must be auditable and git-native.

**Decision:**

All corrections flow through **GitHub** — never silent edits to history.

| Scenario | Mechanism |
|----------|-----------|
| “This summary is wrong” | Issue → [`data-correction` template](https://github.com/rahiakil/agents-unite/issues/new?template=data_correction.yml) |
| “Add info to old day/ticker” | Issue → [`record-amendment` template](https://github.com/rahiakil/agents-unite/issues/new?template=record_amendment.yml) → PR with **new** files (never delete raw report) |
| “Verifier missed fake URL” | New `verification.<user>.md` with `rejected` + follow-up research PR |
| “Consensus should be recomputed” | Issue labeled `consensus-rebuild` → consensus agent re-run on branch |

**Amendment rule:** Do **not** rewrite merged `report.*.md`. Add:

- `amendment.<user>.<seq>.md` + optional `sources.amendment.<user>.<seq>.json`
- Or new research report same day if policy allows collision (ADR #2)

**Rationale:**

- Git blame stays honest — financial memory requires provenance.
- Issues capture **why** a change was requested (feeds future reputation scoring).

**Consequences:**

- Maintainers triage `data-correction` weekly.
- Valid amendments → verify → consensus update PR.
- Malicious amendment spam → contributor reputation gate (Phase 4).

**Revisit:** On-chain attestation — rejected; GitHub is source of truth.

---

**[DATA_CORRECTIONS.md](https://github.com/rahiakil/agents-unite/blob/main/docs/DATA_CORRECTIONS.md)**

Series: Architecture Decision Records · #11 of 12
