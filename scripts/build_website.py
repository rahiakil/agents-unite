#!/usr/bin/env python3
"""Build static GitHub Pages site from gists/ and website templates."""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GISTS = REPO_ROOT / "gists"
WEBSITE = REPO_ROOT / "website"
OUT = WEBSITE / "_site"
PUBLISHED = GISTS / "published.json"
REPO_URL = "https://github.com/rahiakil/agents-unite"
SITE_URL = "https://rahiakil.github.io/agents-unite"


def rel(href: str, depth: int = 0) -> str:
    """Resolve href relative to page depth (0 = site root, 1 = articles/)."""
    if depth <= 0 or href.startswith(("http://", "https://", "//", "#")):
        return href
    return ("../" * depth) + href


def md_to_html(text: str) -> str:
    """Minimal markdown → HTML (headings, links, code, lists, paragraphs)."""
    lines = text.splitlines()
    out: list[str] = []
    in_code = False
    in_ul = False
    in_table = False
    table_rows: list[str] = []

    def flush_table() -> None:
        nonlocal in_table, table_rows
        if not table_rows:
            return
        out.append('<table class="data-table">')
        for i, row in enumerate(table_rows):
            cells = [c.strip() for c in row.strip("|").split("|")]
            tag = "th" if i == 0 else "td"
            out.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells) + "</tr>")
        out.append("</table>")
        table_rows = []
        in_table = False

    def inline(s: str) -> str:
        s = html.escape(s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
        return s

    for line in lines:
        if line.strip().startswith("```"):
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                if in_ul:
                    out.append("</ul>")
                    in_ul = False
                flush_table()
                lang = line.strip()[3:].strip()
                cls = f' class="language-{lang}"' if lang else ""
                out.append(f"<pre><code{cls}>")
                in_code = True
            continue
        if in_code:
            out.append(html.escape(line))
            continue
        if line.startswith("|") and "|" in line[1:]:
            if not in_table:
                if in_ul:
                    out.append("</ul>")
                    in_ul = False
                in_table = True
            if re.match(r"^\|[\s\-:|]+\|$", line.strip()):
                continue
            table_rows.append(line)
            continue
        if in_table:
            flush_table()
        if line.startswith("# "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.startswith("## "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("### "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline(line[2:])}</li>")
        elif line.strip() == "---":
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append("<hr>")
        elif line.strip() == "":
            if in_ul:
                out.append("</ul>")
                in_ul = False
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<p>{inline(line)}</p>")

    if in_ul:
        out.append("</ul>")
    if in_code:
        out.append("</code></pre>")
    flush_table()
    return "\n".join(out)


def shell(
    title: str,
    body: str,
    *,
    active: str = "home",
    desc: str = "",
    depth: int = 0,
    extra_head: str = "",
) -> str:
    meta = desc or title
    nav = [
        ("home", "Home", rel("index.html", depth)),
        ("story", "Story", rel("story.html", depth)),
        ("series", "Series", rel("series.html", depth)),
        ("join", "Join", rel("join.html", depth)),
    ]
    nav_html = "".join(
        f'<a href="{href}" class="nav-link{" active" if key == active else ""}">{label}</a>'
        for key, label, href in nav
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} · agents-unite</title>
  <meta name="description" content="{html.escape(meta)}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(meta)}">
  <meta property="og:type" content="website">
  <link rel="stylesheet" href="{rel("assets/style.css", depth)}">
  {extra_head}
</head>
<body>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="logo" href="{rel("index.html", depth)}">~/agents-unite</a>
      <nav>{nav_html}</nav>
      <a class="btn-sm" href="{REPO_URL}">star the repo on github →</a>
    </div>
  </header>
  <main class="wrap main-content">
    {body}
  </main>
  <footer class="site-footer">
    <div class="wrap">
      <p><strong>Markets change. Memory compounds.</strong> (not investment advice)</p>
      <p>
        <a href="{REPO_URL}">github repo</a> ·
        <a href="{REPO_URL}/blob/main/docs/HARNESS.md">harness docs</a> ·
        mit license
      </p>
    </div>
  </footer>
</body>
</html>"""


def load_all_series() -> list[dict]:
    """Load published.json from each gist series directory."""
    series: list[dict] = []
    for sub in ("", "research", "gating", "adrs"):
        path = GISTS / sub / "published.json" if sub else PUBLISHED
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            data.setdefault("series", sub or "market-ai")
            series.append(data)
    return series


def build_index(published: dict) -> str:
    index_gist = published.get("index_url", "")
    all_series = load_all_series()
    body = f"""
<section class="hero">
  <p class="eyebrow">side project · one github repo · many people's agents</p>
  <h1>Building the World's Financial Memory</h1>
  <p class="lead">Millions run LLM stock research alone and close the tab. This repo saves one ticker per day as permanent Git history — crowd-researched sentiment anyone can fork.</p>
  <div class="hero-cta">
    <a class="btn btn-primary" href="join.html">how to join</a>
    <a class="btn btn-secondary" href="{REPO_URL}">view on github</a>
  </div>
  <p class="hero-sub">you spend ~25¢ on your ticker. everyone else's agents fill in the rest. data/ keeps growing.</p>
</section>

<section class="grid-3">
  <article class="card">
    <h3>the problem</h3>
    <p>Solo LLM research burns budget and misses timezones. Work stays private. History vanishes.</p>
  </article>
  <article class="card">
    <h3>the swap</h3>
    <p>One repo, many agents. You get one assigned ticker. Everyone reads the growing <code>data/</code> folder.</p>
  </article>
  <article class="card">
    <h3>the moat</h3>
    <p>Not the code — <strong>history</strong>. Years of sentiment with sources attached. Fork it, backtest it, train on it.</p>
  </article>
</section>

<section>
  <h2>How it works</h2>
  <div class="pipeline">
    <div class="step"><span>1.</span><strong>Assign</strong><p>one ticker, one role, one day</p></div>
    <div class="step"><span>2.</span><strong>Research</strong><p>cursor, openai, crewai, whatever you run</p></div>
    <div class="step"><span>3.</span><strong>Verify</strong><p>someone audits URLs and claims</p></div>
    <div class="step"><span>4.</span><strong>Consensus</strong><p>weighted median when multiple reports exist</p></div>
    <div class="step"><span>5.</span><strong>PR</strong><p>merged into <code>data/</code> forever</p></div>
  </div>
</section>

<section>
  <h2>Git is the ledger</h2>
  <p>Every report is a commit. Verifiers check the work. Consensus picks a canonical view. Prompts are locked — you can't silently change the rules in your PR.</p>
  <p><a href="story.html">read the longer version →</a></p>
</section>

<section>
  <h2>Gist series</h2>
  <p>Short essays mirrored as <a href="{index_gist}">GitHub gists</a> — shareable without cloning the repo.</p>
  <div class="series-catalog">
"""
    for s in all_series:
        title = s.get("series_title", s.get("series", "Series"))
        url = s.get("index_url", "")
        n = len(s.get("gists", []))
        if url:
            body += f'    <a class="series-chip" href="{url}">{html.escape(title)} <span class="chip-count">{n}</span></a>\n'
    body += """  </div>
</section>

<section>
  <h2>Market AI essays</h2>
  <p>15 short write-ups on the website. <a href="series.html">Full list →</a></p>
  <ol class="series-list">
"""
    for i, g in enumerate(published.get("gists", []), 1):
        title = g.get("description", g.get("file", "")).split("—", 1)[-1].strip()
        body += f'    <li><a href="articles/{i:02d}.html">{html.escape(title)}</a></li>\n'
    body += """  </ol>
</section>

<section class="cta-block">
  <h2>Try it</h2>
  <pre><code>git clone {REPO_URL}.git
cd agents-unite && ./scripts/setup.sh</code></pre>
  <a class="btn btn-primary" href="join.html">setup notes</a>
</section>
"""
    return shell(
        "Building the World's Financial Memory",
        body,
        active="home",
        desc="Crowdsource agentic LLM market research in one Git repo. Spend cents on one ticker; read thousands for free.",
    )


def build_join() -> str:
    body = """
<h1>Join agents-unite</h1>
<p class="lead">Clone once. Cron daily. The repo grows while you sleep.</p>

<h2>Quick start</h2>
<pre><code>git clone https://github.com/rahiakil/agents-unite.git
cd agents-unite
./scripts/setup.sh</code></pre>

<p>Setup picks your harness (OpenAI, Cursor, CrewAI, Swarm, Hermes, OpenClaw), creates a local <code>.venv</code>, and optionally installs cron.</p>

<h2>Test run</h2>
<pre><code>export OPENAI_API_KEY=sk-...   # openai / auto / crewai / swarm
./scripts/run-agent.sh --run
./scripts/daily-run.sh</code></pre>

<h2>Daily automation</h2>
<p>Cron runs <code>./scripts/daily-run.sh</code>:</p>
<ol>
  <li>Assign role + ticker</li>
  <li>Run your agent harness</li>
  <li>Validate schema + sources</li>
  <li>Commit + open PR</li>
</ol>

<h2>What you contribute vs receive</h2>
<table class="data-table">
<tr><th>You spend</th><th>Everyone gets</th></tr>
<tr><td>~25¢ tokens/day</td><td>Growing <code>data/</code> archive</td></tr>
<tr><td>One ticker</td><td>Thousands over time</td></tr>
<tr><td>One PR</td><td>Git history anyone can fork</td></tr>
</table>

<p><a class="btn btn-primary" href="https://github.com/rahiakil/agents-unite">⭐ Star the repository</a></p>
"""
    return shell("Join", body, active="join", desc="Setup agents-unite in five minutes.")


def build_story() -> str:
    body = """
<h1>The story</h1>

<h2>Millions research alone. Nobody publishes.</h2>
<p>Every day people ask LLMs about NVDA, scan Reddit for TSLA, summarize earnings — then close the tab. No archive. No version history. The work is ephemeral.</p>

<h2>You cannot cover the market solo</h2>
<p>~4,000 tickers × ~25¢ each = thousands of dollars per day. Plus timing: Asia open while you sleep, after-hours filings after your cron ran. One timezone always loses.</p>

<h2>Crowdsource in one repo</h2>
<p>Each contributor: one assigned ticker, one day, one PR. Different harnesses worldwide — Cursor, CrewAI, OpenAI, Swarm, Hermes. The crowd splits the token bill and the clock.</p>

<h2>127 posts, one ledger</h2>
<p>127 contributors researching 127 tickers = 127 permanent artifacts in <code>data/</code>, verifiable and mergeable into consensus. Nobody burned tokens on all 127 alone.</p>

<h2>Pipeline, not chat</h2>
<p>Research → verify → consensus. Verifiers audit URLs and claims like network validators. Consensus uses weighted median, not vibes. Raw reports stay forever.</p>

<h2>What compounds</h2>
<p>Today: sentiment pulse. Tomorrow: longitudinal dataset for backtests, RAG, fine-tunes, reputation scoring. How you use <code>data/</code> is yours. Maintenance is crowdsourced.</p>

<p><a href="join.html">Join now →</a> · <a href="series.html">Read the 15-part series →</a></p>
"""
    return shell("Story", body, active="story", desc="Why crowdsourced market AI on Git beats solo LLM research.")


def build_series_index(published: dict) -> str:
    body = "<h1>Market AI on Git</h1><p class=\"lead\">15 essays on crowdsourced agentic market research.</p><div class=\"article-grid\">\n"
    for i, g in enumerate(published.get("gists", []), 1):
        desc = g.get("description", "")
        title = desc.split("—", 1)[-1].strip() if "—" in desc else desc
        gist_url = g.get("url", "")
        body += f"""<article class="card card-link">
  <span class="num">#{i}</span>
  <h3><a href="articles/{i:02d}.html">{html.escape(title)}</a></h3>
  <p><a href="{gist_url}">Gist</a> · <a href="articles/{i:02d}.html">Read on site</a></p>
</article>\n"""
    body += "</div>"
    index_url = published.get("index_url", "")
    if index_url:
        body += f'<p class="meta">Master index gist: <a href="{index_url}">{index_url}</a></p>'
    return shell("Series", body, active="series", desc="15-part Market AI essay series.")


def article_nav(num: int, total: int, *, depth: int = 1) -> str:
    nav_prev = f"{num - 1:02d}.html" if num > 1 else None
    nav_next = f"{num + 1:02d}.html" if num < total else None
    series_href = rel("series.html", depth)
    parts = ['<nav class="article-nav" aria-label="Article navigation">']
    if nav_prev:
        parts.append(f'<a class="nav-btn nav-prev" href="{nav_prev}"><span class="nav-label">Previous</span><span class="nav-arrow">←</span></a>')
    else:
        parts.append('<span class="nav-spacer"></span>')
    parts.append(f'<a class="nav-index" href="{series_href}">#{num} of {total}</a>')
    if nav_next:
        parts.append(f'<a class="nav-btn nav-next" href="{nav_next}"><span class="nav-label">Next</span><span class="nav-arrow">→</span></a>')
    else:
        parts.append('<span class="nav-spacer"></span>')
    parts.append("</nav>")
    return "".join(parts)


def build_article(num: int, md_path: Path, published_entry: dict, total: int) -> str:
    content = md_to_html(md_path.read_text(encoding="utf-8"))
    desc = published_entry.get("description", md_path.stem)
    gist = published_entry.get("url", "")
    title_short = desc.split("—", 1)[-1].strip() if "—" in desc else desc
    pct = round(100 * num / total)
    progress = (
        f'<div class="series-progress" role="progressbar" aria-valuenow="{num}" '
        f'aria-valuemin="1" aria-valuemax="{total}" aria-label="Series progress">'
        f'<div class="series-progress-fill" style="width:{pct}%"></div></div>'
    )
    hero = f"""<header class="article-hero">
  <p class="article-eyebrow">Market AI on Git · essay {num}</p>
  <div class="article-badge">{num:02d}</div>
  {progress}
  <h1 class="article-title">{html.escape(title_short)}</h1>
</header>"""
    nav_top = article_nav(num, total, depth=1)
    nav_bottom = article_nav(num, total, depth=1)
    extra = (
        f'<aside class="article-footer">'
        f'<a class="btn btn-secondary" href="{gist}">Read on GitHub Gist</a> '
        f'<a class="btn btn-primary" href="{REPO_URL}">Star the repo</a>'
        f"</aside>"
    )
    body = nav_top + hero + f'<article class="prose article-body">{content}</article>' + extra + nav_bottom
    return shell(desc, body, active="series", desc=desc, depth=1)


def main() -> None:
    published = json.loads(PUBLISHED.read_text(encoding="utf-8")) if PUBLISHED.is_file() else {"gists": []}

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "assets").mkdir()
    (OUT / "articles").mkdir()

    shutil.copy(WEBSITE / "assets" / "style.css", OUT / "assets" / "style.css")

    (OUT / "index.html").write_text(build_index(published), encoding="utf-8")
    (OUT / "join.html").write_text(build_join(), encoding="utf-8")
    (OUT / "story.html").write_text(build_story(), encoding="utf-8")
    (OUT / "series.html").write_text(build_series_index(published), encoding="utf-8")

    gists = published.get("gists", [])
    total = len(gists)
    for i, entry in enumerate(gists, 1):
        md = GISTS / entry["file"]
        if md.is_file():
            (OUT / "articles" / f"{i:02d}.html").write_text(
                build_article(i, md, entry, total), encoding="utf-8"
            )

    print(f"Built {OUT} ({len(list(OUT.rglob('*')))} files)")


if __name__ == "__main__":
    main()
