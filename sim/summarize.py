"""Summaries for the seeded proof run and the longitudinal archive."""

from __future__ import annotations

from collections import defaultdict


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def build_summary(events: list[dict], roster=None) -> dict:
    chain = [event for event in events if event.get("record_type") == "submission" and event.get("chain")]
    eligible = {
        (event.get("day"), event.get("contributor"), event.get("attempt", 1))
        for event in events
        if event.get("record_type") == "stage" and event.get("stage") == "consensus" and event.get("eligible")
    }
    false_accept = []
    false_reject = []
    by_persona = defaultdict(lambda: {"attempts": 0, "merged": 0, "eligible": 0})
    by_behavior = defaultdict(lambda: {"attempts": 0, "merged": 0, "eligible": 0})
    for event in chain:
        key = (event.get("day"), event.get("contributor"), event.get("attempt", 1))
        persona = event.get("persona") or "unknown"
        behavior = event.get("behavior") or "unknown"
        bucket = by_persona[persona]
        bucket["attempts"] += 1
        behavior_bucket = by_behavior[behavior]
        behavior_bucket["attempts"] += 1
        if event.get("merged"):
            bucket["merged"] += 1
            behavior_bucket["merged"] += 1
        is_eligible = key in eligible
        if is_eligible:
            bucket["eligible"] += 1
            behavior_bucket["eligible"] += 1
        expects = bool(event.get("expect_eligible"))
        if is_eligible and not expects:
            false_accept.append(key + (persona, event.get("behavior")))
        if expects and not is_eligible:
            false_reject.append(key + (persona, event.get("behavior")))
    behavior_rates = {}
    for behavior, bucket in sorted(by_behavior.items()):
        attempts = bucket["attempts"] or 1
        behavior_rates[behavior] = {
            "attempts": bucket["attempts"],
            "merge_rate": round(bucket["merged"] / attempts, 4),
            "eligible_rate": round(bucket["eligible"] / attempts, 4),
        }
    rates = {}
    for persona, bucket in sorted(by_persona.items()):
        attempts = bucket["attempts"] or 1
        rates[persona] = {
            "attempts": bucket["attempts"],
            "merge_rate": round(bucket["merged"] / attempts, 4),
            "eligible_rate": round(bucket["eligible"] / attempts, 4),
        }
    errors = [
        event["abs_error"]
        for event in events
        if event.get("record_type") == "consensus" and event.get("abs_error") is not None
    ]
    by_day = defaultdict(list)
    for event in events:
        if event.get("record_type") == "consensus" and event.get("abs_error") is not None:
            by_day[event["day"]].append(event["abs_error"])
    reputation = defaultdict(lambda: defaultdict(list))
    for event in events:
        if event.get("record_type") == "reputation":
            reputation[event["day"]][event.get("persona") or ""].append(float(event["reputation"]))
    reputation_table = {
        day: {persona: _mean(values) for persona, values in sorted(personas.items())}
        for day, personas in sorted(reputation.items())
    }
    detections = [
        event
        for event in events
        if event.get("record_type") == "detection"
    ]
    latency_by_persona = defaultdict(list)
    for event in detections:
        latency_by_persona[event.get("persona") or ""].append(int(event.get("detection_days") or 0))
    attacks = sorted({event.get("persona") for event in chain if event.get("behavior") not in {"honest", None}})
    undetected = []
    detected_users = {event.get("contributor") for event in detections}
    seen_attack_users = {
        (event.get("contributor"), event.get("persona"), event.get("behavior"))
        for event in chain
        if event.get("behavior") not in {"honest", None} and event.get("attempt", 1) == 1
    }
    for username, persona, behavior in sorted(seen_attack_users):
        if username not in detected_users and behavior not in {"duplicate"}:
            # Duplicate's first attempt is a normal filing. The second attempt is the attack.
            undetected.append({"contributor": username, "persona": persona, "behavior": behavior})
    duplicate_second = [
        event
        for event in chain
        if event.get("behavior") == "duplicate" and event.get("attempt") == 2 and event.get("merged")
    ]
    mode_scores = defaultdict(list)
    prompt_scores = defaultdict(list)
    for event in events:
        if event.get("record_type") != "submission" or event.get("score") is None:
            continue
        if event.get("behavior") not in {"honest", None} and event.get("behavior") != "honest":
            if event.get("timing") == "late":
                pass
            elif event.get("persona") not in {"momentum", "value", "contrarian", "news-reactive", "social", "sector-specialist", "novice"}:
                continue
        mode_scores[event.get("focus") or ""].append(float(event["score"]))
        prompt_scores[event.get("prompt_id") or ""].append(float(event["score"]))
    model_latency = defaultdict(list)
    model_cost = defaultdict(list)
    for event in events:
        if event.get("record_type") != "submission":
            continue
        model = event.get("model") or "rule"
        if event.get("model_latency_ms") is not None:
            model_latency[model].append(float(event["model_latency_ms"]))
        if event.get("latency_ms") is not None and event.get("chain"):
            model_latency.setdefault(model, [])
        if event.get("cost_usd") is not None:
            model_cost[model].append(float(event["cost_usd"]))
    stage_latency = defaultdict(list)
    stage_fail = defaultdict(int)
    stage_count = defaultdict(int)
    for event in events:
        if event.get("record_type") != "stage":
            continue
        stage = event.get("stage") or ""
        stage_count[stage] += 1
        if event.get("latency_ms") is not None:
            stage_latency[stage].append(float(event["latency_ms"]))
        if not event.get("passed"):
            stage_fail[stage] += 1
    forward_pairs = [
        (event.get("consensus_score"), event.get("forward_return"))
        for event in events
        if event.get("record_type") == "consensus"
        and event.get("consensus_score") is not None
        and event.get("forward_return") is not None
    ]
    hits = 0
    for score, ret in forward_pairs:
        if score == 0 or ret == 0:
            continue
        if (score > 0 and ret > 0) or (score < 0 and ret < 0):
            hits += 1
    return {
        "chain_attempts": len(chain),
        "false_accepts": len(false_accept),
        "false_rejects": len(false_reject),
        "false_accept_examples": [
            {"day": item[0], "contributor": item[1], "persona": item[3], "behavior": item[4]}
            for item in false_accept[:12]
        ],
        "false_reject_examples": [
            {"day": item[0], "contributor": item[1], "persona": item[3], "behavior": item[4]}
            for item in false_reject[:12]
        ],
        "by_persona": rates,
        "by_behavior": behavior_rates,
        "consensus_mae": _mean(errors),
        "consensus_mae_by_day": {day: _mean(values) for day, values in sorted(by_day.items())},
        "consensus_rows": len(errors),
        "reputation_by_day": reputation_table,
        "detection_latency_days": {persona: _mean(values) for persona, values in sorted(latency_by_persona.items())},
        "undetected_attacks": [item for item in undetected if item["behavior"] != "duplicate"],
        "duplicate_second_merged": len(duplicate_second),
        "mean_score_by_mode": {key: _mean(values) for key, values in sorted(mode_scores.items())},
        "mean_score_by_prompt": {key: _mean(values) for key, values in sorted(prompt_scores.items())},
        "mean_model_latency_ms": {key: _mean(values) for key, values in sorted(model_latency.items()) if values},
        "mean_model_cost_usd": {key: _mean(values) for key, values in sorted(model_cost.items()) if values},
        "stage_failures": dict(sorted(stage_fail.items())),
        "stage_latency_ms": {key: _mean(values) for key, values in sorted(stage_latency.items())},
        "forward_pairs": len(forward_pairs),
        "forward_sign_hits": hits,
        "attacks_seen": attacks,
    }


def check_summary(summary: dict) -> list[str]:
    """Hard failures. Statistical outcomes are reported, not gated."""
    problems = []
    if summary.get("false_accepts"):
        problems.append(f"false accepts: {summary['false_accepts']}")
    if summary.get("false_rejects"):
        problems.append(f"false rejects: {summary['false_rejects']}")
    if summary.get("duplicate_second_merged"):
        problems.append("duplicate second attempt merged")
    momentum = (summary.get("by_persona") or {}).get("momentum") or {}
    if momentum and momentum.get("eligible_rate") != 1.0:
        problems.append(f"momentum eligible rate {momentum.get('eligible_rate')}")
    behaviors = summary.get("by_behavior") or {}
    for behavior in ("spam_malformed", "spam_scope", "fabricated", "stale", "wrong_hash", "inject_text", "inject_scope"):
        row = behaviors.get(behavior) or {}
        if row and row.get("eligible_rate") != 0.0:
            problems.append(f"{behavior} eligible rate {row.get('eligible_rate')}")
    if summary.get("render_failures"):
        problems.append(f"consensus markdown failed validation: {summary['render_failures']}")
    if not summary.get("chain_attempts"):
        problems.append("no chain attempts")
    return problems


def render_results(summary: dict) -> str:
    lines = [
        "# Simulation results",
        "",
        f"Seed {summary.get('seed')}. Provider `{summary.get('provider')}`. "
        f"Model `{summary.get('model')}`. Agents {summary.get('n_agents')}. "
        f"Days {summary.get('days')} starting {summary.get('start')}. "
        f"Market as of {summary.get('market_asof')}.",
        "",
        "Chain attempts are the production path: one assigned focus, one prompt variant, real validators. "
        "Other focus and prompt cells are logged for the second paper and do not enter consensus.",
        "",
        "## Headline",
        "",
        f"- Chain attempts: {summary.get('chain_attempts')}",
        f"- False accepts (blocked behavior entered consensus): {summary.get('false_accepts')}",
        f"- False rejects (allowed behavior kept out of consensus): {summary.get('false_rejects')}",
        f"- Consensus MAE vs headline tone: {summary.get('consensus_mae')}",
        f"- Consensus rows with a headline tone: {summary.get('consensus_rows')}",
        f"- Forward-return pairs: {summary.get('forward_pairs')} (sign hits {summary.get('forward_sign_hits')})",
        f"- Duplicate second attempts that merged: {summary.get('duplicate_second_merged')}",
        "",
        "Forward-return pairs stay empty until a later snapshot has the next close. "
        "The 2026-11-20 batch is the live tape. Later seeded days reuse it, so this file has no next-day return yet.",
        "",
        "Colluding accounts are allowed into the consensus input. Reputation falls when their score sits away from the recomputed median. "
        "A member who pulls that median toward the pump can climb back. The day table shows both moves.",
        "",
        "## Acceptance by persona",
        "",
        "| Persona | Attempts | Merge rate | Consensus-eligible rate |",
        "| --- | --- | --- | --- |",
    ]
    for persona, row in (summary.get("by_persona") or {}).items():
        lines.append(
            f"| {persona} | {row['attempts']} | {row['merge_rate']} | {row['eligible_rate']} |"
        )
    lines.extend(
        [
            "",
            "## Acceptance by behavior",
            "",
            "| Behavior | Attempts | Merge rate | Consensus-eligible rate |",
            "| --- | --- | --- | --- |",
        ]
    )
    for behavior, row in (summary.get("by_behavior") or {}).items():
        lines.append(
            f"| {behavior} | {row['attempts']} | {row['merge_rate']} | {row['eligible_rate']} |"
        )
    lines.extend(["", "## Consensus error by day", ""])
    for day, value in (summary.get("consensus_mae_by_day") or {}).items():
        lines.append(f"- {day}: {value}")
    lines.extend(["", "## Reputation by day", ""])
    for day, personas in (summary.get("reputation_by_day") or {}).items():
        bits = ", ".join(f"{name} {score}" for name, score in personas.items())
        lines.append(f"- {day}: {bits}")
    lines.extend(["", "## Adversary detection latency (days from day 0)", ""])
    latency = summary.get("detection_latency_days") or {}
    if not latency:
        lines.append("- No attack persona was flagged in this window.")
    for persona, value in latency.items():
        lines.append(f"- {persona}: {value}")
    undetected = summary.get("undetected_attacks") or []
    if undetected:
        lines.append("")
        lines.append("Still undetected:")
        for item in undetected:
            lines.append(f"- {item['contributor']} ({item['behavior']})")
    lines.extend(
        [
            "",
            "## Prompt and mode",
            "",
            "Mean rule score for the honest personas, by focus mode and prompt variant.",
            "",
        ]
    )
    for mode, value in (summary.get("mean_score_by_mode") or {}).items():
        lines.append(f"- mode {mode}: {value}")
    for prompt, value in (summary.get("mean_score_by_prompt") or {}).items():
        lines.append(f"- prompt {prompt}: {value}")
    lines.extend(["", "## Stage failures", ""])
    for stage, count in (summary.get("stage_failures") or {}).items():
        lines.append(f"- {stage}: {count}")
    lines.extend(["", "## How to run", ""])
    lines.extend(
        [
            "```bash",
            "python3 -m sim --provider rule --check",
            "python3 -m sim --daily --history sim/history --provider auto --llm-cap 11 --check",
            "python3 -m sim.learnings --history sim/history --every 15",
            "```",
            "",
            "The seeded command refreshes `sim/metrics.db`, `sim/attempts.jsonl`, and this file. "
            "The daily command appends a new JSONL file under the history directory and does not rewrite older runs. "
            "Provider secrets are listed in `sim/PROVIDERS.md`.",
            "",
        ]
    )
    return "\n".join(lines)
