# Simulation results

Seed 20261121. Provider `rule`. Model `rule`. Agents 34. Days 6 starting 2026-11-20. Market as of 2026-11-20.

Chain attempts are the production path: one assigned focus, one prompt variant, real validators. Other focus and prompt cells are logged for the second paper and do not enter consensus.

## Headline

- Chain attempts: 210
- False accepts (blocked behavior entered consensus): 0
- False rejects (allowed behavior kept out of consensus): 0
- Consensus MAE vs headline tone: 0.2627
- Consensus rows with a headline tone: 47
- Forward-return pairs: 0 (sign hits 0)
- Duplicate second attempts that merged: 0

Forward-return pairs stay empty until a later snapshot has the next close. The 2026-11-20 batch is the live tape. Later seeded days reuse it, so this file has no next-day return yet.

Colluding accounts are allowed into the consensus input. Reputation falls when their score sits away from the recomputed median. A member who pulls that median toward the pump can climb back. The day table shows both moves.

## Acceptance by persona

| Persona | Attempts | Merge rate | Consensus-eligible rate |
| --- | --- | --- | --- |
| colluding-ring | 24 | 1.0 | 1.0 |
| contrarian | 12 | 1.0 | 1.0 |
| momentum | 18 | 1.0 | 1.0 |
| news-reactive | 18 | 1.0 | 1.0 |
| novice | 18 | 1.0 | 1.0 |
| prompt-injection | 12 | 0.5 | 0.0 |
| sector-specialist | 12 | 1.0 | 1.0 |
| social | 18 | 1.0 | 1.0 |
| spammer | 36 | 0.5 | 0.1667 |
| sybil | 24 | 0.75 | 0.75 |
| value | 18 | 1.0 | 1.0 |

## Acceptance by behavior

| Behavior | Attempts | Merge rate | Consensus-eligible rate |
| --- | --- | --- | --- |
| duplicate | 12 | 0.5 | 0.5 |
| fabricated | 6 | 1.0 | 0.0 |
| honest | 114 | 1.0 | 1.0 |
| inject_scope | 6 | 0.0 | 0.0 |
| inject_text | 6 | 1.0 | 0.0 |
| pump | 24 | 1.0 | 1.0 |
| spam_malformed | 6 | 0.0 | 0.0 |
| spam_scope | 6 | 0.0 | 0.0 |
| stale | 6 | 1.0 | 0.0 |
| sybil_pump | 18 | 1.0 | 1.0 |
| wrong_hash | 6 | 0.0 | 0.0 |

## Consensus error by day

- 2026-11-20: 0.2531
- 2026-11-21: 0.2609
- 2026-11-22: 0.1894
- 2026-11-23: 0.4069
- 2026-11-24: 0.3115
- 2026-11-25: 0.1603

## Reputation by day

- 2026-11-20: colluding-ring 0.456, contrarian 0.5454, momentum 0.6037, news-reactive 0.715, novice 0.7069, prompt-injection 0.5824, sector-specialist 0.674, social 0.6583, spammer 0.5702, sybil 0.4214, value 0.6148
- 2026-11-21: colluding-ring 0.4474, contrarian 0.6678, momentum 0.6791, news-reactive 0.7778, novice 0.7776, prompt-injection 0.6113, sector-specialist 0.7354, social 0.7512, spammer 0.6148, sybil 0.4049, value 0.7071
- 2026-11-22: colluding-ring 0.4988, contrarian 0.7242, momentum 0.6914, news-reactive 0.7966, novice 0.7836, prompt-injection 0.5946, sector-specialist 0.7468, social 0.7357, spammer 0.6275, sybil 0.4092, value 0.7614
- 2026-11-23: colluding-ring 0.488, contrarian 0.6883, momentum 0.7134, news-reactive 0.7796, novice 0.8126, prompt-injection 0.6101, sector-specialist 0.7104, social 0.7716, spammer 0.6148, sybil 0.4869, value 0.763
- 2026-11-24: colluding-ring 0.4888, contrarian 0.6917, momentum 0.6948, news-reactive 0.8067, novice 0.8297, prompt-injection 0.6101, sector-specialist 0.7453, social 0.7991, spammer 0.6114, sybil 0.493, value 0.7899
- 2026-11-25: colluding-ring 0.5355, contrarian 0.7042, momentum 0.6824, news-reactive 0.8171, novice 0.8123, prompt-injection 0.5937, sector-specialist 0.7696, social 0.7888, spammer 0.6273, sybil 0.5263, value 0.8119

## Adversary detection latency (days from day 0)

- colluding-ring: 0.3333
- prompt-injection: 0.0
- spammer: 0.0
- sybil: 0.0

Still undetected:
- sim-ring-02 (pump)

## Prompt and mode

Mean rule score for the honest personas, by focus mode and prompt variant.

- mode full: 0.0181
- mode news: 0.0962
- mode sentiment: 0.0187
- mode social: 0.0476
- mode trading: 0.0513
- prompt baseline: 0.0516
- prompt skeptic: 0.0357
- prompt terse: 0.0518

## Stage failures

- consensus: 54
- merge: 30
- scope_guard: 24
- validation: 6

## How to run

```bash
python3 -m sim --provider rule --check
python3 -m sim --daily --history sim/history --provider auto --llm-cap 11 --check
python3 -m sim.learnings --history sim/history --every 15
```

The seeded command refreshes `sim/metrics.db`, `sim/attempts.jsonl`, and this file. The daily command appends a new JSONL file under the history directory and does not rewrite older runs. Provider secrets are listed in `sim/PROVIDERS.md`.
