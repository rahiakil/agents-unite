#!/usr/bin/env bash
# CrewAI multi-agent harness
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
exec python3 "$REPO_ROOT/scripts/harness/crewai_runner.py" "$@"
