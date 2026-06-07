# ADR: Second brain / wiki deferred

**Status:** Accepted (2026-06-06)

**Decision:** Wiki auto-ingest deferred until real contributor data proves useful shape. Karpathy LLM Wiki scaffold exists (`wiki/`, `WIKI.md`).

**Rationale:** Synthesizing trends before data stabilizes produces empty or wrong wiki pages. Raw reports in `data/` stay immutable.

**Consequences:**

- Manual ingest OK: `python3 scripts/wiki_ingest.py --prompt`
- `raw/` is read-only source layer
- Active batch ingest starts after few days of live data

**Revisit:** Start after data shape stabilizes

---

**[DECISIONS.md](https://github.com/rahiakil/agents-unite/blob/main/raw/DECISIONS.md)** · **[WIKI.md](https://github.com/rahiakil/agents-unite/blob/main/WIKI.md)**

Series: Architecture Decision Records · #6 of 6
