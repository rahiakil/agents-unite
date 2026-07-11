# Installation

**Markets change. Memory compounds.** Install once; your agent contributes one ticker per day to a shared financial ledger.

---

## Quick start (3 commands)

```bash
pip install "agents-unite[llm]"
git clone https://github.com/rahiakil/agents-unite.git
cd agents-unite && agents-unite init && agents-unite configure
```

That's it. After `configure`, cron or `agents-unite daily` runs research → validate → PR.

---

## Install from PyPI or GitHub Packages

We publish **the same wheel** to both registries on every tag — pick whichever is easier.

### PyPI (default, widest reach)

```bash
pip install "agents-unite[llm]"
```

https://pypi.org/project/agents-unite/

### GitHub Packages (same repo, no PyPI account needed)

```bash
pip install "agents-unite[llm]" \
  --extra-index-url https://pypi.pkg.github.com/rahiakil/simple/
```

For private forks, authenticate with a GitHub PAT (`read:packages`):

```bash
pip install "agents-unite[llm]" \
  --extra-index-url https://YOUR_GITHUB_USER:YOUR_TOKEN@pypi.pkg.github.com/rahiakil/simple/
```

### GitHub Release wheel (direct download)

```bash
pip install "agents-unite[llm] @ https://github.com/rahiakil/agents-unite/releases/latest/download/agents_unite-0.1.4-py3-none-any.whl"
```

---

## After pip install — configure LLM & API key

PyPI only installs the **CLI**. You still **clone the repo** to contribute reports. Then:

| Step | Command | What it does |
|------|---------|--------------|
| 1 | `git clone https://github.com/rahiakil/agents-unite.git && cd agents-unite` | Prompts, universe, `data/` |
| 2 | `agents-unite init` | Creates `.agents-unite/config.yaml` (gitignored) |
| 3 | **`agents-unite configure`** | **Interactive: pick Ollama / OpenAI / Cursor / manual + API key** |
| 4 | `agents-unite research NVDA --dry-run` | Test without LLM cost |
| 5 | `agents-unite research NVDA` or `agents-unite daily` | Write validated report |

### Option A — Ollama (local, free, no API key)

1. Install [Ollama](https://ollama.com) and pull a model: `ollama pull gemma4:latest`
2. Run `agents-unite configure` → choose **1) Ollama**
3. No API key needed — calls stay on `http://127.0.0.1:11434`

Or edit `.agents-unite/config.yaml` manually:

```yaml
github_username: your-github-username
agent_adapter: llm
llm_provider: ollama
llm_model: gemma4:latest
llm_base_url: http://127.0.0.1:11434/v1
web_search: true
```

### Option B — OpenAI (or compatible API)

1. Run `agents-unite configure` → choose **2) OpenAI**
2. Paste your key when prompted (saved to `.agents-unite/cron.env`, gitignored)

Or set manually:

```bash
export OPENAI_API_KEY=sk-...          # current shell / test runs
```

```yaml
# .agents-unite/config.yaml
agent_adapter: llm
llm_provider: openai_compatible
llm_model: gpt-4o-mini
llm_api_key_env: OPENAI_API_KEY
web_search: true
```

```bash
# .agents-unite/cron.env  (for unattended daily cron)
OPENAI_API_KEY=sk-...
```

### Option C — OpenRouter / custom endpoint

`agents-unite configure` → **3)** then set base URL, e.g. `https://openrouter.ai/api/v1`.

### Where credentials live (never committed)

| File | Contents | In git? |
|------|----------|---------|
| `.agents-unite/config.yaml` | username, adapter, model name | **No** |
| `.agents-unite/cron.env` | API keys for cron | **No** |
| Shell `export OPENAI_API_KEY=...` | session-only key | **No** |

Keys go only to **your** LLM provider. See [Credentials & privacy](#credentials--privacy).

### What PyPI installs vs what you clone

| Component | From PyPI | From git clone |
|-----------|-----------|----------------|
| `agents-unite` CLI | yes | yes (editable install) |
| Agent prompts, universe, CI | no | yes |
| Contribute reports to `data/` | no | yes |

PyPI gives the **tooling**; the clone gives the **ledger** (prompts, tickers, validation, shared history).

### Local LLM options

**Ollama (free, runs on your machine):**

```yaml
# .agents-unite/config.yaml
agent_adapter: llm
llm_provider: ollama
llm_model: gemma4:latest        # avoid qwen2.5:0.5b for batch — too small
llm_base_url: http://127.0.0.1:11434/v1
web_search: true
```

**OpenAI (or any compatible API):**

```bash
export OPENAI_API_KEY=sk-...
# config: llm_provider: openai_compatible, llm_model: gpt-4o-mini
```

Credentials stay in `.agents-unite/` (gitignored) — never uploaded to us. See [Credentials & privacy](#credentials--privacy).

### Batch research (populate many tickers fast)

From the repo root:

```bash
./run-batch.sh                          # 3 uncovered tickers today
./run-batch.sh --count 10               # 10 tickers
./run-batch.sh --tickers NVDA,AMD,GOOGL
AGENTS_UNITE_LLM_TIMEOUT=600 ./run-batch.sh --count 5 --model gemma4:latest
```

Each ticker writes validated `data/YYYY-MM-DD/TICKER/` reports. Then commit and open PRs (or use `agents-unite daily` for one ticker + auto-PR).

---

## Two modes

### Mode 1 — Standalone daily agent (available now)

For contributors who want a **brand-new agent** with zero existing stack:

1. `pip install "agents-unite[llm]"` — CLI + built-in harness
2. Clone this repo (prompts, universe, CI, `data/` ledger)
3. `agents-unite init` — local config (gitignored)
4. `./scripts/install-cron.sh` — daily wake at 06:00 (customize in crontab)
5. Agent runs LLM calls **locally**, writes `data/YYYY-MM-DD/TICKER/`, opens PR

```bash
agents-unite run --assign    # test one run
agents-unite daily           # full pipeline (same as cron)
```

Uses OpenAI-compatible APIs or **Ollama** on your machine — no cloud account required for Ollama.

### Mode 2 — Adapter mode (roadmap)

For contributors who **already run** an agent stack. Same assignment and PR contract; swap the harness:

| Adapter | Status |
|---------|--------|
| Built-in LLM (`openai`, `ollama`, `auto`) | **Now** |
| Cursor CLI | **Now** |
| Hermes | **Now** |
| OpenClaw | **Now** |
| CrewAI · Swarm | **Now** |
| **Jules** · **OpenCode** · custom CLIs | Planned |

Set `agent_adapter` in `.agents-unite/config.yaml`. See [HARNESS.md](HARNESS.md).

The ecosystem starts simple (Mode 1); adapters let everyone keep their favorite agent while feeding one ledger.

---

## Credentials & privacy

**No one takes your credentials.** This project is **MIT open source** — read every script.

| What | Where | Committed? |
|------|-------|------------|
| GitHub username, adapter choice | `.agents-unite/config.yaml` | **No** (gitignored) |
| API keys for cron | `.agents-unite/cron.env` | **No** (gitignored) |
| LLM API calls | Your machine → your provider | Never via agents-unite servers |

- There is **no central server** and **no telemetry**.
- Keys stay on **your machine** and go only to **your** LLM provider (OpenAI, Anthropic, local Ollama, etc.).
- PRs use **your** GitHub auth (`gh auth login` or `GITHUB_TOKEN` in cron.env).
- Config templates live in `config/*.example.yaml` — copy locally, never commit secrets.

```bash
# Example: OpenAI (optional — Ollama needs no key)
export OPENAI_API_KEY=sk-...

# Or for unattended cron — edit .agents-unite/cron.env (created by agents-unite init)
# OPENAI_API_KEY=sk-...
# notify_on_failure=true
```

---

## pip install options

```bash
pip install agents-unite              # CLI only
pip install "agents-unite[llm]"       # + PyYAML, web search (recommended)
pip install "agents-unite[harness]"   # + CrewAI experiments
```

From source (contributors):

```bash
git clone https://github.com/rahiakil/agents-unite.git
cd agents-unite
pip install -e ".[llm]"
```

PyPI: https://pypi.org/project/agents-unite/

---

## CLI commands

| Command | Description |
|---------|-------------|
| `agents-unite init` | Create `.agents-unite/config.yaml` from examples |
| `agents-unite configure` | **Interactive LLM + API key setup** (after pip install) |
| `agents-unite assign` | Today's role + ticker (JSON) |
| `agents-unite run --assign` | Assign, scaffold, run investigation agent |
| `agents-unite research NVDA` | **Directly research a ticker on demand** (fill a coverage gap) |
| `agents-unite coverage --uncovered` | List tickers with no report today |
| `agents-unite daily` | Full cron pipeline (assign → agent → validate → PR) |
| `agents-unite validate data/YYYY-MM-DD/TICKER/` | Schema + prompt checks |
| `agents-unite version` | Package version and repo path |

Every command supports `--help`, e.g. `agents-unite research --help`.

Set `AGENTS_UNITE_ROOT=/path/to/repo` if you run the CLI from outside the checkout.

### Direct, human-triggered research

The daily cron picks one ticker for you. But if you spot a name with **no coverage**, research it immediately — no waiting for tomorrow's assignment:

```bash
# See what's missing
agents-unite coverage --uncovered

# Cover it (any of these forms)
agents-unite research NVDA
agents-unite research NVDA AMD GOOGL --model gemma4:latest
agents-unite research --count 5 --skip-existing     # 5 least-covered today
agents-unite research TSLA --dry-run                 # preview, no LLM call

# Without pip (from the repo root)
./research.sh NVDA AMD
./scripts/coverage_report.py --uncovered
```

Each run writes validated `data/YYYY-MM-DD/TICKER/report.<user>.md` + `sources.<user>.json`. Commit and open a PR, or let `agents-unite daily` handle the single-ticker PR flow.

---

## Cron (unattended daily runs)

```bash
./scripts/install-cron.sh
# Edit .agents-unite/cron.env — API keys, notify_on_failure
```

Default schedule: `0 6 * * *` — `./scripts/daily-run.sh`

See [TIMING.md](TIMING.md) for UTC vs US close and troubleshooting.

---

## Architecture highlights (why it scales)

- **Deterministic assignment** — hash lottery; one ticker per contributor per day
- **Immutable prompts** — `prompt_hash` enforced in CI
- **Verifier + consensus pipeline** — research → verify → weighted merge
- **Raft leader election** (Phase 3) — coordinates hourly shard writes without split-brain
- **Reputation-weighted consensus** (Phase 4) — proof-of-trust for market sentiment

Details: [ARCHITECTURE.md](ARCHITECTURE.md) · [CONSENSUS.md](CONSENSUS.md) · [GOVERNANCE.md](GOVERNANCE.md)

---

## Releases

Maintainers:

```bash
# bump version in pyproject.toml + src/agents_unite/__init__.py
git tag v0.1.0
git push origin v0.1.0
```

The [Release workflow](../.github/workflows/release.yml) builds wheel/sdist, publishes to **PyPI**, and creates a GitHub Release.

**PyPI setup (one-time):** Register `agents-unite` on PyPI, add [trusted publisher](https://docs.pypi.org/trusted-publishers/) for this repo's `release.yml` workflow, or set `PYPI_API_TOKEN` repo secret. See [MAINTAINER_RELEASE.md](MAINTAINER_RELEASE.md).
