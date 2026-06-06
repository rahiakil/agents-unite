# Wiki Lint Agent

Health-check the agents-unite wiki. Read [`WIKI.md`](../WIKI.md).

## Checks

Run through each item. Produce a lint report; fix obvious issues if asked.

### Structure

- [ ] Every file in `wiki/tickers/` is listed in `wiki/index.md`
- [ ] Every file in `wiki/days/` is listed in `wiki/index.md`
- [ ] No orphan pages (pages with zero inbound `[[wikilinks]]` from other wiki pages)

### Data coverage

- [ ] List reports in `data/` not yet in `.ingest-state.json` (run `python3 scripts/wiki_ingest.py`)
- [ ] List tickers with reports but no `wiki/tickers/TICKER.md`

### Consistency

- [ ] Ticker snapshot scores match latest raw report in `data/`
- [ ] Day page ticker table matches reports for that date
- [ ] Stale claims: wiki says X but newer raw source says Y — flag, don't auto-delete

### Sentiment domain rules

- **Contradictions are information.** Two reports disagreeing on MSFT sentiment → preserve both, add `rel: contradicts`, do not merge into one bullish story
- Flag missing expected links (e.g. NVDA page mentions Blackwell but no `[[ai-capex]]`)

### Index freshness

- [ ] `wiki/index.md` last-updated date reasonable
- [ ] `wiki/overview.md` reflects current demo/live data mix

## Output

```markdown
# Wiki lint — YYYY-MM-DD

## Pass
- ...

## Warn
- ...

## Fail
- ...

## Suggested ingests
- data/2026-06-05/TSLA/ (pending)

## Suggested new pages
- wiki/themes/eu-regulation.md (mentioned in AAPL, META)
```

Append to `wiki/log.md`:

```
## [YYYY-MM-DD] lint | N warnings, M failures
```
