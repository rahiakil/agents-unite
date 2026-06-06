# THINKING — Agents Unite product vision

> **Living document.** Last updated: 2026-06-06  
> **Status:** Draft for back-and-forth — nothing here is shipped yet.

---

## One-sentence pitch

A **GitHub-native, crowd-sourced market sentiment ledger**: thousands of people run one cron job; each day one agent wakes up, researches one assigned ticker, opens a PR; verifiers reconcile conflicts; traders get auditable historical trends without burning personal token budgets.

---

## The problem (why this exists)

| Pain | Today | With agents-unite |
|------|-------|-------------------|
| Coverage | ~4,000 US tickers; no individual can research all daily | Work split across N contributors |
| Token cost | One mega-agent scanning everything = $$$ | Each person: **1 ticker ≈ 15 min / low tokens** |
| Data lock-in | Terminals, scrapers, opaque feeds | Open git history, forkable |
| Historical narrative | Scattered bookmarks, no structure | Dated folders, sources.json, wiki index |

**Core insight:** Markets move on narrative before numbers. Narrative is scattered across Reddit, X, news, earnings calls. Nobody has the energy to collect it all alone — but **20,000 people each doing one ticker** could.

---

## The happy path (user story)

1. Trader/developer clones repo once.
2. Runs `./scripts/install-cron.sh` (future) — sets contributor ID, agent backend (Cursor CLI / Claude / local LLM), GitHub token for PRs.
3. **Never touches it again** (ideally).
4. Every day at e.g. 06:00 local (or UTC — TBD):
   - Assignment picks ticker (e.g. NVDA for this machine today).
   - Local agent searches Reddit, X, news, earnings, projections.
   - Writes `data/YYYY-MM-DD/NVDA/report.md` + `sources.json`.
   - Script creates branch `report/2026-06-06-NVDA`, opens PR.
5. CI validates schema; README live stats refresh.
6. **Second brain** (LLM wiki) ingests canonical layer → "what are the trends this week?"

---

## Scale math (sanity check)

| Assumption | Number |
|------------|--------|
| Registered contributors | 20,000 |
| Actually online daily | ~15% → 3,000 |
| Tickers in universe | ~4,000 |
| Reports per day (if 1:1 assignment) | ~3,000 |
| **Coverage** | **~75% of universe per day** |

Even at 5% participation (1,000/day), you still cover **25%** — better than any solo researcher.

**Open question:** Is "random" the right assignment model, or should we **bias toward uncovered tickers** so MSFT doesn't get 10 reports while obscure small-caps get zero?

---

## Folder layout (evolving)

```
data/
  2026-06-06/                    # GMT date (TBD: confirm UTC vs America/New_York)
    NVDA/
      report.<hash>.md           # v2: multi-contributor per ticker
      sources.<hash>.json
      consensus.md               # verifier output — canonical view
    MSFT/
      ...
  _index/
    summary-2026-06-06.md        # auto rollup (exists today)
  canonical/                     # future: merged truth layer for wiki
    2026-06-06/
      NVDA.md
```

**Karpathy LLM wiki** would likely index `canonical/` or `_index/` + consensus files — not raw conflicting PRs.

---

## The MSFT collision problem

> *"If 10 people had MSFT today and submit different PRs — how do you merge? GitHub CI/CD cannot."*

This is the **central design tension**. Options:

### Option A — Prevent collisions (v1 today)

- Deterministic assignment: `SHA256(date:contributor) % N` → same person always gets same ticker on same day; **different people → different tickers** (with high probability when N ≫ contributors).
- **Pro:** No merge conflict by design; simple.
- **Con:** Doesn't guarantee full coverage; luck of hash; doesn't give redundancy for trust.

### Option B — Allow collisions, suffix files (v2)

- Path: `data/DATE/TICKER/report.<contributor_hash>.md`
- No overwrite; all reports kept.
- Nightly **verifier job** writes `consensus.md`.
- **Pro:** Redundancy; detect outliers; proof-of-stake weights make sense.
- **Con:** More storage; wiki must read consensus not raw.

### Option C — Slot reservation (blockchain-ish)

- Each `(date, ticker)` has K slots (e.g. K=3).
- First 3 PRs win; 4th gets CI rejection or reassignment.
- **Pro:** Bounded redundancy.
- **Con:** Race conditions; needs coordinator or on-chain-style ordering (heavy).

### Option D — Verifier merges content (not git merge)

- GitHub never auto-merges conflicting markdown.
- Verifier agent reads all `report.*.md`, produces **one** `consensus.md` + optional `canonical/NVDA.md`.
- Raw reports stay as audit trail (like Ethereum blocks).
- **Pro:** Fits "CI can't merge semantics" reality.
- **Con:** Needs verifier incentives and quality control.

**Leaning for discussion:** **B + D** — allow multiple submissions, verifiers produce canonical layer. Assignment can still spread load, but collisions become a **feature** (redundancy) not a bug.

---

## Verifier network (proof-of-stake sketch)

Inspired by Ethereum, but **git-native and lightweight**:

| Role | Does | Gets |
|------|------|------|
| **Submitter** | Runs cron, opens PR with report | Reputation +1 on merge; future strategy access |
| **Verifier** | Runs consensus agent on tickers with ≥2 reports | Reputation +2; higher weight in disputes |
| **Observer** | Read-only; builds wiki / dashboards | Nothing (free rider OK) |

### Verifier workflow (proposed)

1. Config: `AGENTS_UNITE_ROLE=verifier` in `.agents-unite/config.yaml`
2. Cron (different schedule): pick tickers where `count(reports) >= 2` and no `consensus.md` yet
3. Run `agents/consensus.md` prompt → output `consensus.md`
4. Open PR: `consensus: NVDA 2026-06-06`
5. Other verifiers (future) review PR — 2-of-3 merge? Or trust first verifier until reputation slashing exists?

### Catching manipulation

| Attack | Detection idea |
|--------|----------------|
| Fake URLs | CI fetch HEAD request; 404 → flag |
| Hallucinated numbers | Verifier cross-checks against 2+ independent reports; large deviation → `confidence: low` |
| Sybil (100 fake contributors) | Rate limit per GitHub account; eventually stake/reputation; outlier MAD rejection |
| Coordinated pump | Many bullish reports with thin sources → verifier downweights; spread in consensus metadata |

**Open question:** Do verifiers need **stake** (skin in the game) before v3, or is "anyone with the repo" enough at small scale?

---

## Automation stack (not built yet)

```
cron (daily)
  └─ scripts/daily-run.sh
       ├─ assign_ticker.py
       ├─ run agent (Cursor CLI / claude / codex / local)
       ├─ validate_report.py
       ├─ git branch + commit
       └─ gh pr create
```

**Skill/cron installer** (future): one command adds crontab entry + checks deps + writes config template.

**Config file** (`.agents-unite/config.yaml`):

```yaml
contributor_id: you@example.com
role: submitter          # submitter | verifier | both
agent: cursor            # cursor | claude | codex | openai
schedule: "0 6 * * *"      # cron
timezone: UTC
github:
  token_env: GH_TOKEN    # never commit token
auto_pr: true
```

---

## Relationship to current repo (what exists vs vision)

| Vision piece | Status today |
|--------------|--------------|
| Deterministic ticker assignment | ✅ `assign_ticker.py` |
| Report schema + validation | ✅ |
| Agent prompt template | ✅ |
| Live README on push | ✅ |
| Demo data (AAPL/TSLA/NVDA) | ✅ |
| Cron / one-command install | ❌ not built |
| Auto branch + PR | ❌ not built |
| Multi-report per ticker | ❌ single path only |
| Verifier role + consensus automation | ❌ docs only |
| `canonical/` wiki layer | ❌ |
| LLM wiki integration | ❌ |
| Reputation / stake | ❌ docs only |

---

## LLM wiki as second brain

**Karpathy-style wiki** = indexed corpus agents can query: "What was sentiment on NVDA last week?" "Which tickers flipped bearish?"

Suggested pipeline:

```
data/*/TICKER/report.*.md  ──┐
                               ├──► consensus.md ──► canonical/ ──► wiki index
data/_index/summary-*.md  ────┘
```

Wiki should **not** ingest 10 conflicting MSFT drafts directly — it ingests **consensus + index summaries**.

**Open question:** Host wiki in-repo (`wiki/`) or external tool pointing at this repo?

---

## Discussion prompts (for back-and-forth)

Please react to these — your answers go into `DECISIONS.md`:

1. **GMT vs market timezone** for folder dates — UTC midnight? US market close (21:00 UTC)?

2. **Collision policy** — Prefer A (prevent), B (allow + consensus), or C (K slots)?

3. **Unattended PRs** — Auto-merge if CI passes and single report? Or always human/verifier review?

4. **Verifier bootstrapping** — At 50 users, do we need verifiers yet, or only at scale?

5. **Agent runtime** — Assume Cursor CLI, or support headless Claude API / local Ollama equally?

6. **Token budget** — Hard cap (e.g. max 5 web searches) in agent prompt, or trust contributors?

7. **Reputation** — GitHub username based, or pseudonymous contributor_hash only?

8. **Bad data** — Slash reputation, revert PR, or flag in consensus metadata only?

---

## Rough phase map (aligned with README)

| Phase | Name | Deliverable |
|-------|------|-------------|
| 1 | **Collect** | Cron + auto-PR + submitter role (current repo + automation) |
| 2 | **Hourly** | Intraday shards for volatile names |
| 3 | **Verify** | Verifier role, multi-report paths, `consensus.md` automation |
| 4 | **Stake** | Reputation gates, trading strategy access, dispute resolution |
| 5 | **Wiki** | Canonical layer + LLM wiki second brain |

---

## Raw notes / stream of consciousness

- "Almost like a blockchain" — git commits **are** the chain; PRs are pending txs; consensus is finality.
- Verifiers ≈ validators; submitters ≈ proposers; `_index/` ≈ block explorer summary.
- Don't need Ethereum literally — need **auditability + incentives + conflict resolution**.
- 20k users × 1 ticker × low tokens each >> 1 user × 4000 tickers × bankruptcy.
- Manipulation is inevitable at scale; design for **detect + downweight**, not **prevent perfectly**.
- The product wins if **install is trivial** — `curl | bash` or `make install-cron` and forget.

---

## Next steps (after we align)

1. Lock decisions in `raw/DECISIONS.md`
2. Promote stable sections to `docs/VISION.md` and update `docs/CONSENSUS.md`
3. Implement Phase 1 automation: `scripts/daily-run.sh` + cron installer
4. Implement v2 paths: `report.<hash>.md` when collision detected
5. Verifier cron + consensus PR flow
6. **LLM Wiki** — implemented: see [`WIKI.md`](../WIKI.md), [`wiki/`](../wiki/), `scripts/wiki_ingest.py`

---

*This file is intentionally messy. Argue with it.*
