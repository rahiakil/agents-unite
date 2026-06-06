# CLAUDE.md — Agents Unite

Instructions for Claude Code, Cursor, and other AI agents working in this repository.

## Project purpose

**agents-unite** is a distributed stock market sentiment ledger. Contributors run one agent per day, investigate one assigned ticker, and commit structured reports to GitHub.

## When you change data

After editing or adding files under `data/YYYY-MM-DD/TICKER/`:

1. Run `python3 scripts/validate_report.py data/YYYY-MM-DD/TICKER/`
2. Run `python3 scripts/generate_readme.py` to refresh live README sections
3. Optionally run `python3 scripts/aggregate.py --date YYYY-MM-DD`

On push to `main`, CI (`.github/workflows/update-readme.yml`) automatically regenerates:

- Live stats table in README
- Market pulse leaderboard
- Coverage tracker
- Daily index summaries in `data/_index/`

**Keep the README interesting:** when adding features or changing schema, update both the static README prose and ensure `scripts/generate_readme.py` still produces compelling live output.

## Second brain (LLM Wiki)

**Deferred:** active wiki ingestion starts after a few days of live contributor data. Scaffold exists:

- [`WIKI.md`](WIKI.md), [`wiki/`](wiki/) — Karpathy pattern ready
- Manual: `python3 scripts/wiki_ingest.py --prompt`

Do not auto-ingest until data shape stabilizes. See [raw/DECISIONS.md](raw/DECISIONS.md).

```bash
python3 scripts/wiki_ingest.py              # pending raw → wiki
python3 scripts/wiki_ingest.py --prompt     # agent prompt for next ingest
python3 scripts/wiki_search.py "NVDA trend"   # search compiled knowledge
```

- **Schema:** [`WIKI.md`](WIKI.md) — how the LLM maintains `wiki/`
- **Index:** [`wiki/index.md`](wiki/index.md)
- **Pattern:** [Karpathy LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

Raw reports stay in `data/` (immutable). The wiki synthesizes trends, themes, and cross-ticker links.

## Standard workflow

```bash
./scripts/install-cron.sh          # once: config + crontab
./scripts/run-agent.sh             # or ./scripts/daily-run.sh from cron
# Agent fills data/DATE/TICKER/report.<user>.md (or consensus.md if verifier)
python3 scripts/validate_report.py data/DATE/TICKER/
python3 scripts/generate_readme.py
./scripts/commit-report.sh
```

New reports require `prompt_hash`, `prompt_file`, `github_username`, `daily_role`, `focus` in frontmatter.

## Report requirements

- YAML frontmatter: `ticker`, `date`, `github_username`, `contributor_hash`, `sentiment_score`, `prompt_hash`, `prompt_file`, `daily_role`, `focus`
- Files: `report.<github-slug>.md` + `sources.<slug>.json` OR `consensus.md` for verifiers
- H1 sections: Sentiment, Key Themes, Sources, Price Snapshot, Notable Events
- `sources.json`: types must be `twitter`, `reddit`, `news`, or `other`
- Sentiment score: −1.0 to +1.0 based on social/news tone
- No trading advice

## Key files

| File | Role |
|------|------|
| `agents/investigation.md` | Canonical agent prompt template |
| `scripts/run_investigation.py` | Assignment + prompt rendering |
| `scripts/generate_readme.py` | Live README regeneration |
| `WIKI.md` | LLM wiki maintainer schema |
| `wiki/` | Second brain — compiled sentiment knowledge |
| `scripts/wiki_ingest.py` | Track pending raw → wiki ingests |
| `tickers/universe.json` | Ticker universe for assignment |

## Do not

- Pick your own ticker — use assignment from `run-agent.sh`
- Overwrite existing reports for the same date/ticker
- Remove README live markers (`<!-- LIVE:HEADER_STATS:START -->` etc.)
- Commit placeholder URLs in final reports

## Architecture docs

- [docs/VISION.md](docs/VISION.md) — product vision (locked decisions)
- [docs/CONFIG.md](docs/CONFIG.md) — user config / cron install
- [docs/TRUST.md](docs/TRUST.md) — governance, path guard, prompt provenance
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/CONSENSUS.md](docs/CONSENSUS.md) — verifier / consensus
- [docs/TRADING.md](docs/TRADING.md) — future reputation gating
