#!/usr/bin/env bash
# Hermes adapter — set HERMES_CMD in config or environment.
# Example: export HERMES_CMD='hermes run --prompt-file {prompt}'
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
# shellcheck source=scripts/adapters/_common.sh
source "$REPO_ROOT/scripts/adapters/_common.sh"

PROMPT="$(adapter_require_prompt)"
CMD="${HERMES_CMD:-hermes run --prompt-file {prompt}}"

if ! command -v hermes >/dev/null 2>&1 && [[ "$CMD" == "hermes run --prompt-file {prompt}" ]]; then
  echo "error: hermes CLI not found. Install Hermes or set HERMES_CMD" >&2
  exit 1
fi

CMD="$(adapter_subst "$CMD" "$PROMPT" "$REPO_ROOT")"
adapter_run_cmd "$CMD"
