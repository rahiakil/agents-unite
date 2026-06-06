#!/usr/bin/env bash
# Main entry: assign role/ticker, scaffold, save prompt.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

ensure_gitignore() {
  local gitignore="$REPO_ROOT/.gitignore"
  grep -qxF '.agents-unite/' "$gitignore" 2>/dev/null || echo '.agents-unite/' >> "$gitignore"
}

ensure_gitignore
mkdir -p .agents-unite

if [[ -z "${AGENTS_UNITE_CONTRIBUTOR:-}" ]]; then
  gh_user="$(python3 -c 'import sys; sys.path.insert(0,"scripts"); from au_common import github_username, contributor_id; print(contributor_id())' 2>/dev/null || true)"
  if [[ -n "$gh_user" && "$gh_user" != "anonymous" ]]; then
    export AGENTS_UNITE_CONTRIBUTOR="$gh_user"
    echo "Contributor: $gh_user"
  fi
fi

tmp_out="$(mktemp)"
trap 'rm -f "$tmp_out"' EXIT

python3 scripts/run_investigation.py --scaffold --metadata > "$tmp_out"

python3 - "$tmp_out" "$REPO_ROOT/.agents-unite/prompt.md" <<'PY'
import sys
from pathlib import Path
raw = Path(sys.argv[1]).read_text(encoding="utf-8")
marker = "\n--- PROMPT ---\n"
prompt = raw.split(marker, 1)[1] if marker in raw else raw
Path(sys.argv[2]).write_text(prompt.lstrip(), encoding="utf-8")
PY

assignment_json="$(python3 - "$tmp_out" <<'PY'
import json, sys
from pathlib import Path
raw = Path(sys.argv[1]).read_text(encoding="utf-8")
marker = "\n--- PROMPT ---\n"
meta_text = raw.split(marker, 1)[0].strip()
print(meta_text)
PY
)"

ROLE="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["daily_role"])' "$assignment_json")"
FOCUS="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["focus"])' "$assignment_json")"
TICKER="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["ticker"])' "$assignment_json")"
DATE="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["date"])' "$assignment_json")"
OUTPUT="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["output_dir"])' "$assignment_json")"

echo ""
echo "Assignment"
echo "  Role:     $ROLE ($FOCUS)"
echo "  Ticker:   $TICKER"
echo "  Date:     $DATE"
echo "  Output:   $OUTPUT/"
echo "  Prompt:   .agents-unite/prompt.md"
echo ""
echo "Next steps"
echo "  1. Paste prompt into your agent (Cursor, Hermes, OpenClaw, ...)"
echo "  2. python3 scripts/validate_report.py $OUTPUT/"
echo "  3. ./scripts/commit-report.sh  OR  ./scripts/daily-run.sh (full auto)"
echo ""
echo "Install cron: ./scripts/install-cron.sh"
