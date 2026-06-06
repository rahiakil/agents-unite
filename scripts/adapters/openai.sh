#!/usr/bin/env bash
# OpenAI / OpenRouter — built-in LLM harness (web search + structured output)
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
exec python3 "$REPO_ROOT/scripts/run_agent.py" "$@"
