# Trading Strategy Gating (Future)

agents-unite v1 is **sentiment collection only**. No trade execution, no financial advice, no automated brokers.

This document defines how future trading strategies may **consume** consensus signals safely.

## Principle

> Raw contributor reports are **inputs**. Consensus signals are **candidates**. Trades require **explicit gating**.

```
reports → consensus → signal gate → strategy → (optional) execution
```

Nothing in v1 or v2 auto-trades. Gating is deliberate friction.

## Signal hierarchy

| Layer | Artifact | Tradable? |
|-------|----------|-----------|
| L0 | `report.md` | No — noisy, single contributor |
| L1 | `consensus.md` | No — still not validated for execution |
| L2 | `signals/YYYY-MM-DD.json` | Candidate — passes automated gates |
| L3 | Strategy backtest approval | Yes — human or CI-approved model |
| L4 | Execution | Broker integration, out of repo scope |

## Gating rules (proposed)

A ticker/day may emit an L2 signal only if **all** conditions hold:

### 1. Consensus confidence

```
confidence ∈ {medium, high}
```

Low-confidence consensus never produces trade candidates.

### 2. Score magnitude

```
|consensus_score| ≥ 0.25
```

Weak sentiment is recorded but not actionable.

### 3. Source diversity

Consensus merge must include sources from ≥ 2 types (twitter/reddit/news) and ≥ 5 unique URLs aggregate.

### 4. Liquidity filter

Ticker must be in `tickers/universe.json` with:

- `active: true`
- Average daily volume above configurable threshold (future `liquidity_min` field)
- Not classified `sector: "ETF"` unless strategy explicitly allows ETFs

### 5. Event risk

If **Notable Events** include earnings within ±2 sessions or FDA/binary catalyst, signal is **blocked** unless strategy opts in (`allow_event_risk: true`).

### 6. Reputation floor

At least one contributing report from a contributor with `reputation ≥ 0.5` (future ledger).

## Signal artifact

`signals/YYYY-MM-DD.json`:

```json
{
  "date": "2026-06-05",
  "generated_at": "2026-06-05T23:00:00Z",
  "signals": [
    {
      "ticker": "NVDA",
      "direction": "long",
      "consensus_score": 0.42,
      "confidence": "high",
      "gates_passed": [
        "confidence",
        "magnitude",
        "source_diversity",
        "liquidity",
        "reputation"
      ],
      "gates_failed": [],
      "strategy_tags": ["momentum-sentiment-v1"]
    }
  ]
}
```

`direction` derives from score sign: positive → `long`, negative → `short`, near zero → omitted.

## Strategy registry

Future `strategies/` directory:

```
strategies/
├── momentum-sentiment-v1.yaml
└── mean-reversion-sentiment-v1.yaml
```

Example strategy manifest:

```yaml
id: momentum-sentiment-v1
version: 1
description: Follow high-confidence bullish consensus among large-cap tech
filters:
  sectors: [Technology]
  min_consensus_score: 0.35
  confidence: [high]
  max_positions: 10
risk:
  max_weight_per_ticker: 0.05
  allow_event_risk: false
execution:
  mode: paper  # paper | live
  broker: null
```

Strategies **declare** which gates they require; `scripts/emit_signals.py` (future) intersects strategy filters with L2 gating.

## Backtest requirement

Before `execution.mode: live`:

1. Strategy must have `backtests/<strategy-id>/summary.json` in repo
2. CI checks Sharpe, max drawdown, and sample size thresholds
3. Maintainer approval label on strategy PR

## Paper trading phase

Default execution mode is **paper**:

- Log intended orders to `executions/paper/YYYY-MM-DD.jsonl`
- Compare fills against next-day open (future market data adapter)
- No API keys in this repository

## Live execution (out of scope)

Live trading requires:

- External broker service (not in agents-unite)
- User-owned API credentials
- Regulatory compliance — user's responsibility

The repo may publish signals; it will **not** hold funds or keys.

## Risk disclosures

- Sentiment ≠ fundamentals
- Social media is manipulable
- Consensus reduces but does not eliminate false signals
- Past sentiment correlation does not guarantee future returns

## Implementation roadmap

| Milestone | Deliverable |
|-----------|-------------|
| T1 | Consensus scoring stable |
| T2 | `scripts/emit_signals.py` + gate engine |
| T3 | `strategies/*.yaml` + paper log |
| T4 | Backtest harness |
| T5 | Optional external execution bridge |

## What contributors should know today

Your daily report **will not trigger trades**. Write accurate sentiment and cite real sources; future systems depend on data quality you create now.
