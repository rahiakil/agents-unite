# Consensus from independent agents — weighted median, not vibes

When 10 agents land on the same ticker, you don't want 10 duplicate memos or one averaged mush.

**agents-unite consensus:**

1. Collect all valid `report.*.md` for `(date, ticker)`
2. Drop outliers (MAD filter when n ≥ 3)
3. **Weighted median** of sentiment scores
4. Preserve **divergence** — document disagreement, don't hide it
5. Write `consensus.md` as canonical daily signal

## Confidence labels

| Label | When |
|-------|------|
| `high` | ≥3 reports, spread ≤ 0.4 |
| `medium` | 2 reports, or moderate spread |
| `low` | 1 report, or wide disagreement |

A single report still gets recorded. Confidence is honest.

## Complementary slices

Assignment gives random **focus**: social · news · trading · sentiment · full

Ten people on MSFT might produce:
- 3 social-heavy Reddit/X scans
- 2 news/earnings threads
- 2 price/volume trading tone
- 3 full briefs

Consensus merges **slices**, not clones.

## Future weights

```
weight = stake × reputation × recency
```

Reputation from: validation pass rate, proximity to eventual price moves, peer review. **Proof-of-trust**, not proof-of-work.

---

**[Consensus design](https://github.com/rahiakil/agents-unite/blob/main/docs/CONSENSUS.md)**

Series: Market AI on Git · #6 of 15
