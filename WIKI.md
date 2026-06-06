# WIKI.md — LLM Wiki maintainer schema

> Pattern from [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).  
> **You (the LLM) maintain `wiki/`. Humans curate sources; you do the bookkeeping.**

## Three layers

| Layer | Path | Who writes | Rule |
|-------|------|------------|------|
| **Raw sources** | `data/`, `raw/` | Contributors + humans | **Immutable.** Read only. Never edit. |
| **Wiki** | `wiki/` | **LLM (you)** | Compiled, interlinked, compounding knowledge |
| **Schema** | `WIKI.md` (this file) | Human + LLM co-evolve | Conventions and workflows |

```
data/YYYY-MM-DD/TICKER/report.md  ──ingest──►  wiki/tickers/TICKER.md
raw/THINKING.md                   ──ingest──►  wiki/concepts/*.md
                                              └──►  wiki/index.md, overview.md, log.md
```

## Your job

When asked to **ingest**, **query**, or **lint** the wiki:

1. Read `wiki/index.md` first (navigation)
2. Follow the workflow below
3. Update cross-links using `[[wikilinks]]`
4. Append to `wiki/log.md` (never rewrite history)
5. Update `wiki/index.md` when pages are added/changed

Humans browse the wiki (Obsidian, GitHub, or search). **You write it.**

---

## Directory layout

```
wiki/
├── index.md              # Catalog of all pages (update on every ingest)
├── log.md                # Append-only timeline
├── overview.md           # Rolling market synthesis / thesis
├── tickers/              # One page per ticker (entity pages)
│   └── AAPL.md
├── days/                 # One page per trading day rollup
│   └── 2026-06-05.md
├── themes/               # Cross-ticker narratives (AI capex, Fed, etc.)
├── concepts/             # System + market concepts
│   └── distributed-collection.md
└── .ingest-state.json    # Machine state — update via scripts/wiki_ingest.py
```

---

## Page conventions

### Frontmatter (all wiki pages)

```yaml
---
type: ticker | day | theme | concept | source | synthesis
updated: 2026-06-06
sources: 3                    # count of raw reports integrated
confidence: high | medium | low
tags: [mega-cap, ai, demo]
relates_to:
  - page: "[[NVDA]]"
    rel: correlates_with       # supports | contradicts | extends | correlates_with
---
```

### Ticker page (`wiki/tickers/TICKER.md`)

Sections:

1. **Snapshot** — latest sentiment score, date, label
2. **Trend** — table of recent scores by date (append rows on ingest)
3. **Key themes** — bullets with `[[theme links]]`
4. **Bull / bear cases** — evolving, note contradictions
5. **Notable events** — dated catalysts
6. **Sources** — links to raw `data/DATE/TICKER/` (never duplicate URLs inline without citation)
7. **Open questions** — what to watch next

On ingest: **merge** new data into existing page. Do not replace wholesale unless contradicted — then note both views.

### Day page (`wiki/days/YYYY-MM-DD.md`)

- Market mood summary (avg sentiment, breadth)
- Table of all tickers reported that day
- Links to `[[tickers]]` and `[[themes]]`
- Notable cross-ticker patterns

### Theme page (`wiki/themes/*.md`)

- Narrative spanning multiple tickers (e.g. `[[ai-capex]]` links NVDA, MSFT, GOOGL)
- Update when new reports touch the theme

### Concept page (`wiki/concepts/*.md`)

- System design or market structure (from `raw/` or docs)
- Example: `[[verifier-consensus]]`, `[[distributed-collection]]`

---

## Operations

### Ingest

**Trigger:** new or updated file in `data/YYYY-MM-DD/TICKER/` or `raw/*.md`

```bash
python3 scripts/wiki_ingest.py              # list pending
python3 scripts/wiki_ingest.py --prompt     # print agent prompt for next pending
python3 scripts/wiki_ingest.py --mark-done 2026-06-05 AAPL
```

**Ingest workflow (follow in order):**

1. Read the raw source (`data/.../report.md` + `sources.json`) — do not modify it
2. Discuss key takeaways with the user if interactive; otherwise proceed
3. Update or create `wiki/tickers/TICKER.md`
4. Update or create `wiki/days/YYYY-MM-DD.md`
5. Update relevant `wiki/themes/*.md` pages (create if missing)
6. Revise `wiki/overview.md` if the new data changes the broad thesis
7. Update `wiki/index.md`
8. Append entry to `wiki/log.md`:

   ```markdown
   ## [2026-06-06] ingest | AAPL 2026-06-05 | score +0.62
   - Updated [[AAPL]], [[2026-06-05]], [[ai-integration]]
   - Sources: data/2026-06-05/AAPL/
   ```

9. Run `python3 scripts/wiki_ingest.py --mark-done DATE TICKER`

**One source may touch 5–15 wiki pages.** That is expected.

### Query

**Trigger:** user asks a question about trends, tickers, or the system

1. Read `wiki/index.md`
2. Open relevant pages (use `python3 scripts/wiki_search.py "query"` if needed)
3. Synthesize answer with citations: `[[AAPL]]`, `data/2026-06-05/AAPL/report.md`
4. **File good answers back:** if the synthesis is durable, add to `wiki/overview.md` or create `wiki/synthesis/QUESTION-SLUG.md`

Prompt template: [`agents/wiki-query.md`](agents/wiki-query.md)

### Lint

**Trigger:** periodically, after bulk ingests, or on user request

Check for:

- [ ] Contradictions between ticker pages and day summaries
- [ ] Stale claims (newer raw source supersedes old wiki text)
- [ ] Orphan pages (no inbound `[[links]]`)
- [ ] Tickers in `data/` with no `wiki/tickers/` page
- [ ] Missing cross-references (NVDA mentions Blackwell but no link to `[[ai-capex]]`)
- [ ] `wiki/index.md` out of sync with actual files
- [ ] Themes mentioned ≥2 times without a theme page

For **market sentiment** domains: contradictions between bullish/bearish reports on the same day are **information**, not defects. Preserve both; add `rel: contradicts` in frontmatter. Do not silently merge away disagreement.

Prompt template: [`agents/wiki-lint.md`](agents/wiki-lint.md)

---

## Relationship to other systems

| System | Role |
|--------|------|
| `data/` | Raw contributor reports — source of truth for daily facts |
| `data/_index/` | Machine summaries — ingest input, not wiki replacement |
| `raw/` | Product/design thinking — ingest into `wiki/concepts/` |
| `docs/` | Stable architecture specs — link from wiki, don't duplicate |
| `README.md` | Public dashboard — auto-updated stats, not deep knowledge |

**Wiki indexes and synthesizes.** It does not replace `data/` or duplicate every report verbatim.

---

## Search

At current scale (~hundreds of pages), `wiki/index.md` + grep is enough:

```bash
python3 scripts/wiki_search.py "NVDA Blackwell"
python3 scripts/wiki_search.py --tags ai
```

When the wiki grows past ~100 pages, consider [qmd](https://github.com/tobi/qmd) or similar local hybrid search.

---

## Tips

- **Obsidian:** open `wiki/` as a vault; graph view shows hub tickers and themes
- **Git:** wiki is versioned markdown — diffs show how thesis evolved
- **Demo data:** pages seeded from `data/2026-06-05/` are marked `confidence: low` / demo — upgrade as real reports arrive
- **Never edit `data/` during wiki ops** — only read

---

## Quick commands

```bash
python3 scripts/wiki_ingest.py --prompt    # ingest next pending report
python3 scripts/wiki_search.py "sentiment" # find wiki pages
make wiki-pending                          # list pending ingests
```

When in doubt: read index → ingest → cross-link → log → lint.
