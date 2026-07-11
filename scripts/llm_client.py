#!/usr/bin/env python3
"""Minimal LLM client (stdlib urllib — OpenAI-compatible + Anthropic)."""

from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.request
from typing import Any


class LLMError(RuntimeError):
    pass


def chat_completion(
    *,
    provider: str,
    model: str,
    api_key: str | None,
    base_url: str,
    messages: list[dict[str, str]],
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> str:
    provider = provider.lower()
    if provider == "anthropic":
        return _anthropic_chat(model, api_key, messages, temperature, max_tokens)
    return _openai_compatible_chat(model, api_key, base_url, messages, temperature, max_tokens)


def _request_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: int | None = None) -> dict:
    if timeout is None:
        timeout = int(os.environ.get("AGENTS_UNITE_LLM_TIMEOUT", "180"))
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise LLMError(f"HTTP {exc.code}: {detail[:500]}") from exc
    except urllib.error.URLError as exc:
        raise LLMError(f"Network error: {exc}") from exc


def _openai_compatible_chat(
    model: str,
    api_key: str | None,
    base_url: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> str:
    if not base_url:
        base_url = "https://api.openai.com/v1"
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    data = _request_json(url, headers, payload)
    try:
        return str(data["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError(f"Unexpected response shape: {data!r}") from exc


def _anthropic_chat(
    model: str,
    api_key: str | None,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> str:
    if not api_key:
        raise LLMError("Anthropic requires API key (ANTHROPIC_API_KEY)")

    system_parts = [m["content"] for m in messages if m.get("role") == "system"]
    user_messages = [m for m in messages if m.get("role") != "system"]
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": "\n\n".join(system_parts) if system_parts else "",
        "messages": [{"role": m["role"], "content": m["content"]} for m in user_messages if m["role"] in ("user", "assistant")],
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    data = _request_json("https://api.anthropic.com/v1/messages", headers, payload)
    try:
        parts = data.get("content") or []
        texts = [p.get("text", "") for p in parts if p.get("type") == "text"]
        return "\n".join(t for t in texts if t)
    except (KeyError, TypeError) as exc:
        raise LLMError(f"Unexpected Anthropic response: {data!r}") from exc
