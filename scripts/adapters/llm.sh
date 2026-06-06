#!/usr/bin/env bash
# Built-in Python LLM harness (OpenAI-compatible, Anthropic, Ollama)
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
exec python3 "$REPO_ROOT/scripts/run_agent.py" "$@"
