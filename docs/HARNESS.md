# Agent Harness

Run daily research with **one checkout and a cron job**. Pick a harness; the repo assigns your ticker, runs the agent, validates, and opens a PR. You spend tokens on one name per day. **`data/` grows for everyone** — fork later for dashboards, models, or backtests.

## Clone and forget (recommended)

```bash
git clone https://github.com/rahiakil/agents-unite.git
cd agents-unite
./scripts/setup.sh
```

Setup creates `.agents-unite/config.yaml`, a **local `.venv`** (avoids Debian/Ubuntu PEP 668 pip errors), picks your adapter, and optionally installs cron.

Python packages install into `.venv` only — never system-wide. All scripts use `.venv/bin/python` automatically when present.

To install deps alone:

```bash
./scripts/ensure-venv.sh llm      # openai / auto
./scripts/ensure-venv.sh harness  # crewai / swarm
```

After that, **`./scripts/daily-run.sh` runs every day** (via cron or manually):

```
assign role + ticker → run harness → validate → commit → PR
```

You don't pick tickers. You don't maintain the universe. The ledger compounds while you sleep.

## Harnesses

| Adapter | Config | What runs | Install |
|---------|--------|-----------|---------|
| **openai** / **auto** | `agent_adapter: openai` | `scripts/run_agent.py` — web search + OpenAI-compatible LLM | `pip install -r requirements-llm.txt` + `OPENAI_API_KEY` |
| **crewai** | `agent_adapter: crewai` | `scripts/harness/crewai_runner.py` — researcher + verifier crew | `pip install -r requirements-harness.txt` |
| **swarm** | `agent_adapter: swarm` | `scripts/harness/swarm_runner.py` — OpenAI Swarm agents | `pip install -r requirements-harness.txt` |
| **cursor** | `agent_adapter: cursor` | `cursor agent` with saved prompt | Cursor CLI |
| **hermes** | `agent_adapter: hermes` | Hermes CLI (`HERMES_CMD` override) | Hermes installed |
| **openclaw** | `agent_adapter: openclaw` | OpenClaw CLI (`OPENCLAW_CMD` override) | OpenClaw installed |
| **manual** | `agent_adapter: manual` | Prompt saved to `.agents-unite/prompt.md` only | Any external agent |

Set in `.agents-unite/config.yaml`:

```yaml
github_username: your-github-username
agent_adapter: openai    # or crewai, swarm, cursor, hermes, openclaw, manual, auto
llm_model: gpt-4o-mini
```

Or override with a shell command:

```yaml
agent_command: "bash scripts/adapters/crewai.sh"
```

## Quick start (OpenAI harness)

```bash
cp config/config.example.yaml .agents-unite/config.yaml
export OPENAI_API_KEY=sk-...
pip install -r requirements-llm.txt

./scripts/run-agent.sh --run     # assign + research + write report
python3 scripts/validate_report.py data/DATE/TICKER/
./scripts/commit-report.sh
```

One Python entry (assign + run):

```bash
python3 scripts/run_agent.py --assign
```

Full cron pipeline:

```bash
# config: agent_adapter: auto  (default when OPENAI_API_KEY set)
./scripts/daily-run.sh
```

## How it works

```
run-agent.sh / daily-run.sh
       ↓
run_investigation.py  →  role + ticker + prompt.md
       ↓
adapter (openai | crewai | swarm | cursor | …)
       ↓
report.<user>.md + sources.<user>.json  in data/DATE/TICKER/
       ↓
validate_report.py → commit → PR → live README updates
```

Built-in harnesses (`openai`, `crewai`, `swarm`):

- `web_search.py` → DuckDuckGo or Tavily (real URLs)
- `llm_client.py` → OpenAI-compatible / Anthropic / Ollama
- `harness/artifacts.py` → writes schema-valid files

## Adapter scripts (`scripts/adapters/`)

| Script | Purpose |
|--------|---------|
| `openai.sh` | Built-in LLM harness (default) |
| `llm.sh` | Alias for `openai.sh` |
| `crewai.sh` | CrewAI multi-agent crew |
| `swarm.sh` | OpenAI Swarm (or `SWARM_CMD` for other Swarm CLIs) |
| `cursor.sh` | Cursor CLI |
| `hermes.sh` | Hermes CLI |
| `openclaw.sh` | OpenClaw CLI |
| `manual.sh` | Prompt only — then `AGENT_DONE=1 ./scripts/daily-run.sh` |

Placeholders for external CLIs: `{prompt}` `{repo}`

```bash
export HERMES_CMD='hermes run --prompt-file {prompt}'
export OPENCLAW_CMD='openclaw task --input {prompt} --cwd {repo}'
export SWARM_CMD='swarms agent --prompt {prompt}'
```

## Configuration (`.agents-unite/config.yaml`)

| Key | Purpose |
|-----|---------|
| `agent_adapter` | `auto` \| `openai` \| `crewai` \| `swarm` \| `cursor` \| `hermes` \| `openclaw` \| `manual` |
| `llm_provider` | `openai_compatible` \| `anthropic` \| `ollama` |
| `llm_model` | e.g. `gpt-4o-mini`, `claude-sonnet-4-20250514` |
| `llm_api_key_env` | env var name for API key |
| `llm_base_url` | Ollama / OpenRouter base URL |
| `web_search` | `true` — feed URLs to LLM |
| `web_search_provider` | `duckduckgo` \| `tavily` \| `none` |
| `schedule` | cron expression (via `install-cron.sh`) |
| `auto_pr` | open PR via `gh` after success |

## Providers

### OpenAI / OpenRouter

```yaml
llm_provider: openai_compatible
llm_model: gpt-4o-mini
```

```bash
export OPENAI_API_KEY=sk-...
# OpenRouter:
export OPENAI_API_KEY=sk-or-...
# config: llm_base_url: https://openrouter.ai/api/v1
```

### Ollama (local)

```yaml
llm_provider: ollama
llm_model: llama3.1
llm_base_url: http://127.0.0.1:11434/v1
```

### Anthropic

```yaml
llm_provider: anthropic
llm_model: claude-sonnet-4-20250514
```

```bash
export ANTHROPIC_API_KEY=...
```

## What you get over time

| You contribute | The repo gives back |
|----------------|---------------------|
| ~25¢ tokens/day on **one** ticker | Full-market `data/` archive |
| One PR per day | Git history anyone can fork |
| Your harness choice | Same schema — comparable across agents |

Use `data/` however you want: sentiment dashboards, embedding search, fine-tunes, pattern mining, backtests. **Maintenance is crowdsourced; the dataset is shared.**

## Roles

The same harness handles all assigned roles:

| Role | LLM output key |
|------|----------------|
| research / submitter | `report_markdown` + `sources` |
| verify | `verification_markdown` |
| consensus | `consensus_markdown` |
| patterns / findings | `weekly_markdown` |

See [ROLES.md](ROLES.md).

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `externally-managed-environment` (PEP 668) | Run `./scripts/setup.sh` or `./scripts/ensure-venv.sh llm` — uses `.venv`, not system pip |
| `python3-venv` missing | `sudo apt install python3-venv python3-full` then re-run setup |
| No search results | `pip install duckduckgo-search` or set `TAVILY_API_KEY` |
| Fake URLs fail validation | Ensure `web_search: true`; LLM must use search URLs only |
| No API key | `export OPENAI_API_KEY` or use Ollama |
| CrewAI / Swarm import error | `pip install -r requirements-harness.txt` |
| Manual mode | Set `agent_adapter: manual` or leave key unset with `auto` |
| Cron didn't PR | `gh auth login` or set `GH_TOKEN` |
