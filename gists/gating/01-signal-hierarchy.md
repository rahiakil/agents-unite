# L0 reports → L4 execution. Nothing auto-trades in v1.

agents-unite v1 is **sentiment collection only**. No brokers. No financial advice.

```
reports → consensus → signal gate → strategy → (optional) execution
```

| Layer | Artifact | Tradable? |
|-------|----------|-----------|
| L0 | `report.<user>.md` | No — noisy, single contributor |
| L1 | `consensus.md` | No — not validated for execution |
| L2 | `signals/YYYY-MM-DD.json` | Candidate — passes automated gates |
| L3 | Strategy backtest approval | Yes — human or CI-approved model |
| L4 | Execution | Broker integration, out of repo scope |

Gating is **deliberate friction**. Raw sentiment is inputs; trades require explicit approval.

---

**[TRADING.md](https://github.com/rahiakil/agents-unite/blob/main/docs/TRADING.md)**

Series: Signal Gating Criteria · #1 of 5
