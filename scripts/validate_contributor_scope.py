#!/usr/bin/env python3
"""CI guard: contributor branches may only touch one data/DATE/TICKER/ folder."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

REPORT_BRANCH_RE = re.compile(
    r"^report/(\d{4}-\d{2}-\d{2})-(.+)-([a-f0-9]{8})$",
    re.IGNORECASE,
)
WEEKLY_BRANCH_RE = re.compile(
    r"^weekly/(patterns|findings)/(\d{4}-\d{2}-\d{2})-([a-f0-9]{8})$",
    re.IGNORECASE,
)

PROTECTED_PREFIXES = (
    "scripts/",
    "agents/",
    "docs/",
    "raw/",
    "wiki/",
    "tickers/",
    "schemas/",
    ".github/",
    "config/",
)

PROTECTED_FILES = {
    "WIKI.md",
    "CLAUDE.md",
    "AGENTS.md",
    "Makefile",
    "requirements.txt",
    ".gitignore",
}

ALLOWED_BASENAMES = {
    "report.md",
    "sources.json",
    "consensus.md",
}

ALLOWED_BASENAME_RES = (
    re.compile(r"^report\.[a-zA-Z0-9_-]+\.md$"),
    re.compile(r"^sources\.[a-zA-Z0-9_-]+\.json$"),
    re.compile(r"^verification\.[a-zA-Z0-9_-]+\.md$"),
    re.compile(r"^patterns\.[a-zA-Z0-9_-]+\.md$"),
    re.compile(r"^findings\.[a-zA-Z0-9_-]+\.md$"),
)

REQUIRED_WORKFLOW_CHECKS = {
    ".github/workflows/contributor-guard.yml": (
        "validate_contributor_scope.py",
        "validate_report.py",
    ),
    ".github/workflows/validate-report.yml": (
        "validate_report.py",
    ),
}


def parse_weekly_branch(branch: str) -> tuple[str, str, str] | None:
    """Parse weekly/patterns|findings/DATE-HASH8 → (role, date, hash8)."""
    branch = branch.removeprefix("refs/heads/")
    match = WEEKLY_BRANCH_RE.match(branch)
    if not match:
        return None
    role, date, user_hash = match.group(1).lower(), match.group(2), match.group(3).lower()
    return role, date, user_hash


def parse_report_branch(branch: str) -> tuple[str, str, str] | None:
    """Parse report/DATE-TICKER-HASH8 → (date, ticker, hash8)."""
    branch = branch.removeprefix("refs/heads/")
    match = REPORT_BRANCH_RE.match(branch)
    if not match:
        return None
    date, ticker, user_hash = match.group(1), match.group(2), match.group(3).lower()
    return date, ticker.upper(), user_hash


def expected_data_dir(date: str, ticker: str) -> str:
    return f"data/{date}/{ticker}"


def is_allowed_data_file(path: str) -> bool:
    """Only allowed artifact files in data/DATE/TICKER/."""
    parts = Path(path).parts
    if len(parts) != 4 or parts[0] != "data":
        return False
    if parts[1].startswith("_"):
        return False
    name = parts[3]
    if name in ALLOWED_BASENAMES:
        return True
    return any(r.match(name) for r in ALLOWED_BASENAME_RES)


def is_weekly_data_file(path: str) -> bool:
    parts = Path(path).parts
    if len(parts) != 4 or parts[0] != "data":
        return False
    if parts[1] == "_patterns":
        return bool(re.match(r"^patterns\.[a-zA-Z0-9_-]+\.md$", parts[3]))
    if parts[1] == "_findings":
        return bool(re.match(r"^findings\.[a-zA-Z0-9_-]+\.md$", parts[3]))
    return False


def is_report_data_file(path: str) -> bool:
    name = Path(path).name
    if name in ("report.md", "consensus.md"):
        return True
    if name.startswith("report.") and name.endswith(".md"):
        return True
    if name.startswith("verification.") and name.endswith(".md"):
        return True
    if name.startswith("patterns.") and name.endswith(".md"):
        return True
    if name.startswith("findings.") and name.endswith(".md"):
        return True
    return False


def git_diff_names(base: str, head: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACDMR", base, head],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO_ROOT,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def read_github_username_from_report(path: Path) -> str | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    for line in parts[1].splitlines():
        if line.strip().lower().startswith("github_username:"):
            return line.split(":", 1)[1].strip()
    return None


def user_hash8(username: str) -> str:
    return hashlib.sha256(username.lower().encode("utf-8")).hexdigest()[:8]


def validate_scope(
    branch: str,
    changed_files: list[str],
    *,
    require_report: bool = True,
) -> list[str]:
    errors: list[str] = []
    branch = branch.removeprefix("refs/heads/")
    weekly = parse_weekly_branch(branch)
    if weekly:
        role, date, branch_hash = weekly
        allowed_prefix = f"data/_{role}s/{date}/"
        report_files_in_diff = [f for f in changed_files if is_report_data_file(f)]
        if require_report and not report_files_in_diff:
            errors.append(
                f"no weekly artifact in commit — add {role}.*.md under {allowed_prefix}"
            )
        for path in changed_files:
            if path.startswith(".github/workflows/"):
                errors.append(f"blocked: CI workflows are immutable for contributors ({path})")
                continue
            if path in PROTECTED_FILES:
                errors.append(f"blocked: protected file ({path})")
                continue
            for prefix in PROTECTED_PREFIXES:
                if path.startswith(prefix):
                    errors.append(f"blocked: protected path ({path})")
                    break
            else:
                if not path.startswith(allowed_prefix):
                    errors.append(f"out of scope: {path} — only {allowed_prefix}* allowed")
                    continue
                if not is_weekly_data_file(path):
                    errors.append(f"disallowed file type: {path}")
        for report_path in report_files_in_diff:
            full = REPO_ROOT / report_path
            gh_user = read_github_username_from_report(full)
            if gh_user and user_hash8(gh_user) != branch_hash:
                errors.append(
                    f"{report_path}: branch hash {branch_hash} != github_username {gh_user!r}"
                )
        return errors

    parsed = parse_report_branch(branch)
    if not parsed:
        return [f"branch must match report/DATE-TICKER-HASH8, got: {branch!r}"]

    date, ticker, branch_hash = parsed
    allowed_prefix = expected_data_dir(date, ticker) + "/"

    report_files_in_diff = [f for f in changed_files if is_report_data_file(f)]

    if require_report and not report_files_in_diff:
        errors.append(
            "no report file in commit — must add report.md or report.<user>.md "
            f"under {allowed_prefix}"
        )

    for path in changed_files:
        if path.startswith(".github/workflows/"):
            errors.append(f"blocked: CI workflows are immutable for contributors ({path})")
            continue
        if path in PROTECTED_FILES:
            errors.append(f"blocked: protected file ({path})")
            continue
        for prefix in PROTECTED_PREFIXES:
            if path.startswith(prefix):
                errors.append(f"blocked: protected path ({path})")
                break
        else:
            if not path.startswith(allowed_prefix):
                errors.append(
                    f"out of scope: {path} — only {allowed_prefix}* allowed for this branch"
                )
                continue
            if not is_allowed_data_file(path):
                errors.append(f"disallowed file type in report folder: {path}")

    for report_path in report_files_in_diff:
        full = REPO_ROOT / report_path
        gh_user = read_github_username_from_report(full)
        if not gh_user:
            errors.append(f"{report_path}: missing github_username in frontmatter")
            continue
        expected = user_hash8(gh_user)
        if expected != branch_hash:
            errors.append(
                f"{report_path}: branch hash {branch_hash} does not match "
                f"github_username {gh_user!r} (expected {expected})"
            )

        parts = Path(report_path).parts
        if len(parts) >= 3:
            if parts[1] != date:
                errors.append(f"{report_path}: date {parts[1]} != branch date {date}")
            if parts[2].upper() != ticker:
                errors.append(f"{report_path}: ticker {parts[2]} != branch ticker {ticker}")

    return errors


def verify_workflows() -> list[str]:
    """Ensure required CI workflows exist and still call guard scripts."""
    errors: list[str] = []
    for rel_path, needles in REQUIRED_WORKFLOW_CHECKS.items():
        path = REPO_ROOT / rel_path
        if not path.is_file():
            errors.append(f"missing required workflow: {rel_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel_path}: missing required check {needle!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate contributor branch scope for CI.")
    parser.add_argument("--branch", help="Branch name (e.g. report/2026-06-06-GE-5cd8be5d)")
    parser.add_argument("--base", help="Git base SHA for diff")
    parser.add_argument("--head", help="Git head SHA for diff")
    parser.add_argument(
        "--files",
        nargs="*",
        help="Changed file paths (instead of git diff)",
    )
    parser.add_argument(
        "--verify-workflows",
        action="store_true",
        help="Verify CI workflow integrity on main (cloud-side trust anchor)",
    )
    parser.add_argument(
        "--skip-report-required",
        action="store_true",
        help="Do not require a report file in diff (maintainer use)",
    )
    args = parser.parse_args()

    if args.verify_workflows:
        errors = verify_workflows()
        if errors:
            print("Workflow integrity check failed:", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)
            return 1
        print("Workflow integrity OK.")
        return 0

    branch = args.branch or ""
    if not branch:
        print("error: --branch required", file=sys.stderr)
        return 1

    if args.files is not None:
        changed = args.files
    elif args.base and args.head:
        changed = git_diff_names(args.base, args.head)
    else:
        print("error: provide --base/--head or --files", file=sys.stderr)
        return 1

    errors = validate_scope(
        branch,
        changed,
        require_report=not args.skip_report_required,
    )
    if errors:
        print("Contributor scope validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    parsed = parse_report_branch(branch)
    assert parsed
    date, ticker, _ = parsed
    print(f"OK: scope valid for {expected_data_dir(date, ticker)}/ ({len(changed)} file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
