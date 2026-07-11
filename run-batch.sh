#!/usr/bin/env bash
# Run the built-in LLM agent on multiple tickers to populate data/ quickly.
#
# Setup (PyPI + clone):
#   pip install "agents-unite[llm]"
#   git clone https://github.com/rahiakil/agents-unite.git && cd agents-unite
#   agents-unite init
#   # Ollama (free, local): llm_provider: ollama in .agents-unite/config.yaml
#   # Or: export OPENAI_API_KEY=sk-...
#
# Usage:
#   ./run-batch.sh                          # 3 uncovered tickers today
#   ./run-batch.sh --count 10               # 10 tickers
#   ./run-batch.sh --tickers NVDA,AMD,GOOGL
#   ./run-batch.sh --count 5 --skip-existing
#   ./run-batch.sh --count 5 --model gemma4:latest
#   AGENTS_UNITE_LLM_TIMEOUT=600 ./run-batch.sh --tickers NVDA,AMD
#
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"
source "$REPO_ROOT/scripts/au-env.sh"
exec "$AU_PYTHON" "$REPO_ROOT/scripts/run_batch.py" "$@"
