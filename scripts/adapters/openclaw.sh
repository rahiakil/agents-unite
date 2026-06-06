#!/usr/bin/env bash
# OpenClaw adapter — set OPENCLAW_CMD in environment.
# Example: export OPENCLAW_CMD='openclaw task --input {prompt} --cwd {repo}'
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
# shellcheck source=scripts/adapters/_common.sh
source "$REPO_ROOT/scripts/adapters/_common.sh"

PROMPT="$(adapter_require_prompt)"
CMD="${OPENCLAW_CMD:-${NIMOCLAW_CMD:-openclaw task --input {prompt} --cwd {repo}}}"

if ! command -v openclaw >/dev/null 2>&1 && [[ "$CMD" == *"openclaw task"* ]]; then
  echo "error: openclaw CLI not found. Install OpenClaw or set OPENCLAW_CMD" >&2
  exit 1
fi

CMD="$(adapter_subst "$CMD" "$PROMPT" "$REPO_ROOT")"
adapter_run_cmd "$CMD"
