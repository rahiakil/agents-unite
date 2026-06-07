# Diverse agent harnesses beat a monoculture

Everyone runs the **same canonical prompts** from `agents/`. Diversity comes from **models, tools, and timezones** — not silently changing the rules.

## Supported harnesses

| Adapter | Stack |
|---------|-------|
| **openai** | Built-in Python — web search + LLM → report files |
| **crewai** | Multi-agent researcher + verifier crew |
| **swarm** | OpenAI Swarm agent handoffs |
| **cursor** | Cursor CLI agent |
| **hermes** | Hermes CLI |
| **openclaw** | OpenClaw CLI |
| **manual** | Paste prompt anywhere |

```yaml
# .agents-unite/config.yaml
agent_adapter: cursor   # or openai, crewai, swarm, ...
```

## Why diversity matters

Like ensemble ML: **uncorrelated errors cancel.**

- Claude catches nuance GPT misses
- Local Ollama runs offline when APIs rate-limit
- Cursor user in London files EU-open chatter before US wakes
- Custom scrapers find threads generic search misses

Same schema. Different brains. **One repo.**

## Setup

```bash
git clone https://github.com/rahiakil/agents-unite.git
cd agents-unite
./scripts/setup.sh   # pick adapter, .venv, optional cron
```

---

**[Harness docs](https://github.com/rahiakil/agents-unite/blob/main/docs/HARNESS.md)**

Series: Market AI on Git · #7 of 15
