# Scientific Methods & Principles

How agents-unite applies research best practices to **crowdsourced market intelligence** — not as buzzwords, but as concrete design choices.

## 1. Independent measurements

**Principle:** Reduce correlated error by separating who investigates, how, and with which tools.

| Mechanism | Implementation |
|-----------|----------------|
| Deterministic assignment | Different contributors → different tickers (high probability) |
| Focus split | Same ticker → different lenses (social / news / trading / full) |
| Multi-LLM diversity | Claude, GPT, Gemini, local models — contributors choose |
| Prompt lock | Canonical templates in `agents/`; `prompt_hash` proves template use |

**Why it matters:** Ensemble methods outperform monoculture when errors are imperfectly correlated — same logic as model ensembles in ML.

## 2. Longitudinal observation

**Principle:** Signal value compounds over time; snapshot opinions are weak alone.

```
NVDA/
 ├── 2025-01-01
 ├── 2025-01-02
 ├── …
 └── 2026-06-01
```

Git preserves **what people believed before outcomes were known**. Later evaluation asks:

- Who was consistently early on bearish themes before earnings misses?
- Which prompts produced actionable source citations?
- Which sources appeared repeatedly before major moves?

This is the **financial data flywheel** — history as moat.

## 3. Pre-registration via schema

**Principle:** Constrain outputs before seeing results to limit post-hoc narrative fitting.

Every report must declare upfront (frontmatter):

```yaml
sentiment_score: 0.35
confidence: 0.72        # roadmap
prompt_hash: ...
prompt_file: agents/investigation-social.md
```

Fixed sections prevent moving goalposts. CI rejects malformed or empty reports.

**Roadmap — prediction tracking:**

```yaml
bull_case: ...
bear_case: ...
expected_price: ...
time_horizon: 30d
```

Evaluate against realized prices later → contributor accuracy scores.

## 4. Robust aggregation (not naive averaging)

**Principle:** Use statistics resistant to outliers and manipulation.

| Step | Method | Doc |
|------|--------|-----|
| Input filter | JSON schema + section validation | [DATA_QUALITY.md](DATA_QUALITY.md) |
| Outlier drop | Median + MAD (n ≥ 3) | [CONSENSUS.md](CONSENSUS.md) |
| Point estimate | Weighted median | [CONSENSUS.md](CONSENSUS.md) |
| Theme merge | Verifier + embedding cluster | [RAG_AND_SYNTHESIS.md](RAG_AND_SYNTHESIS.md) |
| Uncertainty | Confidence label from spread + n | [CONSENSUS.md](CONSENSUS.md) |

Disagreement is **data**, not failure — preserved in consensus Divergence sections.

## 5. Reputation as delayed reward

**Principle:** Weight opinions by track record, not volume.

Planned scoring (PageRank / Stack Overflow / ELO analogs):

```
Contributor A: accuracy 74%  (1-month horizon)
Contributor B: accuracy 52%
Contributor C: accuracy 80%
```

After sufficient history:

```
Contributor 241: average alpha +6%
Contributor 102: average alpha −2%
```

Weights feed weighted median and RAG ranking. **Who was right** matters more than **who was loud**.

## 6. Reproducibility

**Principle:** Any claim traces to a commit.

- Raw path: `data/DATE/TICKER/report.user.md`
- Prompt version: `prompt_hash`
- Sources: structured JSON with URLs
- Git SHA at merge time = permanent citation

Fork the repo → reproduce the entire ledger.

## 7. Open science posture

| Choice | Rationale |
|--------|-----------|
| MIT license | No lock-in |
| Public Git history | Inspect AAPL/NVDA sentiment evolution by year |
| Immutable raw layer | Wiki synthesizes; does not rewrite sources |
| CI in the open | Validation rules auditable in `.github/workflows/` |

## 8. Known limitations (honest)

- Not a prediction market (no skin in the game yet)
- Not real-time L2 data (narrative/sentiment focus)
- Verifier coverage scales with volunteer opt-in
- Embedding/RAG layers not production yet

See [VISION.md](VISION.md) for phase roadmap, [TRUST.md](TRUST.md) for governance.
