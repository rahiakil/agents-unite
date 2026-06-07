#!/usr/bin/env python3
"""Publish gist series to GitHub via gh CLI."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GISTS_DIR = REPO_ROOT / "gists"

# market-ai lives at gists/ root; other series live in subdirs
SERIES_DIRS: dict[str, Path] = {
    "market-ai": GISTS_DIR,
    "research": GISTS_DIR / "research",
    "gating": GISTS_DIR / "gating",
    "adrs": GISTS_DIR / "adrs",
}


def load_manifest(series_dir: Path) -> dict:
    manifest = series_dir / "manifest.yaml"
    if not manifest.is_file():
        raise FileNotFoundError(f"missing {manifest}")
    try:
        import yaml
    except ImportError:
        print("error: pyyaml required. Run: ./scripts/ensure-venv.sh llm", file=sys.stderr)
        sys.exit(1)
    return yaml.safe_load(manifest.read_text(encoding="utf-8"))


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


def build_index(manifest: dict, published: list[dict], *, count: int | None = None) -> str:
    repo = manifest.get("repo_url", "")
    title = manifest.get("series_title", "Gist series")
    n = count or len(published)
    intro = manifest.get(
        "series_intro",
        f"A {n}-part series from **agents-unite** — crowdsourced agentic market research on Git.",
    )
    lines = [
        f"# {title}",
        "",
        f"**Repo:** {repo}",
        "",
        intro,
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
            "",
            "## Other series",
            "",
            "- [Market AI on Git](https://github.com/rahiakil/agents-unite/blob/main/gists/INDEX.md) — 15 essays",
            "- [Research Methods](https://github.com/rahiakil/agents-unite/blob/main/gists/research/INDEX.md)",
            "- [Signal Gating](https://github.com/rahiakil/agents-unite/blob/main/gists/gating/INDEX.md)",
            "- [Architecture ADRs](https://github.com/rahiakil/agents-unite/blob/main/gists/adrs/INDEX.md)",
            "- [Website](https://rahiakil.github.io/agents-unite/)",
        ]
    )
    return "\n".join(lines) + "\n"


def publish_series(name: str, *, dry_run: bool, index_only: bool) -> dict | None:
    series_dir = SERIES_DIRS.get(name)
    if not series_dir:
        print(f"error: unknown series {name!r}. Choose: {', '.join(SERIES_DIRS)}", file=sys.stderr)
        return None

    manifest = load_manifest(series_dir)
    published_path = series_dir / "published.json"
    existing: dict = {}
    if published_path.is_file():
        existing = json.loads(published_path.read_text(encoding="utf-8"))

    published: list[dict] = existing.get("gists", []) if index_only else []

    if not index_only:
        published = []
        for entry in manifest.get("gists", []):
            path = series_dir / entry["file"]
            result = create_gist(
                path,
                entry.get("description", path.stem),
                bool(entry.get("public", True)),
                dry_run,
            )
            if result:
                result["description"] = entry.get("description", "")
                published.append(result)

    index_path = series_dir / "INDEX.md"
    index_path.write_text(
        build_index(manifest, published, count=len(manifest.get("gists", published))),
        encoding="utf-8",
    )

    index_result = create_gist(
        index_path,
        f"{manifest.get('series_title', 'Index')} — full index",
        True,
        dry_run,
    )

    out = {
        "series": name,
        "repo_url": manifest.get("repo_url"),
        "series_title": manifest.get("series_title"),
        "index_url": index_result.get("url") if index_result else existing.get("index_url"),
        "gists": published,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if not dry_run:
        published_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        print(f"\nWrote {published_path.relative_to(REPO_ROOT)}")
        if out.get("index_url"):
            print(f"Index gist ({name}): {out['index_url']}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish gist series to GitHub.")
    parser.add_argument(
        "--series",
        choices=list(SERIES_DIRS),
        default="market-ai",
        help="Which series to publish (default: market-ai)",
    )
    parser.add_argument("--all", action="store_true", help="Publish every series")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--index-only", action="store_true", help="Only (re)publish INDEX gist")
    args = parser.parse_args()

    if not args.dry_run and not gh_available():
        print("error: gh CLI not authenticated. Run: gh auth login", file=sys.stderr)
        return 1

    names = list(SERIES_DIRS) if args.all else [args.series]
    results: list[dict] = []
    for name in names:
        print(f"\n=== {name} ===")
        out = publish_series(name, dry_run=args.dry_run, index_only=args.index_only)
        if out:
            results.append(out)

    if args.all and not args.dry_run:
        catalog = GISTS_DIR / "SERIES.md"
        lines = [
            "# Gist series catalog",
            "",
            "Public gist indexes for **agents-unite**.",
            "",
            "| Series | Posts | Index gist |",
            "|--------|-------|------------|",
        ]
        for r in results:
            title = r.get("series_title", r.get("series", ""))
            n = len(r.get("gists", []))
            url = r.get("index_url", "")
            lines.append(f"| {title} | {n} | [index]({url}) |")
        lines.extend(["", f"_Updated {datetime.now(timezone.utc).strftime('%Y-%m-%d')}_", ""])
        catalog.write_text("\n".join(lines), encoding="utf-8")
        print(f"\nWrote {catalog.relative_to(REPO_ROOT)}")

    return 0 if results else 1


if __name__ == "__main__":
    raise SystemExit(main())
