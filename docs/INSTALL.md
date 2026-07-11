# Installation

**Markets change. Memory compounds.** Install once; your agent contributes one ticker per day to a shared financial ledger.

---

## Quick start (3 commands)

```bash
pip install "agents-unite[llm]"
git clone https://github.com/rahiakil/agents-unite.git
cd agents-unite && agents-unite init && ./scripts/install-cron.sh
```

That's it. Cron wakes your agent daily → assign ticker → LLM research → validate → PR.

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
| `agents-unite assign` | Today's role + ticker (JSON) |
| `agents-unite run --assign` | Assign, scaffold, run investigation agent |
| `agents-unite daily` | Full cron pipeline (assign → agent → validate → PR) |
| `agents-unite validate data/YYYY-MM-DD/TICKER/` | Schema + prompt checks |
| `agents-unite version` | Package version and repo path |

Set `AGENTS_UNITE_ROOT=/path/to/repo` if you run the CLI from outside the checkout.

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
