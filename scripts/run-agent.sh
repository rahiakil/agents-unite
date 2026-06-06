#!/usr/bin/env bash
# Main entry: assign role/ticker, scaffold, save prompt.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
# shellcheck source=scripts/au-env.sh
source "$REPO_ROOT/scripts/au-env.sh"

RUN_LLM=0
[[ "${1:-}" == "--run" ]] && RUN_LLM=1

ensure_gitignore() {
  local gitignore="$REPO_ROOT/.gitignore"
  grep -qxF '.agents-unite/' "$gitignore" 2>/dev/null || echo '.agents-unite/' >> "$gitignore"
}

ensure_gitignore
mkdir -p .agents-unite

if [[ -z "${AGENTS_UNITE_CONTRIBUTOR:-}" ]]; then
  gh_user="$("$AU_PYTHON" -c 'import sys; sys.path.insert(0,"scripts"); from au_common import github_username, contributor_id; print(contributor_id())' 2>/dev/null || true)"
  if [[ -n "$gh_user" && "$gh_user" != "anonymous" ]]; then
    export AGENTS_UNITE_CONTRIBUTOR="$gh_user"
    echo "Contributor: $gh_user"
  fi
fi

tmp_out="$(mktemp)"
trap 'rm -f "$tmp_out"' EXIT

"$AU_PYTHON" scripts/run_investigation.py --scaffold --metadata > "$tmp_out"

"$AU_PYTHON" - "$tmp_out" "$REPO_ROOT/.agents-unite/prompt.md" <<'PY'
import sys
from pathlib import Path
raw = Path(sys.argv[1]).read_text(encoding="utf-8")
marker = "\n--- PROMPT ---\n"
prompt = raw.split(marker, 1)[1] if marker in raw else raw
Path(sys.argv[2]).write_text(prompt.lstrip(), encoding="utf-8")
PY

assignment_json="$("$AU_PYTHON" - "$tmp_out" <<'PY'
import json, sys
from pathlib import Path
raw = Path(sys.argv[1]).read_text(encoding="utf-8")
marker = "\n--- PROMPT ---\n"
meta_text = raw.split(marker, 1)[0].strip()
print(meta_text)
PY
)"

ROLE="$("$AU_PYTHON" -c 'import json,sys; print(json.loads(sys.argv[1])["daily_role"])' "$assignment_json")"
FOCUS="$("$AU_PYTHON" -c 'import json,sys; print(json.loads(sys.argv[1])["focus"])' "$assignment_json")"
TICKER="$("$AU_PYTHON" -c 'import json,sys; print(json.loads(sys.argv[1])["ticker"])' "$assignment_json")"
DATE="$("$AU_PYTHON" -c 'import json,sys; print(json.loads(sys.argv[1])["date"])' "$assignment_json")"
OUTPUT="$("$AU_PYTHON" -c 'import json,sys; print(json.loads(sys.argv[1])["output_dir"])' "$assignment_json")"

echo ""
echo "Assignment"
echo "  Role:     $ROLE ($FOCUS)"
echo "  Ticker:   $TICKER"
echo "  Date:     $DATE"
echo "  Output:   $OUTPUT/"
echo "  Prompt:   .agents-unite/prompt.md"
echo ""

if [[ "$RUN_LLM" == "1" ]]; then
  AGENT_CMD="$("$AU_PYTHON" -c "
import sys; sys.path.insert(0,'scripts')
from agent_config import resolve_agent_command
print(resolve_agent_command() or '')
" 2>/dev/null || true)"
  if [[ -n "$AGENT_CMD" ]]; then
    echo "Running agent: $AGENT_CMD"
    eval "$AGENT_CMD" || exit 1
    echo ""
    echo "Done. Validate: $AU_PYTHON scripts/validate_report.py $OUTPUT/"
  else
    echo "No agent configured. Try: ./scripts/ensure-venv.sh llm && export OPENAI_API_KEY"
    exit 1
  fi
else
  echo "Next steps"
  echo "  ./scripts/run-agent.sh --run"
  echo "  $AU_PYTHON scripts/validate_report.py $OUTPUT/"
  echo "  ./scripts/commit-report.sh  OR  ./scripts/daily-run.sh"
fi
echo ""
echo "Setup: ./scripts/setup.sh"
