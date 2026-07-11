"""Locate the agents-unite repository root."""

from __future__ import annotations

import os
from pathlib import Path


def repo_root(start: Path | None = None) -> Path:
    """Return repo root containing tickers/universe.json (or scripts/assign_role.py)."""
    env = os.environ.get("AGENTS_UNITE_ROOT", "").strip()
    if env:
        root = Path(env).expanduser().resolve()
        if _looks_like_repo(root):
            return root
        raise SystemExit(f"AGENTS_UNITE_ROOT is not an agents-unite repo: {root}")

    start = (start or Path.cwd()).resolve()
    for candidate in [start, *start.parents]:
        if _looks_like_repo(candidate):
            return candidate

    raise SystemExit(
        "Not inside an agents-unite checkout.\n"
        "  git clone https://github.com/rahiakil/agents-unite.git\n"
        "  cd agents-unite\n"
        "  pip install -e '.[llm]'\n"
        "Or set AGENTS_UNITE_ROOT=/path/to/agents-unite"
    )


def _looks_like_repo(path: Path) -> bool:
    return (path / "tickers" / "universe.json").is_file() or (
        (path / "scripts" / "assign_role.py").is_file() and (path / "agents").is_dir()
    )


def script_path(root: Path, name: str) -> Path:
    path = root / "scripts" / name
    if not path.is_file():
        raise SystemExit(f"Missing script: {path}")
    return path
