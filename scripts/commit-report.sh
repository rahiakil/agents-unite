#!/usr/bin/env bash
# Validate today's assignment and create a sentiment commit.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

META="$(python3 scripts/assign_role.py --json)"
TICKER="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["ticker"])' "$META")"
DATE="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["date"])' "$META")"
ROLE="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["daily_role"])' "$META")"
BRANCH="$(python3 scripts/branch_name.py)"
report_dir="data/${DATE}/${TICKER}"

echo "Validating: $report_dir/ (role=$ROLE)"
if ! python3 scripts/validate_report.py "$report_dir/"; then
  echo "Commit aborted — fix validation errors."
  exit 1
fi

git checkout -B "$BRANCH"
git add "data/${DATE}/${TICKER}/"
git commit -m "sentiment: ${TICKER} ${DATE} (${ROLE})"

echo "Committed on branch: $BRANCH"
echo "Push + PR: git push -u origin $BRANCH && gh pr create --title \"sentiment: $TICKER $DATE\""
