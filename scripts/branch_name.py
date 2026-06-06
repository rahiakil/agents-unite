#!/usr/bin/env python3
"""Print unique git branch name for a daily report PR."""

from __future__ import annotations

import argparse
import json
import sys

sys.path.insert(0, str(__file__).rsplit("/", 2)[0] if False else __import__("pathlib").Path(__file__).resolve().parent.as_posix())
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from assign_role import assign_role  # noqa: E402
from au_common import make_branch_name  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate report branch name.")
    parser.add_argument("--date")
    parser.add_argument("--date-mode", choices=["utc_midnight", "us_close"])
    parser.add_argument("--contributor")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    assignment = assign_role(args.date, args.contributor, date_mode=args.date_mode)
    branch = assignment.get("branch") or make_branch_name(
        str(assignment["date"]),
        str(assignment["ticker"]),
        str(assignment["contributor_id"]),
        role=str(assignment.get("daily_role", "research")),
    )
    if args.json:
        print(json.dumps({**assignment, "branch": branch}, indent=2))
    else:
        print(branch)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
