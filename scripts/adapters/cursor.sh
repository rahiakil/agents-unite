#!/usr/bin/env bash
# Cursor CLI adapter — requires: cursor agent
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
PROMPT_FILE="${AGENTS_UNITE_PROMPT:-$REPO_ROOT/.agents-unite/prompt.md}"
if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "error: prompt not found at $PROMPT_FILE — run ./scripts/run-agent.sh first" >&2
  exit 1
fi
if ! command -v cursor >/dev/null 2>&1; then
  echo "error: cursor CLI not found. Install Cursor or use agent_adapter: llm" >&2
  exit 1
fi
exec cursor agent --print --force --workspace "$REPO_ROOT" -- "$(cat "$PROMPT_FILE")"
