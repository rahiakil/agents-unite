#!/usr/bin/env bash
# Shared helpers for agent adapter scripts.
set -euo pipefail

adapter_repo_root() {
  cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd
}

adapter_prompt_file() {
  local repo
  repo="$(adapter_repo_root)"
  echo "${AGENTS_UNITE_PROMPT:-$repo/.agents-unite/prompt.md}"
}

adapter_require_prompt() {
  local prompt
  prompt="$(adapter_prompt_file)"
  if [[ ! -f "$prompt" ]]; then
    echo "error: prompt not found at $prompt — run ./scripts/run-agent.sh first" >&2
    exit 1
  fi
  echo "$prompt"
}

adapter_subst() {
  local cmd="$1" prompt="$2" repo="$3"
  cmd="${cmd//\{prompt\}/$prompt}"
  cmd="${cmd//\{repo\}/$repo}"
  printf '%s' "$cmd"
}

adapter_run_cmd() {
  local cmd="$1"
  eval exec $cmd
}
