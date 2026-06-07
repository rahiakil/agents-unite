---
name: website-gist-cleanup
description: Maintain agents-unite GitHub Pages site and gist series after content changes. Use when editing gists/, website/, article HTML, publish scripts, or when the user asks to fix prev/next navigation, refresh gist indexes, or sync README links.
---

# Website & Gist Cleanup

Keep the marketing site, gist series, and README links in sync.

## When to run

After changing any of:

- `gists/**/*.md` or `gists/**/manifest.yaml`
- `website/assets/style.css`
- `scripts/build_website.py` or `scripts/publish_gists.py`
- README "Spread the idea" links

## Checklist

1. **Relative paths** — Article pages live at `articles/NN.html` (depth 1). Prev/next must be `12.html` / `14.html`, not `articles/12.html`. Site nav and CSS use `../` from article pages.

2. **Rebuild site**
   ```bash
   python3 scripts/build_website.py
   ```
   Verify `website/_site/articles/13.html` links: `12.html`, `14.html`, `../series.html`, `../assets/style.css`.

3. **Publish gists** (requires `gh auth login`)
   ```bash
   ./scripts/publish-gists.sh --series research   # or gating, adrs, market-ai
   ./scripts/publish-gists.sh --series market-ai --index-only  # refresh index without duplicating posts
   ./scripts/publish-gists.sh --all             # full republish all series
   ```

4. **Update links**
   - `gists/SERIES.md` — auto-written by `--all`
   - `README.md` — "Spread the idea" row with gist index URLs
   - `gists/README.md` — series table

5. **Push triggers Pages** — workflow `.github/workflows/pages.yml` deploys on push to `main` when `website/`, `gists/`, or `scripts/build_website.py` change.

## Series layout

| Series | Dir | Manifest |
|--------|-----|----------|
| Market AI | `gists/` | `gists/manifest.yaml` |
| Research | `gists/research/` | `gists/research/manifest.yaml` |
| Gating | `gists/gating/` | `gists/gating/manifest.yaml` |
| ADRs | `gists/adrs/` | `gists/adrs/manifest.yaml` |

Each series has `published.json` and `INDEX.md` with gist URLs.

## Common bugs

- **Double `/articles/articles/`** — prev/next used root-relative `articles/NN.html` from inside `articles/`.
- **Broken CSS on articles** — `href="assets/style.css"` should be `../assets/style.css`.
- **Duplicate gists** — Re-running `--series market-ai` creates new gists; use `--index-only` to refresh the index.

## Do not

- Remove README live markers (`<!-- LIVE:*:START/END -->`)
- Commit placeholder gist URLs — run publish first or keep existing `published.json`
