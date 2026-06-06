#!/usr/bin/env bash
# One-shot setup: config, venv, adapter, cron — clone and run daily.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
# shellcheck source=scripts/au-env.sh
source "$REPO_ROOT/scripts/au-env.sh"

echo "=== agents-unite setup ==="
echo ""

# 1. Config + cron
./scripts/install-cron.sh

echo ""
echo "=== Agent harness ==="
echo "  1) openai   — built-in Python harness (needs OPENAI_API_KEY)"
echo "  2) crewai   — CrewAI multi-agent crew"
echo "  3) swarm    — OpenAI Swarm agents"
echo "  4) cursor   — Cursor CLI (no Python packages required)"
echo "  5) hermes   — Hermes CLI"
echo "  6) openclaw — OpenClaw CLI"
echo "  7) manual   — save prompt; paste into any agent"
echo "  8) auto     — openai when API key set, else manual"
echo ""
read -r -p "Adapter [auto]: " ADAPTER || true
ADAPTER="${ADAPTER:-auto}"

CONFIG="$REPO_ROOT/.agents-unite/config.yaml"
au_python - "$CONFIG" "$ADAPTER" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
adapter = sys.argv[2].strip().lower()
aliases = {
    "1": "openai", "2": "crewai", "3": "swarm", "4": "cursor",
    "5": "hermes", "6": "openclaw", "7": "manual", "8": "auto",
}
adapter = aliases.get(adapter, adapter)
text = p.read_text(encoding="utf-8")
lines = []
found = False
for line in text.splitlines():
    if line.startswith("agent_adapter:"):
        lines.append(f"agent_adapter: {adapter}")
        found = True
    else:
        lines.append(line)
if not found:
    lines.append(f"agent_adapter: {adapter}")
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Set agent_adapter: {adapter}")
PY

# Normalize adapter name for dep logic
ADAPTER_NORM="$(au_python - "$ADAPTER" <<'PY'
import sys
aliases = {
    "1": "openai", "2": "crewai", "3": "swarm", "4": "cursor",
    "5": "hermes", "6": "openclaw", "7": "manual", "8": "auto",
}
print(aliases.get(sys.argv[1].strip().lower(), sys.argv[1].strip().lower()))
PY
)"

NEEDS_VENV=0
case "$ADAPTER_NORM" in
  openai|auto|llm|crewai|swarm) NEEDS_VENV=1 ;;
esac

if [[ "$NEEDS_VENV" == "1" ]]; then
  echo ""
  if [[ "$ADAPTER_NORM" == "crewai" || "$ADAPTER_NORM" == "swarm" ]]; then
    ./scripts/ensure-venv.sh harness
  else
    ./scripts/ensure-venv.sh llm
  fi
  # shellcheck source=scripts/au-env.sh
  source "$REPO_ROOT/scripts/au-env.sh"
else
  echo ""
  echo "No Python packages needed for adapter: $ADAPTER_NORM"
  echo "(Assignment scripts use system python3; optional: ./scripts/ensure-venv.sh llm)"
fi

chmod +x "$REPO_ROOT"/scripts/adapters/*.sh
chmod +x "$REPO_ROOT"/scripts/daily-run.sh "$REPO_ROOT"/scripts/run-agent.sh
chmod +x "$REPO_ROOT"/scripts/ensure-venv.sh

echo ""
echo "=== Daily loop ==="
echo "  Cron:     ./scripts/daily-run.sh  (uses .venv when present)"
echo "  Each day: assign → harness → validate → commit → PR"
echo ""
echo "=== Test ==="
if [[ "$NEEDS_VENV" == "1" ]]; then
  echo "  export OPENAI_API_KEY=sk-..."
fi
echo "  ./scripts/run-agent.sh --run"
echo "  ./scripts/daily-run.sh"
