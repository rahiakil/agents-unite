#!/usr/bin/env bash
# OpenAI / OpenRouter — built-in LLM harness (web search + structured output)
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
# shellcheck source=scripts/au-env.sh
source "$REPO_ROOT/scripts/au-env.sh"
exec "$AU_PYTHON" "$REPO_ROOT/scripts/run_agent.py" "$@"
