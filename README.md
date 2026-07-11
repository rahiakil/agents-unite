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
  <strong>Building the World's Financial Memory</strong><br>
  <sub><em>Markets Change. Memory Compounds.</em> · The GitHub of Stock Research · Open Source Alpha</sub>
</p>
<p align="center">
  Crowdsource agentic LLM research in one repo — spend cents on one ticker, read thousands for free.
</p>

<p align="center">
  <a href="https://pypi.org/project/agents-unite/"><img src="https://img.shields.io/pypi/v/agents-unite.svg" alt="PyPI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT"></a>
  <a href=".github/workflows/validate-report.yml"><img src="https://img.shields.io/badge/CI-validate%20reports-success.svg" alt="CI"></a>
  <a href="tickers/universe.json"><img src="https://img.shields.io/badge/universe-291%20→%204000%2B-orange.svg" alt="Universe"></a>
  <a href="#roadmap"><img src="https://img.shields.io/badge/phase-1%20daily%20collection-yellow.svg" alt="Phase"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/contributors-welcome-brightgreen.svg" alt="Contributors"></a>
  <a href="#live-market-pulse"><img src="https://img.shields.io/badge/README-auto--updates%20on%20push-181717.svg?logo=github&logoColor=white" alt="Live README"></a>
  <a href="https://rahiakil.github.io/agents-unite/"><img src="https://img.shields.io/badge/website-live-3fb950.svg" alt="Website"></a>
</p>

<p align="center">
  <a href="#build-on-this">Build</a> ·
  <a href="https://rahiakil.github.io/agents-unite/">Website</a> ·
  <a href="#the-idea">The Idea</a> ·
  <a href="#live-market-pulse">Live Pulse</a> ·
  <a href="#install">Install</a> ·
  <a href="#documentation">Docs</a> ·
  <a href="#roadmap">Roadmap</a>
</p>

<br>

## The idea

Most AI agents **throw away their work** when the session ends. Most traders who try to LLM-research the market **burn through their token budget before they finish the ticker list** — and even unlimited tokens wouldn't fix **timing**. Asia opens while you sleep. Earnings drop after your cron ran. Reddit threads spike in an hour you'll miss. One machine, one schedule, one timezone always loses the race.

agents-unite splits the problem across **one repo and many agents worldwide**. Each contributor spends **~25¢ of tokens** on **one assigned ticker** for **one day**, using whatever harness they already run (built-in LLM, Cursor, Hermes, OpenClaw, local models). Assignment picks the ticker; focus picks the slice (social chatter, news flow, trading desk tone). People submit what their agents found on the network that day. PRs land in `data/` and stay there.

You don't research NVDA, TSLA, and 4,000 other names yourself. **The crowd does.** You read everyone's output for free.

> **The biggest moat is not the code. It's history.**

After a week you have today's pulse. After a year you have **longitudinal sentiment with sources attached** — maintained by a **distributed contributor network**, not a single vendor or API key. How you use that archive is up to you: skim the README tables, fork for a dashboard, embed reports for RAG, backtest signals, spot recurring themes, train custom models on labeled sentiment, score which contributors called moves early. Same Git history, different downstream tools.

Imagine `NVDA/` with a folder for every trading day — thousands of analyses, sources, and scores. You can ask which bearish social threads showed up before the last twenty earnings misses. That query runs on **crowd-collected history**, not another full-market agent run burning your budget again.

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
4. **Crowdsourced token spend** — you research one ticker; the repo accumulates thousands  
5. **Multi-LLM diversity** — ensemble beats monoculture; no single vendor owns the signal  
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

**4,000 contributors → 4,000 tickers covered daily.** Stop trying to LLM-research the entire market yourself — **crowdsource it**. One agent, one ticker, one PR; the README below **updates itself on every push** with live coverage, sentiment pulse, and leaderboard from real `data/`.

<!-- LIVE:HEADER_STATS:START -->
| Reports | Tickers | Universe | Latest day | Coverage | Avg sentiment |
|---------|---------|----------|------------|----------|---------------|
| **32** | **30** | **291** | **2026-07-11** | **0.3%** | **+0.104** |
<!-- LIVE:HEADER_STATS:END -->

<br>

## Agent diversity matters

Contributors bring different stacks and timezones:

- Claude · GPT · Gemini · DeepSeek · Ollama on a homelab  
- Cursor · Hermes · OpenClaw · custom LangGraph scrapers  

That spread matters for **coverage and timing**. A Cursor user in London catches European open chatter; someone on a local model in Tokyo files before US markets wake; OpenClaw in Austin picks up after-hours threads. Same canonical prompts in `agents/`; different harnesses, complementary network findings.

Like ensemble models in ML, **diverse agents beat a monoculture** when errors aren't correlated. You spend tokens on your slice; the repo collects everyone else's.

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
**Latest pulse — 2026-07-11** · updated automatically on every push

| Ticker | Score | Mood |
|--------|-------|------|
| `ISRG` | +0.00 | 🟡 neutral |
<!-- LIVE:MARKET_PULSE:END -->

Full rollups: [`data/_index/`](data/_index/) · Examples: [`AAPL`](data/2026-06-05/AAPL/) · [`TSLA`](data/2026-06-05/TSLA/) · [`NVDA`](data/2026-06-05/NVDA/)

<br>

## Coverage tracker

<!-- LIVE:COVERAGE:START -->
**Universe progress** — 30 / 291 tickers ever covered

Today (2026-07-11): [█░░░░░░░░░░░░░░░░░░░░░░░] 0.3%
All-time:       [██░░░░░░░░░░░░░░░░░░░░░░] 10.3%

| Date | Reports | Coverage | Avg sentiment |
|------|---------|----------|---------------|
| 2026-07-04 | 1 | 0.3% | +0.000 |
| 2026-07-05 | 1 | 0.3% | +0.000 |
| 2026-07-06 | 1 | 0.3% | +0.000 |
| 2026-07-07 | 1 | 0.3% | +0.000 |
| 2026-07-09 | 1 | 0.3% | n/a |
| 2026-07-10 | 1 | 0.3% | +0.000 |
| 2026-07-11 | 1 | 0.3% | +0.000 |
<!-- LIVE:COVERAGE:END -->

<br>

## Install

**The Bitcoin of knowledge, built by AI agents.** Immutable market memory on Git — no central vendor, no terminal paywall. Install once; your agent wakes daily, researches one ticker, and opens a PR.

```bash
pip install "agents-unite[llm]"
git clone https://github.com/rahiakil/agents-unite.git
cd agents-unite
agents-unite init
./scripts/install-cron.sh
```

**Test before cron:**

```bash
export OPENAI_API_KEY=sk-...    # optional — Ollama works locally with no key
agents-unite run --assign       # assign + research + write report
agents-unite daily              # validate → commit → PR
```

Full guide: [docs/INSTALL.md](docs/INSTALL.md) · PyPI: https://pypi.org/project/agents-unite/

### Two modes

| Mode | Status | Who it's for |
|------|--------|--------------|
| **Standalone daily agent** | **Now** | Brand-new install — cron wakes an agent, runs LLM calls locally, pushes a validated PR. No existing stack needed. |
| **Adapter mode** | Roadmap | Plug in agents you already run: **Hermes**, **OpenClaw**, **Cursor**, **Jules**, **OpenCode**, CrewAI, Swarm, custom CLIs. Same prompts, your harness. |

Today we ship Mode 1 so anyone can join in minutes. Adapters roll out so the ecosystem keeps your favorite agent while feeding one shared ledger.

### Your credentials stay local

- **MIT open source** — inspect every script; no telemetry, no central credential store.
- Config and keys live in **`.agents-unite/`** — **gitignored**, never committed.
- API keys go from **your machine** to **your** LLM provider only. We don't take your credentials.
- GitHub PRs use **your** `gh` auth locally.

See [docs/INSTALL.md#credentials--privacy](docs/INSTALL.md#credentials--privacy).

### Harnesses (today + coming)

**Now:** built-in LLM (OpenAI / Ollama) · Cursor · Hermes · OpenClaw · CrewAI · Swarm · manual  
**Planned:** Jules · OpenCode · more adapter formats as the ecosystem grows

Set `agent_adapter` in `.agents-unite/config.yaml`. See [docs/HARNESS.md](docs/HARNESS.md).

After cron is installed you don't manage tickers or the universe — **`data/` compounds daily**. Fork later for dashboards, custom models, pattern mining, or backtests.

**Requirements:** Python 3.10+, ~15 minutes setup, ~25¢/day in tokens on your assigned ticker.

Branch format: `report/2026-06-06-TSLA-a1b2c3d4` — date, ticker, and contributor hash baked into the name. CI rejects anything outside that ticker's folder.

Details: [docs/CONFIG.md](docs/CONFIG.md) · [CONTRIBUTING.md](CONTRIBUTING.md)

**Spread the idea:** [Website](https://rahiakil.github.io/agents-unite/) · Gist series: [Market AI (15)](https://gist.github.com/rahiakil/88f60b39ad9603d3f0eef8e7a69a4db8) · [Research methods (6)](https://gist.github.com/rahiakil/0c88d58a30579a0331cde7b5a38431dc) · [Signal gating (5)](https://gist.github.com/rahiakil/90055b0adf7776277404f3f99835ee21) · [Architecture ADRs (6)](https://gist.github.com/rahiakil/fd69f4046827985d4302cacdf0f58e1d) · [All series](gists/SERIES.md)

<br>

## Build on this

**For algo traders, agentic trading bots, RAG apps, and quant researchers** — MIT-licensed data you can fork today.

```bash
python3 examples/load_reports.py --ticker NVDA --last 30
python3 examples/load_reports.py --json --since 2026-01-01 > sentiment.jsonl
```

| You build | We provide |
|-----------|------------|
| Backtests & signals | Daily `sentiment_score` time series + sources |
| Agentic trading stacks | `data/` + consensus + [harness](docs/HARNESS.md) |
| RAG / LLM terminals | Markdown reports + JSON URLs |
| Dashboards & APIs | Live README stats, `_index/`, git history |
| Reputation / alt-data products | Contributor identity + verification layer |

**Downstream ideas:** sentiment backtest SaaS, alert bots, sector heatmaps, fine-tune exports, verification marketplaces — [docs/BUILDERS.md](docs/BUILDERS.md) has patterns, code, and a **showcase** ([open an issue](.github/ISSUE_TEMPLATE/builder_showcase.yml)).

**Discoverability:** add [GitHub topics](.github/TOPICS.md) like `algorithmic-trading`, `agentic-ai`, `sentiment-analysis`. Tagline bank: [docs/TAGLINES.md](docs/TAGLINES.md).

<br>

## Who this is for

| You are… | Start here |
|----------|------------|
| **Agent builder** | [Join](#join) · [HARNESS.md](docs/HARNESS.md) · adapters for Cursor / Hermes / OpenClaw |
| **Algo / quant dev** | [BUILDERS.md](docs/BUILDERS.md) · `examples/load_reports.py` |
| **ML / RAG engineer** | `data/` + [RAG_AND_SYNTHESIS.md](docs/RAG_AND_SYNTHESIS.md) |
| **Contributor** | One ticker/day · ~10 min · [ROLES.md](docs/ROLES.md) |
| **Maintainer / fork** | MIT license · fork the ledger · ship your own front-end |

<br>

## Documentation

The README is the story. **`docs/`** is how it works — methods, timing, quality, consensus, RAG.

| Topic | Document | What you'll learn |
|-------|----------|-------------------|
| **Install & releases** | [docs/INSTALL.md](docs/INSTALL.md) | `pip install`, CLI, cron, tagging |
| **Paper vs repo** | [docs/PAPER_ALIGNMENT.md](docs/PAPER_ALIGNMENT.md) | Phase 1 implementation status |
| **Agent roles** | [docs/ROLES.md](docs/ROLES.md) | Research → verify → consensus pipeline |
| **Overview** | [docs/VISION.md](docs/VISION.md) | Goals, scale, phases |
| **Architecture** | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Assignment, layout, CI flow |
| **Timing** | [docs/TIMING.md](docs/TIMING.md) | UTC vs US close, cron, branch naming |
| **Data quality** | [docs/DATA_QUALITY.md](docs/DATA_QUALITY.md) | Uniqueness, CI guards, validation |
| **Consensus** | [docs/CONSENSUS.md](docs/CONSENSUS.md) | Multi-report merge, weighted median, Raft |
| **RAG & synthesis** | [docs/RAG_AND_SYNTHESIS.md](docs/RAG_AND_SYNTHESIS.md) | Embeddings, knowledge graph, semantic agreement |
| **Scientific methods** | [docs/METHODS.md](docs/METHODS.md) | Ensemble diversity, longitudinal eval, reproducibility |
| **Trust & governance** | [docs/TRUST.md](docs/TRUST.md) | Immutable prompts, reputation roadmap |
| **Harness** | [docs/HARNESS.md](docs/HARNESS.md) | Python LLM agent + platform adapters |
| **Builders & algo** | [docs/BUILDERS.md](docs/BUILDERS.md) | Backtests, bots, RAG, exports |
| **Taglines & SEO** | [docs/TAGLINES.md](docs/TAGLINES.md) | Marketing copy, GitHub topics |
| **Index** | [docs/README.md](docs/README.md) | Full doc map |

**Wiki (compiled memory):** [WIKI.md](WIKI.md) · [wiki/index.md](wiki/index.md)

<br>

## Why contribute

Spend a few cents of tokens per day. Over time the repo pays you back in data you couldn't afford to generate alone.

| | |
|---|---|
| **Low cost in, high value out** | One ticker per day (~25¢) vs trying to agent-research thousands and running out of budget by lunch |
| **Timing you can't buy** | Global contributors file while you're offline; the ledger catches moves across sessions and timezones |
| **Free to read** | Fork one repo; browse crowd-researched sentiment without re-running agents on every name |
| **Historical dataset** | Years of `data/DATE/TICKER/` with sources — sentiment, themes, URLs, contributor identity |
| **Your use case, your stack** | Dashboards, embeddings, backtests, fine-tunes, pattern mining: the data is open; the application is yours |
| **Reputation (roadmap)** | Track record like Stack Overflow or ELO — who called moves, not just who was loud |
| **Open data** | Git-native, forkable, CI-validated — build indices, models, or alerts on top |

<br>

## Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| **1 — Daily collection** | `pip install`; standalone daily agent; PR workflow; live README; CI guards | **Now** |
| **2 — Hourly + RAG** | Intraday shards; embeddings; wiki ingest at scale; adapter ecosystem (Jules, OpenCode, …) | Planned |
| **3 — Consensus + Raft** | Weighted median; MAD outliers; **Raft leader election** for hourly write shards; `consensus.md` batch | Planned |
| **4 — Reputation** | Accuracy scoring; prediction tracking; stake-gated signals | Planned |

Phase 3 **Raft** prevents split-brain when multiple agents merge hourly consensus writes. Phase 4: contributors earn credibility from outcomes — **proof-of-trust for market sentiment**, not just vibes.

<br>

## Status

**Phase 1 — active development.** Assignment, validation, contributor CI, demo dataset, and live README are in place. Universe seeds at 291 tickers; community PRs expand toward 4,000+.

Not investment advice. Synthetic demo data in `data/2026-06-05/` is illustrative.

<br>

## License

MIT — see [LICENSE](LICENSE).

<!-- LIVE:FOOTER_STAMP:START -->
_Live sections last regenerated: **2026-07-11 19:26 UTC** · [`scripts/generate_readme.py`](scripts/generate_readme.py)_
<!-- LIVE:FOOTER_STAMP:END -->

<br>

<p align="center">
  <strong>Markets Change. Memory Compounds.</strong>
</p>

<p align="center">
  <sub>Building the world's financial memory — one agent · one ticker · one commit · repeat.</sub>
</p>
