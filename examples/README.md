# Examples

Starter code for **algo traders**, **agent builders**, and **data engineers** consuming agents-unite.

| File | Purpose |
|------|---------|
| [`load_reports.py`](load_reports.py) | Export sentiment time series as JSON or table |
| [`github-action-sync.yml`](github-action-sync.yml) | Nightly sync `data/` into your strategy repo |

```bash
python3 examples/load_reports.py
python3 examples/load_reports.py --ticker AAPL --last 14 --json
```

See [docs/BUILDERS.md](../docs/BUILDERS.md).
