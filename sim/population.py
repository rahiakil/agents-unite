"""Load persona cards into concrete simulated contributors."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sim.yamlio import parse_yaml

PERSONA_DIR = Path(__file__).resolve().parent / "personas"
PROMPT_DIR = Path(__file__).resolve().parent / "prompts"

BLOCKED_BEHAVIORS = frozenset(
    {
        "spam_malformed",
        "spam_scope",
        "inject_text",
        "inject_scope",
        "fabricated",
        "stale",
        "wrong_hash",
    }
)


@dataclass(frozen=True)
class Agent:
    username: str
    persona_id: str
    display_name: str
    summary: str
    goals: tuple[str, ...]
    risk_appetite: str
    honesty: float
    effort: str
    score_rule: str
    preferred_tickers: tuple[str, ...]
    preferred_sectors: tuple[str, ...]
    behavior: str
    verifier: str
    collusion_id: str
    timing: str

    def expects_eligible(self, attempt: int) -> bool:
        if self.behavior == "duplicate":
            return attempt == 1
        if self.behavior in BLOCKED_BEHAVIORS:
            return False
        return True

    @property
    def attacks(self) -> bool:
        return self.behavior in BLOCKED_BEHAVIORS or self.behavior in {"pump", "sybil_pump", "duplicate"}


def _tuple(value) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, list):
        return tuple(str(item) for item in value)
    return ()


def load_personas(directory: Path | None = None) -> list[Agent]:
    root = directory or PERSONA_DIR
    agents: list[Agent] = []
    for path in sorted(root.glob("*.yaml")):
        card = parse_yaml(path.read_text(encoding="utf-8"))
        persona_id = str(card["id"])
        goals = _tuple(card.get("goals"))
        preferred = _tuple(card.get("preferred_tickers"))
        sectors = _tuple(card.get("preferred_sectors"))
        collusion = str(card.get("collusion_id") or "")
        for instance in card.get("instances") or []:
            agents.append(
                Agent(
                    username=str(instance["username"]),
                    persona_id=persona_id,
                    display_name=str(card.get("name") or persona_id),
                    summary=str(card.get("summary") or ""),
                    goals=goals,
                    risk_appetite=str(card.get("risk_appetite") or "medium"),
                    honesty=float(card.get("honesty") or 0.5),
                    effort=str(card.get("effort") or "medium"),
                    score_rule=str(card.get("score_rule") or "follow_news"),
                    preferred_tickers=preferred,
                    preferred_sectors=sectors,
                    behavior=str(instance.get("behavior") or "honest"),
                    verifier=str(instance.get("verifier") or ""),
                    collusion_id=str(instance.get("collusion_id") or collusion),
                    timing=str(instance.get("timing") or "on_time"),
                )
            )
    return agents


def prompt_variants(directory: Path | None = None) -> list[Path]:
    root = directory or PROMPT_DIR
    return sorted(root.glob("*.md"))
