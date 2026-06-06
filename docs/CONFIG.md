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
export GH_TOKEN=...          # for gh pr create (see below)
export AGENTS_UNITE_CONTRIBUTOR=github-username  # optional override
export AGENTS_UNITE_DATE_MODE=us_close
```

## GitHub authentication (`gh auth login` vs token)

**Who needs it:** only the machine that **pushes branches and opens PRs** — your laptop, homelab, or cron host. Not every reader of the repo.

| Action | Needs GitHub auth? | How |
|--------|-------------------|-----|
| Clone repo, run agent, write report locally | No | — |
| `git push` to your report branch | Yes | SSH key or HTTPS credential |
| `gh pr create` (auto-PR from cron) | Yes | `gh auth login` **or** `GH_TOKEN` |
| CI validation on GitHub | No (for you) | Runs in GitHub Actions with `GITHUB_TOKEN` automatically |
| Merge PR | Maintainer | GitHub UI or maintainer token |

### Option A — interactive (dev machine)

```bash
gh auth login
```

Stores credentials in `~/.config/gh/`. Used by `daily-run.sh` when `auto_pr: true`.

### Option B — headless (cron / server)

Create a fine-grained PAT at GitHub → Settings → Developer settings → **Tokens**, with:

- Repository access: this repo only
- Permissions: **Contents** (read/write), **Pull requests** (read/write)

Then in cron or `.agents-unite/config.yaml` environment:

```bash
export GH_TOKEN=github_pat_...
# optional: config references github_token_env: GH_TOKEN
```

Never commit the token. `.agents-unite/` is gitignored.

### What runs without auth

- `assign_role.py`, `run-agent.sh`, validation, local commits on `report/DATE-TICKER-HASH`
- You can always `git push -u origin report/...` with SSH/HTTPS alone and open the PR in the browser

### What needs auth

- `gh pr create`, `gh issue create` (verifier alerts), `gh api user` (auto-detect username)

If `auto_pr: false`, cron can skip `gh` entirely — push branch manually or with deploy key.

See [VISION.md](VISION.md), [TRUST.md](TRUST.md).
