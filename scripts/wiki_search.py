#!/usr/bin/env python3
"""Simple search over wiki/ markdown pages."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = REPO_ROOT / "wiki"


def parse_frontmatter_tags(text: str) -> list[str]:
    if not text.startswith("---"):
        return []
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    tags: list[str] = []
    in_tags = False
    for line in parts[1].splitlines():
        if line.strip().startswith("tags:"):
            in_tags = True
            inline = line.split("tags:", 1)[1].strip()
            if inline.startswith("["):
                tags.extend(re.findall(r"[\w-]+", inline))
                in_tags = False
            continue
        if in_tags:
            if line.startswith("  - "):
                tags.append(line.strip().lstrip("- ").strip())
            else:
                in_tags = False
    return tags


def search_pages(query: str, tags: list[str] | None = None) -> list[tuple[Path, int, str]]:
    if not WIKI_DIR.is_dir():
        return []
    terms = [t.lower() for t in query.split() if t.strip()]
    tag_set = {t.lower() for t in (tags or [])}
    results: list[tuple[Path, int, str]] = []

    for path in sorted(WIKI_DIR.rglob("*.md")):
        if path.name in {"index.md", "log.md"}:
            continue
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        page_tags = {t.lower() for t in parse_frontmatter_tags(text)}

        if tag_set and not tag_set.intersection(page_tags):
            continue

        score = 0
        for term in terms:
            score += lower.count(term)
        if terms and score == 0:
            continue
        if not terms and not tag_set:
            score = 1

        title = path.stem
        for line in text.splitlines()[:20]:
            if line.startswith("# "):
                title = line[2:].strip()
                break
        results.append((path, score, title))

    results.sort(key=lambda item: (-item[1], str(item[0])))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Search agents-unite wiki pages.")
    parser.add_argument("query", nargs="?", default="", help="Search terms")
    parser.add_argument("--tags", help="Comma-separated frontmatter tags")
    parser.add_argument("-n", type=int, default=15, help="Max results")
    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
    results = search_pages(args.query, tags)[: args.n]

    if not results:
        print("No matching wiki pages.")
        return 0

    for path, score, title in results:
        rel = path.relative_to(REPO_ROOT)
        print(f"{score:3d}  {rel}  —  {title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
