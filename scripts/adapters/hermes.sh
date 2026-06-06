#!/usr/bin/env bash
# Hermes adapter — set HERMES_CMD in config or environment.
# Example: export HERMES_CMD='hermes run --prompt-file {prompt}'
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
PROMPT_FILE="${AGENTS_UNITE_PROMPT:-$REPO_ROOT/.agents-unite/prompt.md}"
CMD="${HERMES_CMD:-}"
if [[ -z "$CMD" ]]; then
  echo "error: set HERMES_CMD, e.g. hermes run --prompt-file $PROMPT_FILE" >&2
  exit 1
fi
CMD="${CMD//\{prompt\}/$PROMPT_FILE}"
CMD="${CMD//\{repo\}/$REPO_ROOT}"
eval exec $CMD
