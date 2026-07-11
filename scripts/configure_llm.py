#!/usr/bin/env python3
"""Interactive LLM / adapter setup after pip install."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from au_common import load_yaml_config  # noqa: E402

CONFIG_DIR = REPO_ROOT / ".agents-unite"
CONFIG_PATH = CONFIG_DIR / "config.yaml"
CRON_ENV_PATH = CONFIG_DIR / "cron.env"
EXAMPLE = REPO_ROOT / "config" / "config.example.yaml"
CRON_EXAMPLE = REPO_ROOT / "config" / "cron.env.example"

PROFILES = {
    "1": {
        "label": "Ollama (local, free — no API key)",
        "fields": {
            "agent_adapter": "llm",
            "llm_provider": "ollama",
            "llm_model": "gemma4:latest",
            "llm_base_url": "http://127.0.0.1:11434/v1",
            "web_search": "true",
        },
    },
    "2": {
        "label": "OpenAI / compatible API (gpt-4o-mini)",
        "fields": {
            "agent_adapter": "llm",
            "llm_provider": "openai_compatible",
            "llm_model": "gpt-4o-mini",
            "llm_api_key_env": "OPENAI_API_KEY",
            "web_search": "true",
        },
        "key_env": "OPENAI_API_KEY",
    },
    "3": {
        "label": "OpenRouter / other OpenAI-compatible endpoint",
        "fields": {
            "agent_adapter": "llm",
            "llm_provider": "openai_compatible",
            "llm_model": "openai/gpt-4o-mini",
            "llm_api_key_env": "OPENAI_API_KEY",
            "web_search": "true",
        },
        "key_env": "OPENAI_API_KEY",
        "ask_base_url": True,
    },
    "4": {
        "label": "Cursor CLI (uses your Cursor login)",
        "fields": {"agent_adapter": "cursor", "agent_runtime": "cursor"},
    },
    "5": {
        "label": "Manual — paste prompt into any external agent",
        "fields": {"agent_adapter": "manual", "agent_runtime": "manual"},
    },
}


def _ensure_config() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.is_file() and EXAMPLE.is_file():
        CONFIG_PATH.write_text(EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    if not CRON_ENV_PATH.is_file() and CRON_EXAMPLE.is_file():
        CRON_ENV_PATH.write_text(CRON_EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")


def _update_yaml(fields: dict[str, str]) -> None:
    lines = CONFIG_PATH.read_text(encoding="utf-8").splitlines()
    keys = set(fields)
    out: list[str] = []
    seen: set[str] = set()
    for line in lines:
        key = line.split(":", 1)[0].strip() if ":" in line and not line.strip().startswith("#") else ""
        if key in keys:
            out.append(f"{key}: {fields[key]}")
            seen.add(key)
        else:
            out.append(line)
    for key, val in fields.items():
        if key not in seen:
            out.append(f"{key}: {val}")
    CONFIG_PATH.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def _append_cron_env(key: str, value: str) -> None:
    text = CRON_ENV_PATH.read_text(encoding="utf-8") if CRON_ENV_PATH.is_file() else ""
    lines = [ln for ln in text.splitlines() if not ln.startswith(f"{key}=")]
    lines.append(f"{key}={value}")
    CRON_ENV_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def run_interactive() -> int:
    _ensure_config()
    cfg = load_yaml_config()
    user = cfg.get("github_username", "your-github-username")
    print("agents-unite — configure LLM & adapter")
    print(f"Config: {CONFIG_PATH}  (gitignored)\n")
    if user == "your-github-username":
        gh = input("GitHub username (for reports/PRs): ").strip()
        if gh:
            _update_yaml({"github_username": gh})

    print("Choose your agent / LLM:\n")
    for k, p in PROFILES.items():
        print(f"  {k}) {p['label']}")
    print()
    choice = input("Choice [1]: ").strip() or "1"
    profile = PROFILES.get(choice, PROFILES["1"])
    fields = dict(profile["fields"])

    if profile.get("ask_base_url"):
        url = input("OpenAI-compatible base URL (e.g. https://openrouter.ai/api/v1): ").strip()
        if url:
            fields["llm_base_url"] = url

    model = input(f"Model [{fields.get('llm_model', 'default')}]: ").strip()
    if model and "llm_model" in fields:
        fields["llm_model"] = model

    _update_yaml(fields)

    key_env = profile.get("key_env")
    if key_env:
        print(f"\nAPI key for {key_env}:")
        print("  • Session only:  export OPENAI_API_KEY=sk-...")
        print(f"  • Cron / daily: add to {CRON_ENV_PATH}")
        key = input(f"Paste {key_env} now (leave blank to set later): ").strip()
        if key:
            _append_cron_env(key_env, key)
            print(f"Saved to {CRON_ENV_PATH}")

    print("\nDone. Test with:")
    print("  agents-unite research NVDA --dry-run")
    print("  agents-unite research NVDA")
    print("  agents-unite daily")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Configure LLM provider and API keys after pip install.")
    parser.add_argument("--non-interactive", action="store_true", help="Print options only")
    args = parser.parse_args()
    if args.non_interactive:
        print("Run: agents-unite configure")
        print("Or edit .agents-unite/config.yaml — see docs/INSTALL.md")
        return 0
    return run_interactive()


if __name__ == "__main__":
    raise SystemExit(main())
