# ADR: Weekly doc cleanup vs persistent trends

**Status:** Accepted (2026-06-07)

**Context:** Documentation drifts; trend/analysis artifacts must compound. Need distinct lifecycles.

**Decision:**

| Class | Examples | Cleanup |
|-------|----------|---------|
| **Ephemeral docs** | Draft ADRs, outdated HOWTOs, broken links in `docs/` | **Weekly** — maintainer issue [`doc-cleanup`](https://github.com/rahiakil/agents-unite/issues/new?template=doc_cleanup.yml) or scheduled triage |
| **Persistent analysis** | `data/_patterns/`, `data/_findings/`, hourly pattern shards, merged reports | **Never delete** — only append or supersede via new files |
| **Compiled summaries** | `data/_index/`, wiki ingest | Regenerated from source data; old index kept in git history |
| **ADRs / gists** | `gists/adrs/`, `raw/DECISIONS.md` | Supersede with new ADR; mark old “Superseded by #N” |

**Rationale:**

- Trends once captured are **alpha memory** — deleting them defeats the product thesis.
- Docs that lie (wrong commands, removed scripts) erode contributor trust — prune aggressively.

**Consequences:**

- Weekly GitHub issue auto-created (future workflow) or manual Monday triage.
- `doc-stale` label on issues referencing obsolete pages.
- Gist series republished when ADR count changes (`./scripts/publish-gists.sh --series adrs`).

**Revisit:** Automated link checker in CI for `docs/` only.

---

Series: Architecture Decision Records · #12 of 12
