"""Contributor generators.

`rule` is deterministic and needs no key. The others speak HTTP or a local
process. `auto` picks the first configured provider, then `rule`.

Secret names (GitHub Actions secrets or environment variables):

- OPENROUTER_API_KEY: OpenRouter. Model SIM_OPENROUTER_MODEL (default openrouter/free).
- GROQ_API_KEY: Groq. Model SIM_GROQ_MODEL (default llama-3.1-8b-instant).
- GEMINI_API_KEY or GOOGLE_API_KEY: Gemini. Model SIM_GEMINI_MODEL (default gemini-2.0-flash).
- HF_TOKEN or HUGGINGFACE_API_KEY: Hugging Face router. Model SIM_HF_MODEL.
- OLLAMA_HOST: local Ollama. No key. Model SIM_OLLAMA_MODEL (default llama3.2).
- LLAMA_CPP_MODEL: GGUF path for llama.cpp. Binary LLAMA_CPP_BIN (default llama-cli).

A missing key selects `rule`. A configured provider that errors is recorded
and that attempt falls back to `rule`.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass
class Completion:
    provider: str
    model: str
    text: str
    prompt_tokens: int | None
    completion_tokens: int | None
    latency_ms: float
    cost_usd: float | None
    error: str
    fell_back: bool


class RuleProvider:
    name = "rule"
    model = "rule"

    def available(self) -> bool:
        return True

    def complete(self, system: str, user: str) -> Completion:
        return Completion(
            provider=self.name,
            model=self.model,
            text="",
            prompt_tokens=0,
            completion_tokens=0,
            latency_ms=0.0,
            cost_usd=0.0,
            error="",
            fell_back=False,
        )


def _cost(model: str, prompt_tokens: int | None, completion_tokens: int | None) -> float | None:
    """Only free models get a numeric zero. Other prices stay unknown."""
    if model in {"rule", "openrouter/free"} or model.endswith(":free"):
        return 0.0
    return None


def _post_json(url: str, payload: dict, headers: dict[str, str], timeout: float = 45.0) -> tuple[dict, float]:
    started = time.perf_counter()
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body, (time.perf_counter() - started) * 1000.0


class _OpenAIChat:
    name = ""
    default_model = ""
    env_key = ""
    model_env = ""
    url = ""

    def model_name(self) -> str:
        return os.environ.get(self.model_env, self.default_model)

    def available(self) -> bool:
        return bool(os.environ.get(self.env_key))

    def complete(self, system: str, user: str) -> Completion:
        model = self.model_name()
        started = time.perf_counter()
        try:
            body, latency = _post_json(
                self.url,
                {
                    "model": model,
                    "temperature": 0,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                },
                {"Authorization": f"Bearer {os.environ[self.env_key]}"},
            )
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            return Completion(
                provider=self.name,
                model=model,
                text="",
                prompt_tokens=None,
                completion_tokens=None,
                latency_ms=(time.perf_counter() - started) * 1000.0,
                cost_usd=None,
                error=f"{type(exc).__name__}: {exc}",
                fell_back=True,
            )
        choice = ((body.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
        usage = body.get("usage") or {}
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        return Completion(
            provider=self.name,
            model=model,
            text=str(choice),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency,
            cost_usd=_cost(model, prompt_tokens, completion_tokens),
            error="",
            fell_back=False,
        )


class OpenRouterProvider(_OpenAIChat):
    name = "openrouter"
    default_model = "openrouter/free"
    env_key = "OPENROUTER_API_KEY"
    model_env = "SIM_OPENROUTER_MODEL"
    url = "https://openrouter.ai/api/v1/chat/completions"


class GroqProvider(_OpenAIChat):
    name = "groq"
    default_model = "llama-3.1-8b-instant"
    env_key = "GROQ_API_KEY"
    model_env = "SIM_GROQ_MODEL"
    url = "https://api.groq.com/openai/v1/chat/completions"


class HuggingFaceProvider(_OpenAIChat):
    name = "huggingface"
    default_model = "Qwen/Qwen2.5-7B-Instruct"
    env_key = "HF_TOKEN"
    model_env = "SIM_HF_MODEL"
    url = "https://router.huggingface.co/v1/chat/completions"

    def available(self) -> bool:
        return bool(os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY"))

    def complete(self, system: str, user: str) -> Completion:
        token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY") or ""
        os.environ["HF_TOKEN"] = token
        return super().complete(system, user)


class GeminiProvider:
    name = "gemini"
    default_model = "gemini-2.0-flash"

    def model_name(self) -> str:
        return os.environ.get("SIM_GEMINI_MODEL", self.default_model)

    def available(self) -> bool:
        return bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))

    def complete(self, system: str, user: str) -> Completion:
        model = self.model_name()
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        started = time.perf_counter()
        try:
            body, latency = _post_json(
                url,
                {"contents": [{"parts": [{"text": system + "\n\n" + user}]}]},
                {},
            )
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            return Completion(
                provider=self.name,
                model=model,
                text="",
                prompt_tokens=None,
                completion_tokens=None,
                latency_ms=(time.perf_counter() - started) * 1000.0,
                cost_usd=None,
                error=f"{type(exc).__name__}: {exc}",
                fell_back=True,
            )
        parts = (((body.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [{}])
        text = str(parts[0].get("text") or "") if parts else ""
        usage = body.get("usageMetadata") or {}
        return Completion(
            provider=self.name,
            model=model,
            text=text,
            prompt_tokens=usage.get("promptTokenCount"),
            completion_tokens=usage.get("candidatesTokenCount"),
            latency_ms=latency,
            cost_usd=_cost(model, None, None),
            error="",
            fell_back=False,
        )


class OllamaProvider:
    name = "ollama"

    def model_name(self) -> str:
        return os.environ.get("SIM_OLLAMA_MODEL", "llama3.2")

    def host(self) -> str:
        return os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")

    def available(self) -> bool:
        if os.environ.get("SIM_ENABLE_OLLAMA") != "1":
            return False
        try:
            with urllib.request.urlopen(self.host() + "/api/tags", timeout=2) as response:
                return response.status == 200
        except (urllib.error.URLError, TimeoutError):
            return False

    def complete(self, system: str, user: str) -> Completion:
        model = self.model_name()
        started = time.perf_counter()
        try:
            body, latency = _post_json(
                self.host() + "/api/chat",
                {
                    "model": model,
                    "stream": False,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                },
                {},
            )
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            return Completion(
                provider=self.name,
                model=model,
                text="",
                prompt_tokens=None,
                completion_tokens=None,
                latency_ms=(time.perf_counter() - started) * 1000.0,
                cost_usd=0.0,
                error=f"{type(exc).__name__}: {exc}",
                fell_back=True,
            )
        text = str((body.get("message") or {}).get("content") or "")
        return Completion(
            provider=self.name,
            model=model,
            text=text,
            prompt_tokens=None,
            completion_tokens=None,
            latency_ms=latency,
            cost_usd=0.0,
            error="",
            fell_back=False,
        )


class LlamaCppProvider:
    name = "llamacpp"

    def available(self) -> bool:
        model = os.environ.get("LLAMA_CPP_MODEL")
        binary = os.environ.get("LLAMA_CPP_BIN", "llama-cli")
        return bool(model and Path_exists(model) and shutil.which(binary))

    def complete(self, system: str, user: str) -> Completion:
        model = os.environ.get("LLAMA_CPP_MODEL", "")
        binary = os.environ.get("LLAMA_CPP_BIN", "llama-cli")
        started = time.perf_counter()
        try:
            result = subprocess.run(
                [binary, "-m", model, "-p", system + "\n\n" + user, "-n", "256", "--no-display-prompt"],
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return Completion(
                provider=self.name,
                model=model,
                text="",
                prompt_tokens=None,
                completion_tokens=None,
                latency_ms=(time.perf_counter() - started) * 1000.0,
                cost_usd=0.0,
                error=f"{type(exc).__name__}: {exc}",
                fell_back=True,
            )
        if result.returncode != 0:
            return Completion(
                provider=self.name,
                model=model,
                text="",
                prompt_tokens=None,
                completion_tokens=None,
                latency_ms=(time.perf_counter() - started) * 1000.0,
                cost_usd=0.0,
                error=result.stderr[-400:],
                fell_back=True,
            )
        return Completion(
            provider=self.name,
            model=model,
            text=result.stdout,
            prompt_tokens=None,
            completion_tokens=None,
            latency_ms=(time.perf_counter() - started) * 1000.0,
            cost_usd=0.0,
            error="",
            fell_back=False,
        )


def Path_exists(path: str) -> bool:
    from pathlib import Path

    return Path(path).is_file()


PROVIDERS = {
    "rule": RuleProvider,
    "openrouter": OpenRouterProvider,
    "groq": GroqProvider,
    "huggingface": HuggingFaceProvider,
    "gemini": GeminiProvider,
    "ollama": OllamaProvider,
    "llamacpp": LlamaCppProvider,
}
AUTO_ORDER = (
    OpenRouterProvider,
    GroqProvider,
    GeminiProvider,
    HuggingFaceProvider,
    OllamaProvider,
    LlamaCppProvider,
)


def select_provider(name: str):
    if name == "auto":
        for cls in AUTO_ORDER:
            provider = cls()
            if provider.available():
                return provider
        return RuleProvider()
    cls = PROVIDERS.get(name)
    if cls is None:
        raise ValueError(f"unknown provider {name!r}")
    provider = cls()
    if name != "rule" and not provider.available():
        return RuleProvider()
    return provider


def parse_model_score(text: str) -> float | None:
    """Pull a sentiment_score from a model reply. None when the reply is unusable."""
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            payload = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict) and "sentiment_score" in payload:
            try:
                score = float(payload["sentiment_score"])
            except (TypeError, ValueError):
                return None
            if -1.0 <= score <= 1.0:
                return score
    return None
