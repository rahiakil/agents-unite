<p align="center">
  <pre align="center">
   █████╗ ██████╗ ███████╗███╗   ██╗████████╗███████╗
  ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔════╝
  ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ███████╗
  ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ╚════██║
  ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ███████║
  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝
  ██╗   ██╗███╗   ██╗██╗████████╗███████╗
  ██║   ██║████╗  ██║██║╚══██╔══╝██╔════╝
  ██║   ██║██╔██╗ ██║██║   ██║   █████╗  
  ██║   ██║██║╚██╗██║██║   ██║   ██╔══╝  
  ╚██████╔╝██║ ╚████║██║   ██║   ███████╗
   ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝   ╚══════╝
  </pre>
</p>

<p align="center">
  <strong>A distributed, crowdsourced market intelligence ledger — built by agents, stored on Git, compounding forever.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT"></a>
  <a href=".github/workflows/validate-report.yml"><img src="https://img.shields.io/badge/CI-validate%20reports-success.svg" alt="CI"></a>
  <a href="tickers/universe.json"><img src="https://img.shields.io/badge/universe-291%20→%204000%2B-orange.svg" alt="Universe"></a>
  <a href="#roadmap"><img src="https://img.shields.io/badge/phase-1%20daily%20collection-yellow.svg" alt="Phase"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/contributors-welcome-brightgreen.svg" alt="Contributors"></a>
  <a href="#live-market-pulse"><img src="https://img.shields.io/badge/README-auto--updates%20on%20push-181717.svg?logo=github&logoColor=white" alt="Live README"></a>
</p>

<p align="center">
  <a href="#the-idea">The Idea</a> ·
  <a href="#live-market-pulse">Live Pulse</a> ·
  <a href="#join">Join</a> ·
  <a href="#documentation">Docs</a> ·
  <a href="#roadmap">Roadmap</a>
</p>

<br>

## The idea

Most AI systems **throw away their work**. agents-unite turns thousands of tiny, independent agent runs into a **persistent collective memory** — a longitudinal archive of what people (and their agents) believed about every ticker, every day, with sources attached.

Each participant spends a **small amount of their own LLM tokens**. Different agents, prompts, and tools contribute **independently**. Contributions land as **pull requests** and become **permanent history**. Over months and years, consensus emerges when many analyses reach similar conclusions — and future agents can reason over the full dataset.

> **The biggest moat is not the code. It's history.**

Imagine `NVDA/` with a folder for every trading day — thousands of analyses, sources, and sentiment scores. Eventually you know: what people believed, what actually happened, which contributors were consistently right, which prompts worked, which sources mattered. That becomes a **financial data flywheel**.

Future agents ask:

> *"Show me every bearish signal people identified before the last 20 earnings disappointments."*

That's the asset.

<br>

## What this is (and isn't)

agents-unite sits between ideas you already know — but rarely combined:

| | |
|---|---|
| **Wikipedia + Git** | Versioned, forkable public knowledge |
| **Open-source development** | PR review, CI, contributor trust |
| **Prediction markets** | Many independent views → aggregate signal |
| **Collective intelligence** | Small tasks, massive fan-out |
| **Longitudinal research** | Same tickers tracked across years |

Reddit, StockTwits, wikis, and scrapers exist. What's unusual here is **all of this together**:

1. **Git-based version history** — every belief is a commit  
2. **PR review workflow** — schema validation in the cloud, not on your honor  
3. **Agentic contributors** — Cursor, Claude, Gemini, local models, custom pipelines  
4. **User-owned token spend** — no central API bill  
5. **Multi-LLM diversity** — ensemble beats monoculture  
6. **Longitudinal memory** — years of `data/DATE/TICKER/`  
7. **Consensus from independent analysis** — not one editor's opinion  

<br>

## One ticker. One day. One PR.

People love **small missions**:

```
Today's assignment:  TSLA
Your cost:           ~25¢ of tokens
Your job:            Summarize what the market is saying
Your output:         One PR → data/2026-06-06/TSLA/
```

**4,000 contributors → 4,000 tickers covered daily.** No one burns tokens on the whole market alone. The README below **updates itself on every push** — live coverage, sentiment pulse, and leaderboard from real `data/`.

<!-- LIVE:HEADER_STATS:START -->
| Reports | Tickers | Universe | Latest day | Coverage | Avg sentiment |
|---------|---------|----------|------------|----------|---------------|
| **3** | **3** | **291** | **2026-06-05** | **1.0%** | **+0.393** |
<!-- LIVE:HEADER_STATS:END -->

<br>

## Agent diversity matters

Contributors bring different stacks:

- Claude · GPT · Gemini · DeepSeek · local models  
- LangGraph agents · custom scrapers · manual research  

Like ensemble models in ML, **diverse agents outperform a monoculture** when errors aren't perfectly correlated. The repo locks **prompt templates** (`agents/`) so diversity comes from models and sources — not from silently changing the rules.

<br>

## Where this goes

PRs are the ingestion layer. The full pipeline:

```mermaid
flowchart TB
    A[One ticker / day / contributor] --> B[Daily reports in data/]
    B --> C[Embeddings + search]
    C --> D[Knowledge graph wiki/]
    D --> E[Consensus engine]
    E --> F[LLM synthesis → research briefs]

    B --> G[Reputation + accuracy over time]
    G --> E
```

**Today:** daily reports, CI validation, live README, wiki scaffold.  
**Next:** semantic agreement, contributor accuracy, leaderboards, prediction tracking.

Technical breakdown: [docs/RAG_AND_SYNTHESIS.md](docs/RAG_AND_SYNTHESIS.md) · [docs/CONSENSUS.md](docs/CONSENSUS.md) · [docs/METHODS.md](docs/METHODS.md)

<br>

## Live market pulse

<!-- LIVE:MARKET_PULSE:START -->
**Latest pulse — 2026-06-05** · updated automatically on every push

| Ticker | Score | Mood |
|--------|-------|------|
| `NVDA` | +0.84 | 🟢 bullish |
| `AAPL` | +0.62 | 🟢 bullish |
| `TSLA` | -0.28 | 🔴 bearish |
<!-- LIVE:MARKET_PULSE:END -->

Full rollups: [`data/_index/`](data/_index/) · Examples: [`AAPL`](data/2026-06-05/AAPL/) · [`TSLA`](data/2026-06-05/TSLA/) · [`NVDA`](data/2026-06-05/NVDA/)

<br>

## Coverage tracker

<!-- LIVE:COVERAGE:START -->
**Universe progress** — 3 / 291 tickers ever covered

Today (2026-06-05): [█░░░░░░░░░░░░░░░░░░░░░░░] 1.0%
All-time:       [█░░░░░░░░░░░░░░░░░░░░░░░] 1.0%

| Date | Reports | Coverage | Avg sentiment |
|------|---------|----------|---------------|
| 2026-06-05 | 3 | 1.0% | +0.393 |
<!-- LIVE:COVERAGE:END -->

<br>

## Join

```bash
git clone https://github.com/rahiakil/agents-unite.git
cd agents-unite
./scripts/install-cron.sh          # config + optional cron

export AGENTS_UNITE_CONTRIBUTOR=your-github-username
./scripts/run-agent.sh             # assigns ticker, saves prompt
# → fill report in data/YYYY-MM-DD/TICKER/ with your agent
AGENT_DONE=1 ./scripts/daily-run.sh   # validate, commit, push, open PR
```

**Requirements:** Python 3.10+, any agent with web access, ~15 minutes. Your tokens, your machine, your PR.

Branch format: `report/2026-06-06-TSLA-a1b2c3d4` — date, ticker, and contributor hash baked into the name. CI rejects anything outside that ticker's folder.

Details: [docs/CONFIG.md](docs/CONFIG.md) · [CONTRIBUTING.md](CONTRIBUTING.md)

<br>

## Documentation

The README is the story. **`docs/`** is how it works — methods, timing, quality, consensus, RAG.

| Topic | Document | What you'll learn |
|-------|----------|-------------------|
| **Agent roles** | [docs/ROLES.md](docs/ROLES.md) | Research → verify → consensus pipeline |
| **Overview** | [docs/VISION.md](docs/VISION.md) | Goals, scale, phases |
| **Architecture** | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Assignment, layout, CI flow |
| **Timing** | [docs/TIMING.md](docs/TIMING.md) | UTC vs US close, cron, branch naming |
| **Data quality** | [docs/DATA_QUALITY.md](docs/DATA_QUALITY.md) | Uniqueness, CI guards, validation |
| **Consensus** | [docs/CONSENSUS.md](docs/CONSENSUS.md) | Multi-report merge, weighted median, Raft |
| **RAG & synthesis** | [docs/RAG_AND_SYNTHESIS.md](docs/RAG_AND_SYNTHESIS.md) | Embeddings, knowledge graph, semantic agreement |
| **Scientific methods** | [docs/METHODS.md](docs/METHODS.md) | Ensemble diversity, longitudinal eval, reproducibility |
| **Trust & governance** | [docs/TRUST.md](docs/TRUST.md) | Immutable prompts, reputation roadmap |
| **Local setup** | [docs/CONFIG.md](docs/CONFIG.md) | Cron, `gh auth`, tokens |
| **Index** | [docs/README.md](docs/README.md) | Full doc map |

**Wiki (compiled memory):** [WIKI.md](WIKI.md) · [wiki/index.md](wiki/index.md)

<br>

## Why contribute

| | |
|---|---|
| **Low cost** | One ticker, fixed schema, minutes of agent time |
| **Public history** | `AAPL/2025/` … `2026/` — evolving sentiment anyone can inspect |
| **Reputation (roadmap)** | Track record like Stack Overflow or ELO — *who was right*, not just who was loud |
| **Leaderboards (roadmap)** | Top contributors, best prompts, best agents |
| **Open data** | Fork the repo; build dashboards, indices, or strategies |

<br>

## Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| **1 — Daily collection** | One ticker/person/day; PR workflow; live README; CI guards | **Now** |
| **2 — Hourly + RAG** | Intraday shards; embeddings; wiki ingest at scale | Planned |
| **3 — Consensus** | Weighted median; semantic agreement; `consensus.md` batch | Planned |
| **4 — Reputation** | Accuracy scoring; prediction tracking; stake-gated signals | Planned |

Phase 4: contributors earn credibility from outcomes — **proof-of-trust for market sentiment**, not just vibes.

<br>

## Status

**Phase 1 — active development.** Assignment, validation, contributor CI, demo dataset, and live README are in place. Universe seeds at 291 tickers; community PRs expand toward 4,000+.

Not investment advice. Synthetic demo data in `data/2026-06-05/` is illustrative.

<br>

## License

MIT — see [LICENSE](LICENSE).

<!-- LIVE:FOOTER_STAMP:START -->
_Live sections last regenerated: **2026-06-06 15:32 UTC** · [`scripts/generate_readme.py`](scripts/generate_readme.py)_
<!-- LIVE:FOOTER_STAMP:END -->

<br>

<p align="center">
  <strong>Models change. Historical reasoning accumulates forever.</strong>
</p>

<p align="center">
  <sub>One agent · one ticker · one commit · repeat — until the market has a memory.</sub>
</p>
