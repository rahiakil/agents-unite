# Pre-register outputs via schema

Post-hoc narrative fitting is the enemy of honest market research.

Every report declares upfront in YAML frontmatter:

```yaml
sentiment_score: 0.35
prompt_hash: 16b431faca503ced
prompt_file: agents/investigation-social.md
daily_role: research
focus: social
```

Fixed H1 sections — Sentiment, Key Themes, Sources, Price Snapshot, Notable Events — prevent moving goalposts. CI rejects malformed or empty reports.

**Roadmap:** `bull_case`, `bear_case`, `time_horizon` fields for prediction tracking.

Schema is the contract. The agent fills the contract; it does not improvise structure.

---

**[METHODS.md](https://github.com/rahiakil/agents-unite/blob/main/docs/METHODS.md)** · **[DATA_QUALITY.md](https://github.com/rahiakil/agents-unite/blob/main/docs/DATA_QUALITY.md)**

Series: Market Research Methods · #3 of 6
