# Contributing to agents-unite

Thank you for helping build **the world's financial memory** — a distributed, open stock research ledger.

**Contributors:** one agent, one ticker, one PR per day.  
**Builders:** fork data, ship backtests, bots, dashboards — see [docs/BUILDERS.md](docs/BUILDERS.md) and [examples/](examples/).

## Quick start

```bash
git clone https://github.com/<org>/agents-unite.git
cd agents-unite

# Optional: stable identity across machines
export AGENTS_UNITE_CONTRIBUTOR="you@example.com"

# 1. Get your assignment and agent prompt
python scripts/run_investigation.py --scaffold --metadata

# 2. Run your AI agent with the printed prompt (Cursor, Codex, Claude, etc.)
#    Agent writes to data/YYYY-MM-DD/TICKER/report.md and sources.json

# 3. Validate before committing
python scripts/validate_report.py data/$(date -u +%Y-%m-%d)/$(python scripts/assign_ticker.py)/
python scripts/generate_readme.py   # refresh live README stats

# 4. Commit and open a PR
git checkout -b report/$(date -u +%Y-%m-%d)-TICKER
git add data/
git commit -m "Add sentiment report for TICKER on YYYY-MM-DD"
git push -u origin HEAD
```

Replace `TICKER` and `YYYY-MM-DD` with your assignment output.

## How assignment works

Ticker assignment is **deterministic**:

```
SHA256("{date}:{contributor_hash}") % active_ticker_count → your ticker
```

- **Same person + same day → same ticker** everywhere in the world.
- Contributor identity resolves in order:
  1. `--contributor` flag
  2. `AGENTS_UNITE_CONTRIBUTOR` env var
  3. `git config user.email`
  4. `anonymous` (not recommended — collides with other anonymous users)

Verify your assignment:

```bash
python scripts/assign_ticker.py --json
```

## What to submit

Each investigation produces exactly two files:

```
data/YYYY-MM-DD/TICKER/
├── report.md      # Structured sentiment report
└── sources.json   # URLs and metadata
```

### Report requirements

- YAML frontmatter with `ticker`, `date`, `sentiment_score`, `contributor_hash`
- Sections: **Sentiment**, **Key Themes**, **Sources**, **Price Snapshot**, **Notable Events**
- Sentiment score between **-1.0** and **+1.0**
- Minimum substance (~200 characters); no placeholder URLs in final output

### Sources requirements

- Valid JSON with `ticker`, `date`, `sources[]`
- Each source: `type` (`twitter` | `reddit` | `news` | `other`), `url`, `title`
- At least one real source (aim for 3+ across 2+ types)

## Rules

1. **One report per contributor per day** — your path is determined by assignment; do not pick a ticker manually.
2. **Do not overwrite others' reports** — one folder per ticker per day; if taken, your assignment still points you elsewhere.
3. **No trading advice** — sentiment collection only. See [docs/TRADING.md](docs/TRADING.md) for future gating.
4. **Real sources only** — link to actual posts/articles you referenced.
5. **Validate locally** — CI will reject malformed reports.

## Expanding the ticker universe

The seed list in `tickers/universe.json` supports growth to 4000+ symbols. To add tickers:

1. Add entries following the existing schema (`ticker`, `name`, `exchange`, `sector`, `active`).
2. Keep tickers **unique** and **uppercase**.
3. Set `"active": false` to retire symbols without breaking history.
4. Open a PR titled `tickers: add <SYMBOL>` — no daily report required.

## Agent prompt

The canonical prompt template is [`agents/investigation.md`](agents/investigation.md). `run_investigation.py` fills in `{{TICKER}}`, `{{DATE}}`, and output paths.

Design goals:

- **Token-efficient** — structured extraction, not 10-page research memos
- **Open-ended** — agent chooses how to search, but must hit the schema
- **Git-friendly** — one directory per ticker per day, easy to diff and review

## CI

Pull requests that touch `data/**` run [`.github/workflows/validate-report.yml`](.github/workflows/validate-report.yml). Fix validation errors before merge.

## Code contributions

- Python 3.10+; scripts use stdlib only (see `requirements.txt`).
- Match existing style; keep scripts runnable from repo root.
- Architecture details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Questions

Open a GitHub issue with the `question` label. For consensus/trading future work, see [docs/CONSENSUS.md](docs/CONSENSUS.md) and [docs/TRADING.md](docs/TRADING.md).
