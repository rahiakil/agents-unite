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


def shell(title: str, body: str, *, active: str = "home", desc: str = "") -> str:
    meta = desc or title
    nav = [
        ("home", "Home", "index.html"),
        ("story", "Story", "story.html"),
        ("series", "Series", "series.html"),
        ("join", "Join", "join.html"),
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
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="logo" href="index.html">agents<span>-unite</span></a>
      <nav>{nav_html}</nav>
      <a class="btn btn-sm" href="{REPO_URL}">⭐ Star on GitHub</a>
    </div>
  </header>
  <main class="wrap main-content">
    {body}
  </main>
  <footer class="site-footer">
    <div class="wrap">
      <p><strong>Markets change. Memory compounds.</strong></p>
      <p>
        <a href="{REPO_URL}">GitHub repo</a> ·
        <a href="{REPO_URL}/blob/main/docs/HARNESS.md">Harness docs</a> ·
        MIT · Not investment advice
      </p>
    </div>
  </footer>
</body>
</html>"""


def build_index(published: dict) -> str:
    index_gist = published.get("index_url", "")
    body = f"""
<section class="hero">
  <p class="eyebrow">Open source · Crowdsourced · Agentic</p>
  <h1>Building the World's Financial Memory</h1>
  <p class="lead">Millions run LLM stock research alone and close the tab. We turn one ticker per day into permanent Git history — crowd-researched sentiment the whole market can read.</p>
  <div class="hero-cta">
    <a class="btn btn-primary" href="join.html">Join in 5 minutes</a>
    <a class="btn btn-secondary" href="{REPO_URL}">View repository</a>
  </div>
  <p class="hero-sub">~25¢ of tokens on your ticker · thousands of tickers from everyone · compounding on Git</p>
</section>

<section class="grid-3">
  <article class="card">
    <h3>The problem</h3>
    <p>Solo LLM research burns budget and misses timezones. Work stays private. History vanishes.</p>
  </article>
  <article class="card">
    <h3>The swap</h3>
    <p>One repo, many agents. You research one assigned ticker. Everyone reads the growing <code>data/</code> archive.</p>
  </article>
  <article class="card">
    <h3>The moat</h3>
    <p>Not the code — <strong>history</strong>. Years of labeled sentiment with sources. Fork it. Backtest it. Train on it.</p>
  </article>
</section>

<section>
  <h2>How it works</h2>
  <div class="pipeline">
    <div class="step"><span>1</span><strong>Assign</strong><p>One ticker · one role · one day</p></div>
    <div class="arrow">→</div>
    <div class="step"><span>2</span><strong>Research</strong><p>Cursor · OpenAI · CrewAI · Swarm</p></div>
    <div class="arrow">→</div>
    <div class="step"><span>3</span><strong>Verify</strong><p>Distributed audit layer</p></div>
    <div class="arrow">→</div>
    <div class="step"><span>4</span><strong>Consensus</strong><p>Weighted median signal</p></div>
    <div class="arrow">→</div>
    <div class="step"><span>5</span><strong>PR</strong><p>Permanent commit in <code>data/</code></p></div>
  </div>
</section>

<section>
  <h2>Git is the ledger</h2>
  <p>Every report is a commit. Verifiers are validators. Consensus is finality. Immutable prompts and CI guards — blockchain-like coordination without a coin.</p>
  <p><a href="story.html">Read the full story →</a></p>
</section>

<section>
  <h2>Market AI series</h2>
  <p>15 short essays on crowdsourced market AI — also on <a href="{index_gist}">GitHub Gists</a>.</p>
  <ul class="series-list">
"""
    for i, g in enumerate(published.get("gists", []), 1):
        title = g.get("description", g.get("file", "")).split("—", 1)[-1].strip()
        body += f'    <li><a href="articles/{i:02d}.html">{html.escape(title)}</a></li>\n'
    body += f"""  </ul>
  <p><a href="series.html">Browse all articles →</a></p>
</section>

<section class="cta-block">
  <h2>Run one ticker today</h2>
  <pre><code>git clone {REPO_URL}.git
cd agents-unite && ./scripts/setup.sh</code></pre>
  <a class="btn btn-primary" href="join.html">Setup guide</a>
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


def build_article(num: int, md_path: Path, published_entry: dict) -> str:
    content = md_to_html(md_path.read_text(encoding="utf-8"))
    desc = published_entry.get("description", md_path.stem)
    gist = published_entry.get("url", "")
    nav_prev = f"articles/{num-1:02d}.html" if num > 1 else None
    nav_next = f"articles/{num+1:02d}.html" if num < 15 else None
    nav = '<nav class="article-nav">'
    if nav_prev:
        nav += f'<a href="{nav_prev}">← Previous</a>'
    nav += '<a href="series.html">Index</a>'
    if nav_next:
        nav += f'<a href="{nav_next}">Next →</a>'
    nav += "</nav>"
    extra = f'<p class="meta"><a href="{gist}">View on GitHub Gist</a> · <a href="{REPO_URL}">Star the repo</a></p>'
    body = nav + f'<article class="prose">{content}</article>' + extra + nav
    return shell(desc, body, active="series", desc=desc)


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
    for i, entry in enumerate(gists, 1):
        md = GISTS / entry["file"]
        if md.is_file():
            (OUT / "articles" / f"{i:02d}.html").write_text(build_article(i, md, entry), encoding="utf-8")

    print(f"Built {OUT} ({len(list(OUT.rglob('*')))} files)")


if __name__ == "__main__":
    main()
