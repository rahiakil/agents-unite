#!/usr/bin/env python3
"""Web search for agent harness — feeds LLM real URLs, not HTML dumps."""

from __future__ import annotations

import json
import os
import ssl
import urllib.parse
import urllib.request
from typing import Any


def search(query: str, *, provider: str = "duckduckgo", max_results: int = 8) -> list[dict[str, str]]:
    provider = (provider or "duckduckgo").lower()
    if provider == "none":
        return []
    if provider == "tavily":
        return _tavily_search(query, max_results=max_results)
    return _duckduckgo_search(query, max_results=max_results)


def format_for_prompt(results: list[dict[str, str]]) -> str:
    if not results:
        return "No web search results available. Use only URLs you can verify from search."
    lines = ["## Web search results (use these URLs in sources.json)\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. [{r.get('type', 'other')}] {r.get('title', '')}")
        lines.append(f"   URL: {r.get('url', '')}")
        if r.get("snippet"):
            lines.append(f"   Snippet: {r['snippet'][:300]}")
    return "\n".join(lines)


def _duckduckgo_search(query: str, max_results: int) -> list[dict[str, str]]:
    ddgs_cls = None
    try:
        from ddgs import DDGS as DDGSNew  # type: ignore

        ddgs_cls = DDGSNew
    except ImportError:
        try:
            from duckduckgo_search import DDGS as DDGSOld  # type: ignore

            ddgs_cls = DDGSOld
        except ImportError:
            return []

    out: list[dict[str, str]] = []
    try:
        with ddgs_cls() as ddgs:
            for item in ddgs.text(query, max_results=max_results):
                url = item.get("href") or item.get("url") or ""
                if not url:
                    continue
                stype = _guess_source_type(url)
                out.append(
                    {
                        "type": stype,
                        "url": url,
                        "title": item.get("title") or "",
                        "snippet": item.get("body") or item.get("snippet") or "",
                    }
                )
    except Exception:
        return out
    return out


def _tavily_search(query: str, max_results: int) -> list[dict[str, str]]:
    key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not key:
        return []
    payload = json.dumps({"api_key": key, "query": query, "max_results": max_results}).encode()
    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return []

    out: list[dict[str, str]] = []
    for item in data.get("results") or []:
        url = item.get("url") or ""
        if not url:
            continue
        out.append(
            {
                "type": _guess_source_type(url),
                "url": url,
                "title": item.get("title") or "",
                "snippet": item.get("content") or "",
            }
        )
    return out


def _guess_source_type(url: str) -> str:
    host = urllib.parse.urlparse(url).netloc.lower()
    if "reddit.com" in host:
        return "reddit"
    if "twitter.com" in host or "x.com" in host:
        return "twitter"
    if any(x in host for x in ("reuters", "bloomberg", "cnbc", "wsj", "ft.com", "news", "finance.yahoo")):
        return "news"
    return "other"
