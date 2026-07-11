#!/usr/bin/env bash
# Direct, human-triggered research for specific ticker(s).
# Use this when you spot a coverage gap and want to fill it now —
# no need to wait for the daily cron assignment.
#
# Usage:
#   ./research.sh NVDA                       # one ticker
#   ./research.sh NVDA AMD GOOGL             # several
#   ./research.sh NVDA --model gemma4:latest
#   ./research.sh --count 5 --skip-existing  # 5 least-covered today
#   ./research.sh TSLA --dry-run
#
# Equivalent CLI (after `pip install agents-unite`):
#   agents-unite research NVDA
#
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"
source "$REPO_ROOT/scripts/au-env.sh"

# Split leading bare ticker args (NVDA AMD) from --flags for run_batch.py.
TICKERS=()
PASS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -*) PASS+=("$1"); shift; [[ $# -gt 0 && "$1" != -* ]] && { PASS+=("$1"); shift; } ;;
    *)  TICKERS+=("$1"); shift ;;
  esac
done

ARGS=()
if [[ ${#TICKERS[@]} -gt 0 ]]; then
  ARGS+=(--tickers "$(IFS=,; echo "${TICKERS[*]}")")
fi
ARGS+=("${PASS[@]:-}")

exec "$AU_PYTHON" "$REPO_ROOT/scripts/run_batch.py" "${ARGS[@]}"
