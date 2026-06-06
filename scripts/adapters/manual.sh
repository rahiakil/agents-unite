#!/usr/bin/env bash
# Manual mode — prompt only; user runs external agent
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROMPT="${AGENTS_UNITE_PROMPT:-$REPO_ROOT/.agents-unite/prompt.md}"
echo "Manual mode: paste prompt from $PROMPT into your agent."
echo "Then: AGENT_DONE=1 ./scripts/daily-run.sh"
exit 2
