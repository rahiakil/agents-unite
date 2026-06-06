# User Configuration

Copy [`config/config.example.yaml`](../config/config.example.yaml) to `.agents-unite/config.yaml` (gitignored).

Install:

```bash
./scripts/install-cron.sh
```

## Fields

| Key | Values | Description |
|-----|--------|-------------|
| `github_username` | string | **Required** for reputation and report filenames |
| `date_mode` | `utc_midnight` \| `us_close` | Folder date for `data/YYYY-MM-DD/` |
| `verifier_opt_in` | bool | If true, ~25% of days you are randomly a verifier |
| `detail_level` | `minimal` \| `standard` \| `deep` | Token budget hint in prompts |
| `agent_runtime` | string | Informational label (cursor, hermes, openclaw, manual) |
| `agent_command` | shell | Optional full automation command |
| `schedule` | cron | Used by install-cron.sh |
| `auto_pr` | bool | Open PR via `gh` after success |
| `retry_on_failure` | bool | Retry once, then alert verifiers |

## Date modes

**utc_midnight** — `data/` folder uses UTC calendar date. Good for global contributors.

**us_close** — folder uses US equity session date (America/New_York). Good for US traders waking up to "today's market."

## Verifier opt-in

When `verifier_opt_in: true`:

- You do **not** know until cron runs whether today is submitter or verifier
- Prompt is chosen by `scripts/assign_role.py` from `agents/`
- Verifier writes `consensus.md` in assigned ticker folder

## Automation levels

1. **Manual** (default): cron saves prompt → you paste into agent → `AGENT_DONE=1 ./scripts/daily-run.sh`
2. **Semi-auto**: set `agent_command` to your CLI
3. **Full-auto**: agent_command + gh auth + validate + PR

## Environment

```bash
export GH_TOKEN=...          # for gh pr create
export AGENTS_UNITE_CONTRIBUTOR=github-username  # optional override
export AGENTS_UNITE_DATE_MODE=us_close
```

See [VISION.md](VISION.md), [TRUST.md](TRUST.md).
