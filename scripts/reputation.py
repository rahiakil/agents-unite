#!/usr/bin/env python3
"""Off-chain reputation ledger.

Faithful to docs/CONSENSUS.md and docs/METHODS.md:

- Identity is the GitHub username.
- Stake is 1. There is no token.
- Weight in the weighted median is stake * reputation * recency.
- Reputation tracks validation pass rate, proximity to the later consensus,
  and whether verifier votes matched the quorum.

A submission counts as a pass when it merges: schema, scope, and the one-file rule.
Proximity is measured only for merged reports, against the recomputed consensus.
After evidence the score is 0.15 * pass_rate + 0.70 * proximity + 0.15 * peer,
with add-one smoothing. The proximity term dominates so a contributor who
always clears the gates but sits far from consensus loses the 0.5 floor.
Scores are clamped to [0.02, 0.99] so a weight never becomes zero.
"""

from __future__ import annotations

import json
from pathlib import Path

STAKE = 1.0
RECENCY_ON_TIME = 1.0
RECENCY_LATE = 0.25
PRIOR = 0.5
FLOOR = 0.02
CAP = 0.99


def _blank(username: str) -> dict:
    return {
        "username": username,
        "passes": 0,
        "failures": 0,
        "prox_sum": 0.0,
        "prox_n": 0,
        "peer_ok": 0,
        "peer_n": 0,
        "reputation": PRIOR,
    }


def _ratio(numer: float, denom: float) -> float:
    if denom <= 0:
        return PRIOR
    return numer / denom


def score_row(row: dict) -> float:
    """Current reputation from accumulated evidence. Prior if the row is empty."""
    if row["passes"] + row["failures"] + row["prox_n"] + row["peer_n"] == 0:
        return PRIOR
    pass_rate = _ratio(row["passes"] + 1, row["passes"] + row["failures"] + 2)
    if row["prox_n"]:
        proximity = _ratio(row["prox_sum"] + PRIOR, row["prox_n"] + 1)
    else:
        proximity = PRIOR
    if row["peer_n"]:
        peer = _ratio(row["peer_ok"] + 1, row["peer_n"] + 2)
    else:
        peer = PRIOR
    raw = 0.15 * pass_rate + 0.70 * proximity + 0.15 * peer
    return max(FLOOR, min(CAP, raw))


class Ledger:
    def __init__(self) -> None:
        self.rows: dict[str, dict] = {}

    def row(self, username: str) -> dict:
        key = username.lower()
        if key not in self.rows:
            self.rows[key] = _blank(username)
        return self.rows[key]

    def reputation(self, username: str) -> float:
        key = username.lower()
        if key not in self.rows:
            return PRIOR
        return float(self.rows[key]["reputation"])

    def weight(self, username: str, *, late: bool = False, stake: float = STAKE) -> float:
        recency = RECENCY_LATE if late else RECENCY_ON_TIME
        return stake * self.reputation(username) * recency

    def observe(
        self,
        username: str,
        *,
        validation_pass: bool | None = None,
        distance: float | None = None,
        peer_match: bool | None = None,
    ) -> float:
        """Record one piece of evidence and return the updated reputation.

        `distance` is score minus consensus. Proximity is 1 minus the
        absolute distance, clipped at 0.
        """
        item = self.row(username)
        if validation_pass is True:
            item["passes"] += 1
        elif validation_pass is False:
            item["failures"] += 1
        if distance is not None:
            item["prox_sum"] += 1.0 - min(1.0, abs(distance))
            item["prox_n"] += 1
        if peer_match is True:
            item["peer_ok"] += 1
            item["peer_n"] += 1
        elif peer_match is False:
            item["peer_n"] += 1
        item["reputation"] = round(score_row(item), 6)
        return float(item["reputation"])

    def to_dict(self) -> dict:
        return {
            "version": 1,
            "formula": "0.15*pass_rate + 0.70*proximity + 0.15*peer",
            "stake": STAKE,
            "recency_on_time": RECENCY_ON_TIME,
            "recency_late": RECENCY_LATE,
            "contributors": {k: dict(v) for k, v in sorted(self.rows.items())},
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "Ledger":
        ledger = cls()
        if not path.is_file():
            return ledger
        data = json.loads(path.read_text(encoding="utf-8"))
        for key, row in (data.get("contributors") or {}).items():
            item = _blank(str(row.get("username") or key))
            item.update(row)
            item["reputation"] = score_row(item)
            ledger.rows[key.lower()] = item
        return ledger
