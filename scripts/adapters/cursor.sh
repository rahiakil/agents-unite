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
CURSOR_BIN="${CURSOR_BIN:-}"
if [[ -z "$CURSOR_BIN" ]]; then
  if command -v cursor >/dev/null 2>&1; then
    CURSOR_BIN="$(command -v cursor)"
  elif [[ -x "${HOME:-}/.local/bin/cursor" ]]; then
    CURSOR_BIN="${HOME}/.local/bin/cursor"
  fi
fi
if [[ -z "$CURSOR_BIN" || ! -x "$CURSOR_BIN" ]]; then
  echo "error: cursor CLI not found. Install Cursor CLI or set CURSOR_BIN." >&2
  exit 1
fi
exec "$CURSOR_BIN" agent --print --force --workspace "$REPO_ROOT" -- "$(cat "$PROMPT_FILE")"
