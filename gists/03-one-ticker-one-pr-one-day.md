# One agent. One ticker. One PR. The smallest mission that scales.

People finish tasks they can see the end of.

```
Today's assignment:  MSFT
Your job:            Summarize what the market is saying (last 24–72h)
Your output:         One PR → data/2026-06-06/MSFT/
Your time:           ~15 minutes of agent time
```

Not "research the entire market." Not "build a terminal." **One folder. One day. Done.**

## What's in the PR

Two files, strict schema:

```yaml
# report.<github-user>.md
---
ticker: MSFT
date: 2026-06-06
github_username: you
sentiment_score: 0.42   # -1.0 to +1.0
prompt_hash: abc123      # proves which template was used
---
# Sentiment
# Key Themes
# Sources
# Price Snapshot
# Notable Events
```

```json
// sources.<user>.json — real URLs only
{ "sources": [
  { "type": "reddit", "url": "https://...", "title": "..." },
  { "type": "news", "url": "https://...", "title": "..." }
]}
```

CI validates on every PR. Bad schema → rejected. **Quality by construction.**

## Scale

4,000 contributors × 1 ticker × 1 day = **4,000 tickers covered daily.**

Each PR is tiny. The README **auto-updates** live coverage and sentiment pulse on every merge.

---

**[Run your first assignment](https://github.com/rahiakil/agents-unite/blob/main/docs/HARNESS.md)**

Series: Market AI on Git · #3 of 15
