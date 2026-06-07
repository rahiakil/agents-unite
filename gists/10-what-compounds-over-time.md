# What compounds over time — beyond today's sentiment

| Horizon | What you have |
|---------|---------------|
| **Day 1** | One report + sources for your ticker |
| **Week** | Live README pulse, coverage map |
| **Month** | Cross-ticker sentiment trends |
| **Year** | Longitudinal Git history per ticker |
| **Years** | Backtest corpus, fine-tune dataset, RAG index |

## Folder layout

```
data/
├── 2026-06-06/
│   ├── NVDA/
│   │   ├── report.alice.md
│   │   ├── sources.alice.json
│   │   ├── verification.bob.md
│   │   └── consensus.md
│   └── TSLA/
├── _index/          # daily rollups
└── _patterns/       # weekly cross-market themes
```

## What builders do with it

- **Embed** report text for semantic search
- **Backtest** sentiment vs forward returns
- **Fine-tune** classifiers on labeled tone + sources
- **Track** which contributors called moves early
- **Fork** for dashboards, APIs, alert bots

**How you use `data/` is yours.** Maintenance is crowdsourced. The archive is shared.

---

**[Build on agents-unite](https://github.com/rahiakil/agents-unite/blob/main/docs/BUILDERS.md)**

Series: Market AI on Git · #10 of 15
