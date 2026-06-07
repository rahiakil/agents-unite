#!/usr/bin/env bash
# Publish Market AI gist series to GitHub.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/au-env.sh
source "$REPO_ROOT/scripts/au-env.sh"
cd "$REPO_ROOT"
exec "$AU_PYTHON" "$REPO_ROOT/scripts/publish_gists.py" "$@"
