# Study schema

The JSONL file is the source of truth. `sim/metrics.db` is a derived copy of one run. The daily job appends a new file under `history/runs/` on the `sim-data` branch and rewrites `history/summary.json`. Old JSONL files stay byte-for-byte.

## Files

| Path | Role |
| --- | --- |
| `sim/attempts.jsonl` | Every event from the seeded proof run |
| `sim/metrics.db` | SQLite copy of that run |
| `sim/summary.json` | Rollup used by `sim/RESULTS.md` |
| `sim/reputation.json` | Ledger at the end of the seeded run |
| `sim/fixtures/batch-2026-11-20.json` | Prices, headlines, and posts from the real batch |
| `history/runs/*.jsonl` | Append-only archive, one file per cloud day |
| `history/learnings/*.md` | Cadence report from `python3 -m sim.learnings` |

SQLite tables: `runs (run_id, seed, provider, model, days, n_agents)` and `events` with the indexed columns plus `payload` holding the full JSON object.

## Event types

Every object has `record_type`, `run_id`, and `seed` when the harness wrote it.

### stage

`assignment`, `generation`, `validation`, `scope_guard`, `merge`, `consensus`.

Fields: `day`, `day_index`, `contributor`, `persona`, `behavior`, `origin` (`simulated`), `ticker`, `attempt`, `chain`, `stage`, `passed`, `failure_reason`, `latency_ms`. Generation rows also carry `prompt_id`, `prompt_hash`, `focus`, `provider`, `model`. Consensus rows carry `eligible` and `consensus_kept`. `failure_reason` on consensus is empty, `mad_outlier`, or `verifier_rejected`.

### submission

One row per chain attempt and one row per prompt/mode cell.

Chain rows (`chain: true`) are the production path: assigned focus, the day's prompt variant, real `validate_submitter_report` and `validate_scope`. Cells (`chain: false`) vary focus across `sentiment`, `news`, `social`, `trading`, `full` and the files in `sim/prompts/`. Cells do not merge and do not vote.

Fields used for paper 2:

| Field | Meaning |
| --- | --- |
| `persona`, `behavior`, `collusion_id` | Archetype and attack |
| `prompt_id`, `prompt_hash` | Variant file stem and SHA256 |
| `focus`, `assigned_focus`, `focus_prompt_file`, `focus_prompt_hash` | Mode under test and the mode the hash assigned |
| `provider`, `model`, `prompt_tokens`, `completion_tokens`, `cost_usd`, `model_latency_ms`, `fallback_reason` | Generator. `cost_usd` is 0 for `rule`, `openrouter/free`, and models ending in `:free`. Other prices stay null |
| `score`, `news_tone`, `social_tone`, `change_pct` | Score, headline tone, social tone, same-day move |
| `forward_return` | Next later close over this close, minus one. Null until a second priced date exists |
| `market_asof`, `market_input` | Which tape the persona read |
| `expect_eligible`, `merged`, `eligible`, `consensus_kept` | Gate labels. `eligible` is filled from the consensus stage (verifier approval), then joined into the summary |
| `main_ledger_blocked` | True for every simulated row. Contributor Guard rejects these identities on main |
| `timing` | `on_time` or `late` (late recency weight 0.25) |

### consensus

One row per ticker per day. `consensus_score` is the weighted median after MAD. `ground_truth` is `news_tone`. `abs_error` is the absolute gap. `leader` is the first elected publisher whose score matches the recomputation within 0.02. `leader_cheats_rejected` counts publishers the harness refused. `forward_return` and `change_pct` sit on this row too. `render_valid` is true when the written `consensus.md` passes `validate_consensus`.

### reputation

One row per contributor per day. `reputation` is the ledger value after that day's evidence. A pass is a merge (schema, scope, and the one-file rule). Proximity is measured only on merged reports, against the recomputed consensus. Formula: `0.15 * pass_rate + 0.70 * proximity + 0.15 * peer`, add-one smoothing, clamp `[0.02, 0.99]`. Prior is 0.5. Weight in the median is `stake * reputation * recency` with stake 1.

### detection

First day an attack identity is caught. `reason` is the validator or scope message, `mad_outlier`, `verifier_rejected`, or `reputation_below_floor`. Latency in the rollup is `day_index` of that row. Pump and sybil scores are schema-valid, so detection is MAD or reputation, not the schema gate.

## Rollup

`python3 -m sim.summarize` is internal. The CLI prints the headline and writes `RESULTS.md`.

`python3 -m sim.learnings --history PATH --from YYYY-MM-DD --to YYYY-MM-DD --every 15`

The cadence flag writes only when the number of distinct days in the window is a positive multiple of 15. `--force` writes anyway. The daily workflow calls this with `--every 15`.

False accept: a blocked behavior (`spam_malformed`, `spam_scope`, `inject_text`, `inject_scope`, `fabricated`, `stale`, `wrong_hash`) became verifier-approved. False reject: an identity that should be eligible was kept out. Pump and sybil scores are eligible on purpose. The duplicate behavior is eligible on attempt 1 and blocked on attempt 2.
