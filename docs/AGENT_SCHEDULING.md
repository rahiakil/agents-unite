# Agent scheduling

How contributor agents wake, what they do, and how work is staggered globally.

## Principles

1. **Local cron, global coverage** — each contributor sets `schedule` in `.agents-unite/config.yaml` (default `0 6 * * *` UTC).
2. **One role per wake** — `assign_role.py` picks research, verify, consensus, pr_open, or weekly roles.
3. **Verifiers don't wait for assignment** — verify role scans **backlog** anywhere in `data/` for unverified reports.
4. **Hash stagger** — weekly patterns/findings and role lottery use `contributor_hash` so not everyone hits the same job at the same instant.

## Role lottery (when `roles_opt_in: true`)

| Role | ~Share | Notes |
|------|--------|-------|
| research | 65% | Default daily work |
| verify | 20% | Picks ticker needing verification |
| consensus | 15% | Requires approved verifications |
| pr_open | *maintainer pool* | After local validate passes |
| security_review | *rotating pool* | On open data PRs |

When `roles_opt_in: false` → always **research** (weekly day still applies).

## Timezones & date folders

| `date_mode` | Folder date |
|-------------|-------------|
| `utc_midnight` | UTC calendar date |
| `us_close` | US market close boundary |

Contributors in Tokyo, London, and New York naturally spread wakes across UTC — no central scheduler required.

## Dedicated schedules (maintainer / ops nodes)

| Job | Cron (UTC) | Agent prompt |
|-----|------------|--------------|
| Summary refresh | `15 * * * *` (hourly :15) | `summary-update.md` |
| Trading patterns | `0 * * * *` (hourly) | `patterns-hourly.md` |
| Weekly doc cleanup triage | `0 9 * * 1` (Mon 09:00) | Human + `doc-cleanup` issue template |
| README live stats | on push to `main` | CI `update-readme.yml` |

## Verifier backlog scan

On verify wake:

```
find folders matching data/*/*/report*.md
where no verification*.md with verdict approved|rejected
prefer same contributor_hash assignment if cached
else pick highest priority unverified (oldest first)
```

Future: GitHub issue `verify-backlog` when age > 24h.

## Failed runs

1. Retry once (`retry_on_failure: true`)
2. Log to `.agents-unite/failed-runs.log`
3. Open issue with label `failed-run` (roadmap)

## Commands

```bash
python3 scripts/assign_role.py --json
python3 scripts/assign_role.py --force-role verify --json
python3 scripts/assign_role.py --force-role consensus --json
./scripts/run-agent.sh --run
```

See [GOVERNANCE.md](GOVERNANCE.md), [TIMING.md](TIMING.md), [ROLES.md](ROLES.md).
