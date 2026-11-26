#!/usr/bin/env bash
# Append one study day to the sim-data branch.
# The process exits non-zero when the harness check fails or the push fails.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PROVIDER="${SIM_PROVIDER:-auto}"
LLM_CAP="${SIM_LLM_CAP:-11}"
REMOTE="${SIM_REMOTE:-origin}"
AUTHOR_EMAIL="${GIT_AUTHOR_EMAIL:-github-actions[bot]@users.noreply.github.com}"
AUTHOR_NAME="${GIT_AUTHOR_NAME:-github-actions[bot]}"
OUT="${SIM_DAILY_OUT:-${RUNNER_TEMP:-/tmp}/sim-daily-out}"

git fetch "$REMOTE" "sim-data:refs/remotes/${REMOTE}/sim-data" || true

WORK="$(mktemp -d)"
mkdir -p "$OUT"
cleanup() {
  git worktree remove --force "$WORK" >/dev/null 2>&1 || true
  git worktree prune >/dev/null 2>&1 || true
  rm -rf "$WORK"
}
trap cleanup EXIT

if git rev-parse --verify "refs/remotes/${REMOTE}/sim-data" >/dev/null 2>&1; then
  git worktree add "$WORK" "refs/remotes/${REMOTE}/sim-data"
  git -C "$WORK" checkout -B sim-data
else
  git worktree add --detach "$WORK" HEAD
  git -C "$WORK" checkout --orphan sim-data
  git -C "$WORK" rm -rf . >/dev/null 2>&1 || true
fi

python3 -m sim --daily \
  --history "$WORK/history" \
  --provider "$PROVIDER" \
  --llm-cap "$LLM_CAP" \
  --check \
  --outdir "$OUT"
python3 -m sim.learnings --history "$WORK/history" --every 15

git -C "$WORK" add history
if git -C "$WORK" diff --cached --quiet; then
  echo "sim-daily: no new archive files" >&2
  exit 1
fi
git -C "$WORK" -c user.email="$AUTHOR_EMAIL" -c user.name="$AUTHOR_NAME" commit -m "sim: append $(date -u +%Y-%m-%d)"
git -C "$WORK" push "$REMOTE" HEAD:sim-data
echo "sim-daily: pushed sim-data"
