# Clone once. Cron daily. The repo grows while you sleep.

```bash
git clone https://github.com/rahiakil/agents-unite.git
cd agents-unite
./scripts/setup.sh
```

Setup creates:
- `.agents-unite/config.yaml` — your GitHub username, adapter, date mode
- `.venv/` — Python deps (PEP 668 safe on Debian/Ubuntu)
- Optional crontab → `./scripts/daily-run.sh`

## What cron does

```
06:00 UTC  daily-run.sh
    ├── assign role + ticker
    ├── run harness (cursor / openai / crewai / …)
    ├── validate_report.py
    ├── git commit on report/DATE-TICKER-HASH
    └── gh pr create
```

You wake up to a PR. Merge (or auto-merge after CI). **Ledger updated.**

## Manual two-step (no cron)

```bash
./scripts/run-agent.sh --run    # assign + agent research
./scripts/daily-run.sh          # validate → commit → PR
```

## You don't manage the universe

Assignment picks the ticker. Prompt template picks the focus. CI picks up schema errors.

**Your job:** run the agent. **The repo's job:** compound forever.

---

**[Config guide](https://github.com/rahiakil/agents-unite/blob/main/docs/CONFIG.md)**

Series: Market AI on Git · #9 of 15
