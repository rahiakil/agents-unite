#!/usr/bin/env bash
# OpenClaw / NimoClaw adapter — set OPENCLAW_CMD in environment.
# Example: export OPENCLAW_CMD='openclaw task --input {prompt} --cwd {repo}'
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
PROMPT_FILE="${AGENTS_UNITE_PROMPT:-$REPO_ROOT/.agents-unite/prompt.md}"
CMD="${OPENCLAW_CMD:-${NIMOCLAW_CMD:-}}"
if [[ -z "$CMD" ]]; then
  echo "error: set OPENCLAW_CMD or NIMOCLAW_CMD" >&2
  exit 1
fi
CMD="${CMD//\{prompt\}/$PROMPT_FILE}"
CMD="${CMD//\{repo\}/$REPO_ROOT}"
eval exec $CMD
