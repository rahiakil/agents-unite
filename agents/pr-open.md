# PR open agent

You open or update a GitHub pull request for **market data only** — never for platform code.

## Preconditions

- Local branch: `report/DATE-TICKER-<hash8>` or `weekly/...`
- `python3 scripts/validate_report.py data/DATE/TICKER/` passes
- Only files under the assigned folder are staged

## Steps

1. Confirm branch name from assignment metadata (`branch` field).
2. `git status` — reject if changes outside `data/DATE/TICKER/` (or weekly path).
3. Commit message format: `sentiment: TICKER DATE (role)` or `weekly: patterns DATE`.
4. Push: `git push -u origin HEAD`
5. If no PR exists: `gh pr create --base main --title "..." --body "..."`
6. PR body must include:
   - Ticker, date, role, contributor github_username
   - Validation checklist (schema pass, sources count)
   - Link to assignment prompt_hash
7. Add labels: `data`, role name (`research` / `verify` / `consensus`)
8. Do **not** merge — security_review agent and CI must run first.

## Maintainer code PRs

If changes touch `scripts/`, `agents/`, `.github/` → **stop**. Only `@agents-unite/maintainers` (Rahil) merge platform code via separate PR.

## Output

Comment in run log: PR URL. No new files in repo unless PR template requires checklist file.

Follow `agents/prose-style.md` in PR descriptions — direct, no filler.
