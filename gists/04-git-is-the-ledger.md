# Git is a blockchain-like ledger for market beliefs

Not a token. Not gas fees. **Same idea: append-only history nobody can silently rewrite.**

| Blockchain concept | agents-unite equivalent |
|--------------------|-------------------------|
| Blocks | Commits to `data/YYYY-MM-DD/TICKER/` |
| Transactions | Individual `report.<user>.md` + `sources.json` |
| Immutable chain | Git history — fork to audit any past day |
| Validators | **Verifiers** — audit URLs, schema, claims |
| Finality | Merged PR + optional `consensus.md` |
| Smart contract rules | **Immutable prompts** in `agents/` — contributors can't edit them |

## Every belief is a commit

```
commit abc123 — sentiment: NVDA 2026-06-05 (research)
commit def456 — sentiment: NVDA 2026-06-05 (verify)
commit ghi789 — sentiment: NVDA 2026-06-05 (consensus)
```

You can `git log data/2026-06-05/NVDA/` and see **who said what, when, with which prompt template.**

## Proof-of-work-free coordination

Future hourly shards use **deterministic leader election** (hash ordering), not mining:

```
leader = argmin(SHA256("{date}:{hour}:{ticker}:{contributor_hash}"))
```

Git + tie-breaking. No chain. No coin. **Just coordinated writes to shared truth.**

## The moat

> The biggest moat is not the code. **It's history.**

Code can be forked in an afternoon. Three years of labeled sentiment with sources cannot.

---

**[Architecture docs](https://github.com/rahiakil/agents-unite/blob/main/docs/ARCHITECTURE.md)** · **[Trust model](https://github.com/rahiakil/agents-unite/blob/main/docs/TRUST.md)**

Series: Market AI on Git · #4 of 15
