# Low-confidence consensus never becomes a trade candidate

When multiple reports disagree, consensus emits a confidence level:

```
confidence ∈ {low, medium, high}
```

**Gate rule:** L2 signals require `confidence ∈ {medium, high}`.

Low-confidence days are still archived in `data/` — they are **recorded, not actionable**.

This prevents thin or contested sentiment from leaking into automated strategies.

Weighted median picks the score; dispersion and verifier notes feed confidence.

---

**[CONSENSUS.md](https://github.com/rahiakil/agents-unite/blob/main/docs/CONSENSUS.md)** · **[TRADING.md](https://github.com/rahiakil/agents-unite/blob/main/docs/TRADING.md)**

Series: Signal Gating Criteria · #2 of 5
