# Reputation floors and per-strategy gates

Future ledger: `contributors/reputation.json` tied to **GitHub username**.

**Reputation floor gate:**

At least one contributing report from a contributor with `reputation ≥ 0.5`.

**Strategy registry:**

Each strategy declares which gates it requires. `emit_signals.py` (future) intersects strategy filters with L2 gating.

```yaml
strategy: momentum_sentiment_v1
requires:
  - consensus_confidence_medium
  - reputation_floor
  - liquidity_min_1m
allow_event_risk: false
```

No strategy runs without naming its gates. No gate passes without a logged artifact.

---

**[TRADING.md](https://github.com/rahiakil/agents-unite/blob/main/docs/TRADING.md)** · **[TRUST.md](https://github.com/rahiakil/agents-unite/blob/main/docs/TRUST.md)**

Series: Signal Gating Criteria · #5 of 5
