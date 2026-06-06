#!/usr/bin/env bash
# Validate today's assignment and create a sentiment commit.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
# shellcheck source=scripts/au-env.sh
source "$REPO_ROOT/scripts/au-env.sh"

META="$("$AU_PYTHON" scripts/assign_role.py --json)"
TICKER="$("$AU_PYTHON" -c 'import json,sys; print(json.loads(sys.argv[1])["ticker"])' "$META")"
DATE="$("$AU_PYTHON" -c 'import json,sys; print(json.loads(sys.argv[1])["date"])' "$META")"
ROLE="$("$AU_PYTHON" -c 'import json,sys; print(json.loads(sys.argv[1])["daily_role"])' "$META")"
BRANCH="$("$AU_PYTHON" scripts/branch_name.py)"
report_dir="data/${DATE}/${TICKER}"

echo "Validating: $report_dir/ (role=$ROLE)"
if ! "$AU_PYTHON" scripts/validate_report.py "$report_dir/"; then
  echo "Commit aborted — fix validation errors."
  exit 1
fi

git checkout -B "$BRANCH"
git add "data/${DATE}/${TICKER}/"
git commit -m "sentiment: ${TICKER} ${DATE} (${ROLE})"

echo "Committed on branch: $BRANCH"
echo "Push + PR: git push -u origin $BRANCH && gh pr create --title \"sentiment: $TICKER $DATE\""
