# Website (GitHub Pages)

Marketing site built from `gists/` and deployed automatically.

## Build locally

```bash
python3 scripts/build_website.py
# open website/_site/index.html
```

## Deploy

Push to `main` — [`.github/workflows/pages.yml`](../.github/workflows/pages.yml) builds and deploys.

Live: **https://rahiakil.github.io/agents-unite/**

## Pages

| Path | Content |
|------|---------|
| `/` | Landing — hero, pipeline, CTA |
| `/story.html` | Full narrative |
| `/series.html` | 15-part Market AI index |
| `/join.html` | Setup guide |
| `/articles/01.html` … `15.html` | Individual essays (from gists) |
