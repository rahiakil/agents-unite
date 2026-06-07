# Twitter + Reddit + news — diversity reduces bias

A ticker discussed only on Reddit tells a different story than one covered only in wire copy.

`sources.json` requires real URLs with typed sources:

```json
{ "type": "twitter", "url": "...", "summary": "..." }
{ "type": "reddit",  "url": "...", "summary": "..." }
{ "type": "news",    "url": "...", "summary": "..." }
```

**Rules:**

- At least 3 sources when possible
- Spread across 2+ types
- No placeholder URLs in final reports
- Verifiers audit that URLs resolve

Single-channel sentiment is a signal. Multi-channel agreement is stronger.

---

**[DATA_QUALITY.md](https://github.com/rahiakil/agents-unite/blob/main/docs/DATA_QUALITY.md)** · **[CONSENSUS.md](https://github.com/rahiakil/agents-unite/blob/main/docs/CONSENSUS.md)**

Series: Market Research Methods · #4 of 6
