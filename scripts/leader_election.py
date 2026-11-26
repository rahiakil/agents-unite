#!/usr/bin/env python3
"""Deterministic leader election for a consensus shard.

docs/CONSENSUS.md:

    leader = argmin(SHA256("{date}:{hour}:{ticker}:{contributor_hash}"))

among contributors who submitted a valid report for that shard.
No network and no proof of work. The daily study uses hour "close".
Hourly shards pass the clock hour. `contributor_hash` is the full SHA256
hex from au_common.contributor_hash, not the 8 character branch prefix.
"""

from __future__ import annotations

import hashlib


def shard_key(date: str, hour: str, ticker: str, contributor_hash: str) -> str:
    material = f"{date}:{hour}:{ticker}:{contributor_hash}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def election_order(
    date: str,
    hour: str,
    ticker: str,
    candidates: list[tuple[str, str]],
) -> list[str]:
    """Return usernames from lowest shard key to highest.

    `candidates` is (username, full contributor hash). Ties break on username
    so the order is total even if two hashes collide.
    """
    ranked = sorted(
        candidates,
        key=lambda item: (shard_key(date, hour, ticker, item[1]), item[0].lower()),
    )
    return [username for username, _hash in ranked]


def elect_leader(
    date: str,
    hour: str,
    ticker: str,
    candidates: list[tuple[str, str]],
) -> str | None:
    order = election_order(date, hour, ticker, candidates)
    return order[0] if order else None


def publication_matches(published: float, expected: float, *, tol: float = 0.02) -> bool:
    """A leader's consensus_score must match an independent recomputation."""
    return abs(published - expected) <= tol
