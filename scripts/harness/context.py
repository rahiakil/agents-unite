from __future__ import annotations

from pathlib import Path

from harness.paths import REPO_ROOT


def build_search_query(meta: dict) -> str:
    role = meta.get("daily_role", "research")
    ticker = meta.get("ticker", "")
    date = meta.get("date", "")
    focus = meta.get("focus", "full")
    if role in ("patterns", "findings"):
        return f"stock market breaking news {date} sector themes"
    if role == "verify":
        return f"{ticker} stock news reddit twitter {date}"
    if role == "consensus":
        return f"{ticker} stock sentiment {date}"
    focus_hint = {
        "social": "reddit twitter",
        "news": "news earnings",
        "trading": "price volume",
        "sentiment": "sentiment",
    }.get(focus, "")
    return f"{ticker} stock {focus_hint} {date} market"


def gather_folder_context(output_dir: Path) -> str:
    if not output_dir.is_dir():
        return ""
    chunks: list[str] = []
    for path in sorted(output_dir.glob("*")):
        if path.suffix in (".md", ".json") and path.is_file():
            text = path.read_text(encoding="utf-8")
            if len(text) > 12000:
                text = text[:12000] + "\n... [truncated]"
            chunks.append(f"### {path.name}\n{text}")
    return "\n\n".join(chunks)


def build_user_content(meta: dict, prompt: str, cfg: dict) -> str:
    import sys

    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from agent_config import llm_settings  # noqa: WPS433
    from web_search import format_for_prompt, search  # noqa: WPS433

    settings = llm_settings(cfg)
    user_content = prompt
    if settings["web_search"] and meta.get("daily_role") in (
        "research",
        "submitter",
        "verify",
        "consensus",
        "patterns",
        "findings",
    ):
        q = build_search_query(meta)
        results = search(q, provider=settings["web_search_provider"])
        search_block = format_for_prompt(results)
        if search_block:
            user_content = f"{search_block}\n\n---\n\n{prompt}"

    context = gather_folder_context(REPO_ROOT / meta.get("output_dir", ""))
    if context:
        user_content = f"## Existing files in output folder\n\n{context}\n\n---\n\n{user_content}"
    return user_content
