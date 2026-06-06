# Wiki Query Agent

You are answering a question using the **agents-unite LLM wiki** — not raw RAG over `data/`.

Read [`WIKI.md`](../WIKI.md) first.

## Question

{{QUESTION}}

## Workflow

1. Read `wiki/index.md`
2. Search if needed: `python3 scripts/wiki_search.py "{{QUESTION}}"`
3. Open 2–5 relevant wiki pages
4. Synthesize an answer with citations:
   - Wiki pages: `[[AAPL]]`, `[[ai-capex]]`
   - Raw sources when citing facts: `data/2026-06-05/AAPL/report.md`
5. If contradictions exist in the wiki, surface them — do not flatten disagreement

## Output format

```markdown
# Answer: <short title>

## Summary
2–4 sentences.

## Evidence
| Claim | Source |
|-------|--------|
| ... | [[NVDA]] / data/... |

## Contradictions / gaps
- ...

## Suggested follow-ups
- ...
```

## File back (optional)

If this answer is durable (not a one-off), ask the user or write:

- `wiki/synthesis/<slug>.md` — for reusable analyses
- Or append a paragraph to `wiki/overview.md`

Append to `wiki/log.md`:

```
## [{{TODAY}}] query | <short title>
```
