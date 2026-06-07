# Market AI on Git — GitHub Gist series

15 public gists explaining **agents-unite**: crowdsourced agentic LLM market research in one repo.

## Why gists?

Millions run stock sentiment agents daily and **never publish the output**. Gists are a lightweight way to spread the narrative before people clone the repo — each post is shareable, linkable, and points home to [agents-unite](https://github.com/rahiakil/agents-unite).

## Series outline

| # | File | Topic |
|---|------|-------|
| 1 | `01-millions-research-alone-history-disappears.md` | The problem — ephemeral private research |
| 2 | `02-burn-pennies-read-thousands.md` | Crowdsource vs solo token burn |
| 3 | `03-one-ticker-one-pr-one-day.md` | The daily mission |
| 4 | `04-git-is-the-ledger.md` | Git as append-only belief ledger |
| 5 | `05-verifiers-distributed-audit.md` | Verifier role (validator metaphor) |
| 6 | `06-consensus-weighted-median.md` | Consensus algorithm |
| 7 | `07-multi-agent-diversity.md` | Harness adapters |
| 8 | `08-assignment-math.md` | Deterministic assignment |
| 9 | `09-clone-cron-forget.md` | Setup + automation |
| 10 | `10-what-compounds-over-time.md` | Long-term data upside |
| 11 | `11-build-on-open-data.md` | Algo / RAG builders |
| 12 | `12-roles-pipeline.md` | research → verify → consensus |
| 13 | `13-trust-immutable-prompts.md` | CI + prompt provenance |
| 14 | `14-vs-solo-token-burn.md` | Tokens + timing |
| 15 | `15-join-agents-unite.md` | Call to action |

## Publish

Requires [GitHub CLI](https://cli.github.com/) (`gh auth login`):

```bash
./scripts/publish-gists.sh           # create all public gists + index
./scripts/publish-gists.sh --dry-run
```

Output: `gists/published.json` with URLs. Share `index_url` or the [website](https://rahiakil.github.io/agents-unite/).

## Expand the series

Add entries to `manifest.yaml` and new `.md` files. Re-run publish (creates new gists; does not update existing — edit gists on GitHub or delete and republish).

Taglines bank for future posts: [`docs/TAGLINES.md`](../docs/TAGLINES.md)

## Social rollout

1. Post gist #1 on X/LinkedIn/HN — hook with "millions burn tokens, history vanishes"
2. Thread through #2–#5 (crowd + ledger + verifiers)
3. Pin gist #15 (join) in repo README Discussions
4. Link `published.json` index from README

Not investment advice.
