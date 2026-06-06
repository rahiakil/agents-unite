#!/usr/bin/env bash
# OpenAI Swarm harness — or set SWARM_CMD for other Swarm CLIs (e.g. swarms package)
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
# shellcheck source=scripts/adapters/_common.sh
source "$REPO_ROOT/scripts/adapters/_common.sh"

PROMPT="$(adapter_require_prompt)"
CMD="${SWARM_CMD:-}"

if [[ -n "$CMD" ]]; then
  CMD="$(adapter_subst "$CMD" "$PROMPT" "$REPO_ROOT")"
  adapter_run_cmd "$CMD"
fi

if python3 -c "import swarm" 2>/dev/null; then
  exec python3 "$REPO_ROOT/scripts/harness/swarm_runner.py" "$@"
fi

echo "error: install OpenAI Swarm (pip install -r requirements-harness.txt)" >&2
echo "       or set SWARM_CMD='swarms agent --prompt {prompt}'" >&2
exit 1
