# Agent Harness

Run daily research **without** an external agent IDE — or plug in Cursor, Hermes, OpenClaw.

## Quick start (Python + LLM)

```bash
cp config/config.example.yaml .agents-unite/config.yaml
# edit github_username

export OPENAI_API_KEY=sk-...
pip install -r requirements-llm.txt   # pyyaml + duckduckgo-search

./scripts/run-agent.sh                # assign + save prompt
python3 scripts/run_agent.py          # web search + LLM → report files
python3 scripts/validate_report.py data/DATE/TICKER/
./scripts/commit-report.sh
```

One command (assign + run):

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
run-agent.sh → assign role + prompt.md
       ↓
run_agent.py
  ├── web_search.py   → DuckDuckGo or Tavily (real URLs)
  ├── llm_client.py   → OpenAI-compatible / Anthropic / Ollama
  └── writes report.*.md + sources.*.json
       ↓
validate_report.py → commit → PR
```

The LLM **synthesizes** search snippets into structured markdown + JSON. No HTML scraping or image dumps.

## Configuration (`.agents-unite/config.yaml`)

| Key | Purpose |
|-----|---------|
| `agent_adapter` | `auto` \| `llm` \| `cursor` \| `hermes` \| `openclaw` \| `manual` |
| `llm_provider` | `openai_compatible` \| `anthropic` \| `ollama` |
| `llm_model` | e.g. `gpt-4o-mini`, `claude-sonnet-4-20250514` |
| `llm_api_key_env` | env var name for API key |
| `llm_base_url` | Ollama / OpenRouter base URL |
| `web_search` | `true` — feed URLs to LLM |
| `web_search_provider` | `duckduckgo` \| `tavily` \| `none` |

## Adapters (`scripts/adapters/`)

| Script | When to use |
|--------|-------------|
| `llm.sh` | Built-in harness (default with API key) |
| `cursor.sh` | Cursor CLI `cursor agent` |
| `hermes.sh` | Set `HERMES_CMD='hermes run --prompt-file {prompt}'` |
| `openclaw.sh` | Set `OPENCLAW_CMD='openclaw task --input {prompt} --cwd {repo}'` |
| `manual.sh` | Prompt only — paste into any agent |

Set explicitly:

```yaml
agent_adapter: cursor
# or
agent_command: "bash scripts/adapters/hermes.sh"
```

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

## Roles

The same harness handles all assigned roles:

| Role | LLM output key |
|------|----------------|
| research | `report_markdown` + `sources` |
| verify | `verification_markdown` |
| consensus | `consensus_markdown` |
| patterns / findings | `weekly_markdown` |

See [ROLES.md](ROLES.md).

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No search results | `pip install duckduckgo-search` or set `TAVILY_API_KEY` |
| Fake URLs fail validation | Ensure `web_search: true`; LLM must use search URLs only |
| No API key | `export OPENAI_API_KEY` or use Ollama |
| Manual mode | Set `agent_adapter: manual` or leave key unset |
