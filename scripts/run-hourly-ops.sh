#!/usr/bin/env bash
# Hourly ops: summary index + trading pattern shards (maintainer node).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
# shellcheck source=scripts/au-env.sh
source "$REPO_ROOT/scripts/au-env.sh"

ROLE="${1:-patterns_hourly}"
case "$ROLE" in
  summary_update|patterns_hourly) ;;
  *)
    echo "Usage: $0 [summary_update|patterns_hourly]" >&2
    exit 1
    ;;
esac

echo "=== hourly ops: $ROLE ==="
META="$("$AU_PYTHON" scripts/assign_role.py --force-role "$ROLE" --json)"
echo "$META" | "$AU_PYTHON" -m json.tool

"$AU_PYTHON" scripts/run_investigation.py --scaffold --metadata 2>/dev/null || true

if command -v "$AU_PYTHON" >/dev/null; then
  AGENT_CMD="$("$AU_PYTHON" -c "import sys; sys.path.insert(0,'scripts'); from agent_config import resolve_agent_command; print(resolve_agent_command() or '')" 2>/dev/null || true)"
  if [[ -n "$AGENT_CMD" ]]; then
    eval "$AGENT_CMD" || echo "Agent run failed — see .agents-unite/prompt.md"
  else
    echo "Configure agent_adapter (llm/cursor) then re-run."
  fi
fi
