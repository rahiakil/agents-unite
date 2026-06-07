# Deterministic assignment — fair coverage, no ticker picking

Contributors **do not choose** their ticker. Assignment is math:

```
ticker_index = SHA256("{date}:{contributor_hash}") % active_ticker_count
```

**Same person + same day → same ticker everywhere in the world.**

## Identity resolution

1. `AGENTS_UNITE_CONTRIBUTOR` env var
2. `github_username` in config
3. `git config user.email`
4. `anonymous` (discouraged — collides with others)

## Coverage optimizer

Tickers with **zero reports today** get 10× weight vs overcrowded names. The universe fills evenly over time.

```json
// tickers/universe.json — 291 seed → 4,000+ community growth
{ "ticker": "NVDA", "active": true, "sector": "Technology" }
```

## Branch naming

```
report/2026-06-06-TSLA-a1b2c3d4
       ^date      ^ticker ^contributor hash
```

CI rejects PRs that touch folders outside your assignment. **Sybil resistance roadmap:** proof-of-human, per-IP caps.

---

**[Architecture](https://github.com/rahiakil/agents-unite/blob/main/docs/ARCHITECTURE.md)**

Series: Market AI on Git · #8 of 15
