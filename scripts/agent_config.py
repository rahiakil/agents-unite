#!/usr/bin/env python3
"""LLM and adapter settings from config + environment."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

import sys

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from au_common import load_yaml_config  # noqa: E402


def _env(name: str) -> str | None:
    val = os.environ.get(name)
    return val.strip() if val and val.strip() else None


def llm_settings(cfg: dict | None = None) -> dict:
    cfg = cfg if cfg is not None else load_yaml_config()
    provider = str(cfg.get("llm_provider", "openai_compatible")).strip().lower()
    model = str(cfg.get("llm_model", "gpt-4o-mini")).strip()
    key_env = str(cfg.get("llm_api_key_env", "OPENAI_API_KEY")).strip()
    base_url = str(cfg.get("llm_base_url", "") or "").strip()

    if provider == "ollama" and not base_url:
        base_url = "http://127.0.0.1:11434/v1"

    if provider == "anthropic":
        key_env = str(cfg.get("llm_api_key_env", "ANTHROPIC_API_KEY")).strip()
        if not model or model == "gpt-4o-mini":
            model = str(cfg.get("llm_model", "claude-sonnet-4-20250514")).strip()

    api_key = _env(key_env)
    if not api_key and provider in ("openai", "openai_compatible"):
        api_key = _env("OPENAI_API_KEY")
    if not api_key and provider == "anthropic":
        api_key = _env("ANTHROPIC_API_KEY")

    return {
        "provider": provider,
        "model": model,
        "api_key": api_key,
        "api_key_env": key_env,
        "base_url": base_url.rstrip("/") if base_url else "",
        "temperature": float(cfg.get("llm_temperature", 0.3)),
        "max_tokens": int(cfg.get("llm_max_tokens", 4096)),
        "web_search": bool(cfg.get("web_search", True)),
        "web_search_provider": str(cfg.get("web_search_provider", "duckduckgo")).lower(),
        "tavily_api_key_env": str(cfg.get("tavily_api_key_env", "TAVILY_API_KEY")),
    }


def llm_configured(cfg: dict | None = None) -> bool:
    s = llm_settings(cfg)
    if s["provider"] == "ollama":
        return bool(s["base_url"])
    return bool(s["api_key"])


def resolve_agent_command(cfg: dict | None = None) -> str | None:
    """Command for daily-run to execute, or None for manual mode."""
    cfg = cfg if cfg is not None else load_yaml_config()
    explicit = str(cfg.get("agent_command", "") or "").strip()
    if explicit:
        return explicit

    adapter = str(cfg.get("agent_adapter", "auto")).strip().lower()
    repo = REPO_ROOT

    if adapter == "manual":
        return None
    if adapter == "llm":
        return f"python3 {repo / 'scripts' / 'run_agent.py'}"
    if adapter == "cursor":
        return f"bash {repo / 'scripts' / 'adapters' / 'cursor.sh'}"
    if adapter == "hermes":
        return f"bash {repo / 'scripts' / 'adapters' / 'hermes.sh'}"
    if adapter == "openclaw":
        return f"bash {repo / 'scripts' / 'adapters' / 'openclaw.sh'}"

    # auto: prefer built-in LLM harness when keys exist
    if llm_configured(cfg):
        return f"python3 {repo / 'scripts' / 'run_agent.py'}"
    return None
