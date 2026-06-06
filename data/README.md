# Daily Sentiment Data

This directory holds the collective sentiment archive. Each contributor adds one folder per day.

## Layout

```
data/
├── YYYY-MM-DD/
│   └── TICKER/
│       ├── report.md       # Structured sentiment report (required)
│       └── sources.json    # Twitter, Reddit, news links (required)
└── _index/
    └── summary-YYYY-MM-DD.md   # Auto-generated daily rollup
```

## Adding a report

```bash
./scripts/run-agent.sh          # get your assignment
# ... agent writes report.md + sources.json ...
python3 scripts/validate_report.py data/YYYY-MM-DD/TICKER/
./scripts/commit-report.sh
```

## Reading the data

```bash
python3 scripts/stats.py                    # coverage, averages, top movers
python3 scripts/aggregate.py --date DATE    # daily summary table
cat data/_index/summary-2026-06-05.md       # example rollup
```

## Rules

- **One report per contributor per day** — assignment is deterministic
- **One folder per ticker per day** — do not overwrite others' work
- **Real sources only** — no placeholder URLs in merged reports
- **Demo data** in `2026-06-05/` is illustrative; new reports use today's date

## Future (Phase 2+)

```
data/YYYY-MM-DD/TICKER/HH/     # hourly intraday updates
data/YYYY-MM-DD/TICKER/consensus.md   # reconciled canonical score
```
