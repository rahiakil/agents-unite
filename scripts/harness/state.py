from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from harness.paths import REPO_ROOT, STATE_DIR


def load_meta(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    if "--- PROMPT ---" in raw:
        raw = raw.split("--- PROMPT ---", 1)[0]
    return json.loads(raw.strip())


def load_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assign_and_scaffold() -> tuple[dict, str]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "run_investigation.py"), "--scaffold", "--metadata"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "run_investigation failed")

    raw = proc.stdout
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    meta_path = STATE_DIR / "run-meta.json"
    meta_path.write_text(raw, encoding="utf-8")

    if "--- PROMPT ---" in raw:
        meta_text, prompt = raw.split("--- PROMPT ---", 1)
    else:
        meta_text, prompt = raw, ""
    prompt = prompt.lstrip()
    (STATE_DIR / "prompt.md").write_text(prompt, encoding="utf-8")
    return json.loads(meta_text.strip()), prompt


def resolve_state(meta_path: Path | None, prompt_path: Path | None) -> tuple[dict, str]:
    meta_file = meta_path or STATE_DIR / "run-meta.json"
    prompt_file = prompt_path or STATE_DIR / "prompt.md"
    if not meta_file.is_file() or not prompt_file.is_file():
        raise FileNotFoundError("run ./scripts/run-agent.sh first or use --assign")
    return load_meta(meta_file), load_prompt(prompt_file)
