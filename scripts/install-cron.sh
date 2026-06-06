#!/usr/bin/env bash
# One-command installer: config + cron entry for daily-run.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$REPO_ROOT/.agents-unite"
CONFIG_FILE="$CONFIG_DIR/config.yaml"
EXAMPLE="$REPO_ROOT/config/config.example.yaml"

mkdir -p "$CONFIG_DIR"

if [[ ! -f "$CONFIG_FILE" ]]; then
  cp "$EXAMPLE" "$CONFIG_FILE"
  echo "Created $CONFIG_FILE — edit github_username and settings."
else
  echo "Config exists: $CONFIG_FILE"
fi

# Ensure gitignore
grep -qxF '.agents-unite/' "$REPO_ROOT/.gitignore" 2>/dev/null || echo '.agents-unite/' >> "$REPO_ROOT/.gitignore"

echo ""
echo "=== Configuration ==="
echo "  date_mode:       utc_midnight | us_close"
echo "  detail_level:    minimal | standard | deep"
echo "  verifier_opt_in: true/false (random verifier days)"
echo "  agent_runtime:   cursor | hermes | openclaw | manual"
echo ""

read -r -p "GitHub username: " GH_USER || true
if [[ -n "${GH_USER:-}" ]]; then
  sed -i "s/your-github-username/$GH_USER/" "$CONFIG_FILE" 2>/dev/null || \
    python3 -c "
from pathlib import Path
p=Path('$CONFIG_FILE')
t=p.read_text().replace('your-github-username','$GH_USER')
p.write_text(t)
"
fi

read -r -p "Date mode [utc_midnight]: " DATE_MODE || true
DATE_MODE="${DATE_MODE:-utc_midnight}"

read -r -p "Detail level [standard]: " DETAIL || true
DETAIL="${DETAIL:-standard}"

read -r -p "Opt in to verifier pool? [y/N]: " VERIFIER || true
VERIFIER_OPT="false"
[[ "${VERIFIER:-}" =~ ^[Yy] ]] && VERIFIER_OPT="true"

read -r -p "Cron schedule [0 6 * * *]: " SCHEDULE || true
SCHEDULE="${SCHEDULE:-0 6 * * *}"

chmod +x "$REPO_ROOT/scripts/daily-run.sh"

CRON_LINE="$SCHEDULE cd $REPO_ROOT && ./scripts/daily-run.sh >> $CONFIG_DIR/cron.log 2>&1"

echo ""
echo "Add this crontab line:"
echo "  $CRON_LINE"
echo ""
read -r -p "Install crontab now? [y/N]: " INSTALL || true
if [[ "${INSTALL:-}" =~ ^[Yy] ]]; then
  (crontab -l 2>/dev/null | grep -v "agents-unite/scripts/daily-run" || true; echo "$CRON_LINE") | crontab -
  echo "Crontab installed."
fi

echo ""
echo "Prerequisites:"
echo "  - gh auth login (for auto-PR)"
echo "  - export GH_TOKEN or set github_token_env in config"
echo "  - Set agent_command in config when ready for full automation"
echo ""
echo "Test: ./scripts/daily-run.sh"
