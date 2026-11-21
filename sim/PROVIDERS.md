# Model providers

`python3 -m sim --provider NAME` selects the generator. `auto` walks the list below and uses the first provider that has credentials. A named provider with no credentials, and any provider that errors, falls back to `rule`. `rule` is deterministic, costs nothing, and is what the seeded proof and the pull-request CI job use.

| Provider | Secret | Model variable | Default model |
| --- | --- | --- | --- |
| `openrouter` | `OPENROUTER_API_KEY` | `SIM_OPENROUTER_MODEL` | `openrouter/free` |
| `groq` | `GROQ_API_KEY` | `SIM_GROQ_MODEL` | `llama-3.1-8b-instant` |
| `gemini` | `GEMINI_API_KEY` or `GOOGLE_API_KEY` | `SIM_GEMINI_MODEL` | `gemini-2.0-flash` |
| `huggingface` | `HF_TOKEN` or `HUGGINGFACE_API_KEY` | `SIM_HF_MODEL` | `Qwen/Qwen2.5-7B-Instruct` |
| `ollama` | none | `SIM_OLLAMA_MODEL` | `llama3.2` |
| `llamacpp` | none | `LLAMA_CPP_MODEL` (GGUF path) | |
| `rule` | none | | `rule` |

Ollama also needs `SIM_ENABLE_OLLAMA=1` and a reachable `OLLAMA_HOST` (default `http://127.0.0.1:11434`). llama.cpp needs `LLAMA_CPP_BIN` (default `llama-cli`) on `PATH` and the GGUF file from `LLAMA_CPP_MODEL`. GitHub-hosted runners have neither binary. Those two providers are for a machine you control.

The daily workflow (`.github/workflows/sim-daily.yml`) maps the four API secrets and the four `SIM_*_MODEL` repository variables. With none of the secrets set, `auto` selects `rule` and the job still passes.

`--llm-cap` limits how many honest chain attempts call a model. The daily default is 11. Cells stay on `rule` so a day of 34 personas times five modes times three prompts does not fan out into API calls. `cost_usd` is 0 for `rule`, `openrouter/free`, and any model id ending in `:free`. Other prices are left null.

Read the same names from the environment locally. Do not commit key values.
