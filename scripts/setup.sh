#!/usr/bin/env bash
# One-shot setup: config, deps, adapter, cron — clone and run daily.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== agents-unite setup ==="
echo ""

# 1. Config + cron
./scripts/install-cron.sh

echo ""
echo "=== Agent harness ==="
echo "Pick how daily research runs (stored in .agents-unite/config.yaml):"
echo "  1) openai   — built-in Python harness + web search (needs OPENAI_API_KEY)"
echo "  2) crewai   — CrewAI multi-agent crew (pip install -r requirements-harness.txt)"
echo "  3) swarm    — OpenAI Swarm agents (pip install -r requirements-harness.txt)"
echo "  4) cursor   — Cursor CLI (cursor agent)"
echo "  5) hermes   — Hermes CLI"
echo "  6) openclaw — OpenClaw CLI"
echo "  7) manual   — save prompt only; paste into any agent"
echo "  8) auto     — openai when API key set, else manual (default)"
echo ""
read -r -p "Adapter [auto]: " ADAPTER || true
ADAPTER="${ADAPTER:-auto}"

CONFIG="$REPO_ROOT/.agents-unite/config.yaml"
python3 - "$CONFIG" "$ADAPTER" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
adapter = sys.argv[2].strip().lower()
aliases = {"1": "openai", "2": "crewai", "3": "swarm", "4": "cursor",
           "5": "hermes", "6": "openclaw", "7": "manual", "8": "auto"}
adapter = aliases.get(adapter, adapter)
text = p.read_text(encoding="utf-8")
if "agent_adapter:" in text:
    lines = []
    for line in text.splitlines():
        if line.startswith("agent_adapter:"):
            lines.append(f"agent_adapter: {adapter}")
        else:
            lines.append(line)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
else:
    p.write_text(text.rstrip() + f"\nagent_adapter: {adapter}\n", encoding="utf-8")
print(f"Set agent_adapter: {adapter}")
PY

echo ""
read -r -p "Install Python deps now? [Y/n]: " DEPS || true
if [[ "${DEPS:-Y}" =~ ^[Yy]?$ ]]; then
  pip install -r requirements-llm.txt
  if [[ "$ADAPTER" == "crewai" || "$ADAPTER" == "swarm" || "$ADAPTER" == "2" || "$ADAPTER" == "3" ]]; then
    pip install -r requirements-harness.txt
  fi
fi

chmod +x "$REPO_ROOT"/scripts/adapters/*.sh
chmod +x "$REPO_ROOT"/scripts/daily-run.sh "$REPO_ROOT"/scripts/run-agent.sh

echo ""
echo "=== Daily loop (automatic) ==="
echo "  Cron runs:  ./scripts/daily-run.sh"
echo "  Each day:   assign ticker → run harness → validate → commit → PR"
echo "  You spend ~25¢ on your ticker. The repo grows for everyone."
echo ""
echo "=== Test now ==="
echo "  export OPENAI_API_KEY=sk-...   # if using openai/auto/crewai/swarm"
echo "  ./scripts/run-agent.sh --run"
echo "  ./scripts/daily-run.sh"
echo ""
echo "Fork later for dashboards, models, backtests — data/ is yours to use."
