#!/usr/bin/env bash
# Create .venv and install requirements (avoids PEP 668 system pip errors).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/au-env.sh
source "$REPO_ROOT/scripts/au-env.sh"
cd "$REPO_ROOT"

PROFILE="${1:-llm}"   # llm | harness | skip

if [[ "$PROFILE" == "skip" ]]; then
  exit 0
fi

if [[ ! -x "${AU_VENV}/bin/python" ]]; then
  echo "Creating virtualenv at .venv ..."
  if ! python3 -m venv "${AU_VENV}" 2>/dev/null; then
    echo "error: could not create .venv" >&2
    echo "  Debian/Ubuntu: sudo apt install python3-venv python3-full" >&2
    echo "  Then re-run: ./scripts/setup.sh" >&2
    exit 1
  fi
  # shellcheck source=scripts/au-env.sh
  source "$REPO_ROOT/scripts/au-env.sh"
fi

echo "Installing into .venv (not system Python) ..."
"$AU_PIP" install -q --upgrade pip

case "$PROFILE" in
  llm)
    "$AU_PIP" install -r requirements-llm.txt
    ;;
  harness)
    "$AU_PIP" install -r requirements-harness.txt
    ;;
  *)
    echo "error: unknown profile '$PROFILE' (use llm, harness, or skip)" >&2
    exit 1
    ;;
esac

echo "OK: $( "$AU_PYTHON" --version ) at ${AU_VENV}"
