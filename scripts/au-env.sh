#!/usr/bin/env bash
# Shared Python resolution: prefer repo .venv (PEP 668 safe).
# Source from any script:  source "$(dirname "$0")/au-env.sh"

if [[ -z "${REPO_ROOT:-}" ]]; then
  REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

AU_VENV="${REPO_ROOT}/.venv"

if [[ -x "${AU_VENV}/bin/python" ]]; then
  AU_PYTHON="${AU_VENV}/bin/python"
  AU_PIP="${AU_VENV}/bin/pip"
  export PATH="${AU_VENV}/bin:${PATH}"
  export VIRTUAL_ENV="${AU_VENV}"
else
  AU_PYTHON="${AGENTS_UNITE_PYTHON:-python3}"
  AU_PIP="${AGENTS_UNITE_PIP:-pip3}"
fi

# Cron uses a minimal PATH — ensure user-local bins (cursor, gh, etc.) resolve.
if [[ -n "${HOME:-}" ]]; then
  export PATH="${HOME}/.local/bin:${HOME}/bin:${PATH}"
fi

export AGENTS_UNITE_PYTHON="${AU_PYTHON}"
export REPO_ROOT

au_python() { "$AU_PYTHON" "$@"; }
