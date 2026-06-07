#!/usr/bin/env python3
"""Publish gists/ series to GitHub via gh CLI."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GISTS_DIR = REPO_ROOT / "gists"
MANIFEST = GISTS_DIR / "manifest.yaml"
PUBLISHED = GISTS_DIR / "published.json"


def load_manifest() -> dict:
    try:
        import yaml
    except ImportError:
        print("error: pyyaml required. Run: ./scripts/ensure-venv.sh llm", file=sys.stderr)
        sys.exit(1)
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))


def gh_available() -> bool:
    try:
        subprocess.run(["gh", "auth", "status"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def create_gist(path: Path, description: str, public: bool, dry_run: bool) -> dict | None:
    if not path.is_file():
        print(f"skip missing: {path.name}", file=sys.stderr)
        return None
    cmd = [
        "gh", "gist", "create", str(path),
        "--desc", description,
    ]
    if public:
        cmd.append("--public")
    if dry_run:
        print(f"[dry-run] {' '.join(cmd)}")
        return {"file": path.name, "url": f"https://gist.github.com/dry-run/{path.stem}"}
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        print(f"error creating {path.name}: {proc.stderr or proc.stdout}", file=sys.stderr)
        return None
    url = proc.stdout.strip()
    print(f"OK  {path.name} → {url}")
    return {"file": path.name, "description": description, "url": url}


def build_index(manifest: dict, published: list[dict]) -> str:
    repo = manifest.get("repo_url", "")
    title = manifest.get("series_title", "Gist series")
    lines = [
        f"# {title}",
        "",
        f"**Repo:** {repo}",
        "",
        "A 15-part series on crowdsourced market AI — why millions burn tokens alone, "
        "and how one Git repo turns agent research into permanent history.",
        "",
        "## Index",
        "",
    ]
    for i, item in enumerate(published, 1):
        url = item.get("url", "")
        desc = item.get("description", item.get("file", ""))
        lines.append(f"{i}. [{desc}]({url})")
    lines.extend(
        [
            "",
            "---",
            "",
            "**Markets change. Memory compounds.**",
            "",
            f"⭐ [Star agents-unite]({repo}) · Run one ticker · One PR · Repeat",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish gists/ to GitHub.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--index-only", action="store_true", help="Only (re)publish INDEX gist")
    args = parser.parse_args()

    if not MANIFEST.is_file():
        print(f"error: missing {MANIFEST}", file=sys.stderr)
        return 1
    if not args.dry_run and not gh_available():
        print("error: gh CLI not authenticated. Run: gh auth login", file=sys.stderr)
        return 1

    manifest = load_manifest()
    existing: dict = {}
    if PUBLISHED.is_file():
        existing = json.loads(PUBLISHED.read_text(encoding="utf-8"))

    published: list[dict] = existing.get("gists", []) if args.index_only else []

    if not args.index_only:
        published = []
        for entry in manifest.get("gists", []):
            path = GISTS_DIR / entry["file"]
            result = create_gist(
                path,
                entry.get("description", path.stem),
                bool(entry.get("public", True)),
                args.dry_run,
            )
            if result:
                result["description"] = entry.get("description", "")
                published.append(result)

    index_path = GISTS_DIR / "INDEX.md"
    index_path.write_text(build_index(manifest, published), encoding="utf-8")

    index_result = create_gist(
        index_path,
        f"{manifest.get('series_title', 'Index')} — full index",
        True,
        args.dry_run,
    )

    out = {
        "repo_url": manifest.get("repo_url"),
        "series_title": manifest.get("series_title"),
        "index_url": index_result.get("url") if index_result else existing.get("index_url"),
        "gists": published,
        "updated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    }
    if not args.dry_run:
        PUBLISHED.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        print(f"\nWrote {PUBLISHED.relative_to(REPO_ROOT)}")
        if out.get("index_url"):
            print(f"Index gist: {out['index_url']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
