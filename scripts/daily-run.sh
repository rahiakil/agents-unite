#!/usr/bin/env bash
# Daily cron entry: assign role, run agent, validate, open PR.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

STATE_DIR="$REPO_ROOT/.agents-unite"
LOG_FILE="$STATE_DIR/daily-run.log"
mkdir -p "$STATE_DIR"

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG_FILE"; }

# Load config if present
if [[ -f "$REPO_ROOT/.agents-unite/config.yaml" ]]; then
  export AGENTS_UNITE_CONFIG="$REPO_ROOT/.agents-unite/config.yaml"
fi

# Contributor identity
if [[ -z "${AGENTS_UNITE_CONTRIBUTOR:-}" ]]; then
  gh_user="$(python3 -c 'import sys; sys.path.insert(0,"scripts"); from au_common import github_username; print(github_username() or "")' 2>/dev/null || true)"
  [[ -n "$gh_user" ]] && export AGENTS_UNITE_CONTRIBUTOR="$gh_user"
fi

ATTEMPT=1
MAX_ATTEMPTS=2

run_once() {
  log "Attempt $ATTEMPT: assigning role and ticker"
  python3 scripts/run_investigation.py --scaffold --metadata > "$STATE_DIR/run-meta.json" || return 1

  python3 - "$STATE_DIR/run-meta.json" "$STATE_DIR/prompt.md" <<'PY'
import json, sys
from pathlib import Path
raw = Path(sys.argv[1]).read_text(encoding="utf-8")
# file contains JSON then --- PROMPT ---
if "--- PROMPT ---" in raw:
    meta_text, prompt = raw.split("--- PROMPT ---", 1)
else:
    lines = raw.splitlines()
    meta_lines, prompt_lines = [], []
    in_prompt = False
    for line in lines:
        if line.strip() == "--- PROMPT ---":
            in_prompt = True
            continue
        (prompt_lines if in_prompt else meta_lines).append(line)
    meta_text, prompt = "\n".join(meta_lines), "\n".join(prompt_lines)
Path(sys.argv[2]).write_text(prompt.lstrip(), encoding="utf-8")
PY

  META="$(python3 -c "
import json
from pathlib import Path
raw = Path('$STATE_DIR/run-meta.json').read_text()
if '--- PROMPT ---' in raw:
    raw = raw.split('--- PROMPT ---', 1)[0]
print(json.dumps(json.loads(raw.strip())))
")"

  ROLE="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["daily_role"])' "$META")"
  TICKER="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["ticker"])' "$META")"
  DATE="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["date"])' "$META")"
  OUTPUT="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["output_dir"])' "$META")"

  log "Assigned: role=$ROLE ticker=$TICKER date=$DATE"

  # Run user agent if configured
  AGENT_CMD="$(python3 -c "
import sys; sys.path.insert(0,'scripts')
from au_common import load_yaml_config
c=load_yaml_config()
print(c.get('agent_command',''))
" 2>/dev/null || true)"

  if [[ -n "$AGENT_CMD" ]]; then
    log "Running agent_command"
    eval "$AGENT_CMD" || return 1
  else
    log "No agent_command set — prompt saved to .agents-unite/prompt.md (manual mode)"
    log "Paste prompt into your agent (Cursor, Hermes, OpenClaw, etc.) then re-run with AGENT_DONE=1"
    if [[ "${AGENT_DONE:-0}" != "1" ]]; then
      return 2
    fi
  fi

  log "Validating $OUTPUT"
  python3 scripts/validate_report.py "$OUTPUT/" || return 1

  BRANCH="$(python3 scripts/branch_name.py --contributor "${AGENTS_UNITE_CONTRIBUTOR:-}")"
  log "Branch: $BRANCH"
  git checkout -B "$BRANCH"
  git add "data/$DATE/$TICKER/" || true
  git add "data/$DATE/$TICKER/report"*.md "data/$DATE/$TICKER/sources"*.json "data/$DATE/$TICKER/consensus.md" 2>/dev/null || true

  if git diff --staged --quiet; then
    log "Nothing to commit"
    return 0
  fi

  git commit -m "sentiment: $TICKER $DATE ($ROLE)"

  if command -v gh >/dev/null 2>&1; then
    log "Opening PR"
    gh pr create --title "sentiment: $TICKER $DATE" --body "$(cat <<EOF
Automated daily report from agents-unite.

| Field | Value |
|-------|-------|
| Branch | \`$BRANCH\` |
| Role | $ROLE |
| Ticker | $TICKER |
| Date | $DATE |
| Output | \`$OUTPUT/\` |
EOF
)" --head "$BRANCH" 2>/dev/null || gh pr view --web 2>/dev/null || true
  else
    log "gh not found — commit created locally on $BRANCH"
  fi

  python3 scripts/generate_readme.py 2>/dev/null || true
  return 0
}

alert_verifiers() {
  log "Run failed after retries — alerting (create local alert file)"
  DATE="$(date -u +%Y-%m-%d)"
  echo "Daily run failed at $(date -u +%Y-%m-%dT%H:%M:%SZ). Manual verifier review needed." \
    >> "$STATE_DIR/failed-runs.log"
  if command -v gh >/dev/null 2>&1; then
    gh issue create --title "daily-run failed: $DATE" \
      --body "Automated daily run failed after retry. See .agents-unite/daily-run.log" 2>/dev/null || true
  fi
}

while [[ $ATTEMPT -le $MAX_ATTEMPTS ]]; do
  if run_once; then
    log "Success"
    exit 0
  fi
  rc=$?
  if [[ $rc -eq 2 ]]; then
    log "Waiting for manual agent (set AGENT_DONE=1 to continue)"
    exit 0
  fi
  ATTEMPT=$((ATTEMPT + 1))
  log "Attempt failed, retrying..."
  sleep 30
done

alert_verifiers
exit 1
