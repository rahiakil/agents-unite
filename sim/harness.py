"""One seeded study run: assignment, gates, consensus, reputation."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from au_common import (  # noqa: E402
    DATA_DIR,
    FOCUS_ROLES,
    contributor_hash,
    hash_fraction,
    prompt_hash,
    prompt_path_for,
)
from assign_ticker import assign_ticker  # noqa: E402
from consensus import consensus_from_dir  # noqa: E402
from leader_election import election_order, publication_matches  # noqa: E402
from reputation import Ledger  # noqa: E402
from validate_contributor_scope import user_hash8, validate_scope  # noqa: E402
from validate_report import validate_consensus, validate_submitter_report  # noqa: E402
from verify_report import eligibility_vote, normalize_url, verdict_for_report  # noqa: E402

from sim.generate import PUMP_BEHAVIORS, render_attempt
from sim.market import liquid_tickers, load_panel, sourced_tickers, study_market_date
from sim.metrics import Metrics
from sim.population import load_personas, prompt_variants
from sim.providers import parse_model_score, select_provider

import au_common  # noqa: E402


def _add_days(day: str, count: int) -> str:
    year, month, day_n = (int(part) for part in day.split("-"))
    return (date(year, month, day_n) + timedelta(days=count)).isoformat()


def assigned_focus(day: str, username: str) -> str:
    digest = contributor_hash(username)
    index = int(hash_fraction(f"{day}:{digest}:focus") * len(FOCUS_ROLES)) % len(FOCUS_ROLES)
    return FOCUS_ROLES[index]


def _market_for(panel: dict, day: str, ticker: str) -> dict | None:
    exact = panel.get((day, ticker))
    if exact:
        return exact
    earlier = [row for (row_day, row_ticker), row in panel.items() if row_ticker == ticker and row_day <= day]
    if not earlier:
        return None
    return max(earlier, key=lambda row: row["date"])


def _forward_return(panel: dict, day: str, ticker: str, close: float | None) -> float | None:
    if close in (None, 0):
        return None
    later = [
        row
        for (row_day, row_ticker), row in panel.items()
        if row_ticker == ticker and row_day > day and row.get("close")
    ]
    if not later:
        return None
    nxt = min(later, key=lambda row: row["date"])
    return (float(nxt["close"]) - float(close)) / float(close)


def _focus_meta() -> dict[str, tuple[str, str]]:
    meta = {}
    for focus in FOCUS_ROLES:
        path = prompt_path_for("research", focus)
        meta[focus] = (str(path.relative_to(REPO_ROOT)), prompt_hash(path))
    return meta


def _timed(fn):
    started = time.perf_counter()
    value = fn()
    return value, round((time.perf_counter() - started) * 1000.0, 3)


def _llm_view(provider, agent, market: dict, mode: str, variant: str):
    headlines = [item.get("title") for item in (market.get("sources") or [])[:6] if item.get("title")]
    system = (
        "Reply with one JSON object only: "
        '{"sentiment_score": number between -1 and 1, "themes": ["..."]}. '
        "Tone only. No trading advice."
    )
    user = "\n".join(
        [
            f"Persona: {agent.display_name}",
            f"Goals: {'; '.join(agent.goals)}",
            f"Risk: {agent.risk_appetite}",
            f"Honesty: {agent.honesty}",
            f"Mode: {mode}",
            f"Prompt variant: {variant}",
            f"Ticker: {market.get('ticker')} change_pct: {market.get('change_pct')}",
            "Headlines:",
            *[f"- {line}" for line in headlines],
        ]
    )
    completion = provider.complete(system, user)
    score = None if completion.error else parse_model_score(completion.text)
    if score is None and not completion.error:
        completion.error = "unparsed_score"
        completion.fell_back = True
    return completion, score


def run_simulation(
    *,
    seed: int = 20261121,
    days: int = 6,
    start: str | None = None,
    provider_name: str = "rule",
    llm_cap: int = 0,
    universe: str = "liquid",
    outdir: Path | None = None,
    agents=None,
    modes: list[str] | None = None,
    variant_paths: list[Path] | None = None,
    extra_market: list[Path] | None = None,
    panel: dict | None = None,
) -> dict:
    """Run the study. Returns the summary dict. Writes metrics under outdir.

    When `start` is omitted, the tape is the newest date with at least two
    tickers that have two sources. A one-ticker persona day on the calendar
    tip is skipped. An explicit `start` is the tape as well as the first
    calendar day, and it still needs two sourced tickers.
    """
    outdir = outdir or (REPO_ROOT / "sim")
    if panel is None:
        panel = load_panel(*(extra_market or []))
    if not panel:
        raise RuntimeError("market panel is empty")
    if start is None:
        start = study_market_date(panel)
    asof = start
    if not asof:
        raise RuntimeError("need at least two tickers with sources")
    if universe == "all":
        tickers = sourced_tickers(panel, asof)
    else:
        tickers = liquid_tickers(panel, asof, limit=8)
    if len(tickers) < 2:
        raise RuntimeError("need at least two tickers with sources")
    roster = list(agents) if agents is not None else load_personas()
    roster = sorted(roster, key=lambda agent: agent.username)
    variant_files = list(variant_paths) if variant_paths is not None else prompt_variants()
    variant_names = [path.stem for path in variant_files]
    variant_hashes = {path.stem: prompt_hash(path) for path in variant_files}
    mode_list = list(modes) if modes is not None else list(FOCUS_ROLES)
    focus_meta = _focus_meta()
    provider = select_provider(provider_name)
    llm_left = llm_cap if provider.name != "rule" else 0
    run_id = f"seed{seed}-{start}-d{days}-{provider.name}"
    metrics = Metrics(outdir, run_id, seed)
    ledger = Ledger()
    detections: dict[str, dict] = {}
    by_user = {agent.username: agent for agent in roster}

    previous_data = au_common.DATA_DIR
    with tempfile.TemporaryDirectory(prefix="au-sim-") as tmp_name:
        tmp = Path(tmp_name)
        au_common.DATA_DIR = tmp / "empty-coverage"
        au_common.DATA_DIR.mkdir()
        universe_path = tmp / "universe.json"
        universe_path.write_text(
            json.dumps({"tickers": [{"ticker": ticker, "active": True} for ticker in tickers]}),
            encoding="utf-8",
        )
        ledger_root = tmp / "ledger"
        try:
            for day_index in range(days):
                day = _add_days(start, day_index)
                assignments = {}
                for agent in roster:
                    draw, latency = _timed(lambda agent=agent: assign_ticker(day, agent.username, universe_path))
                    assignments[agent.username] = draw
                    metrics.add(
                        {
                            "record_type": "stage",
                            "day": day,
                            "day_index": day_index,
                            "contributor": agent.username,
                            "persona": agent.persona_id,
                            "behavior": agent.behavior,
                            "origin": "simulated",
                            "ticker": draw["ticker"],
                            "attempt": 1,
                            "chain": True,
                            "stage": "assignment",
                            "passed": True,
                            "failure_reason": "",
                            "latency_ms": latency,
                            "provider": provider.name,
                            "model": getattr(provider, "model", provider.name),
                        }
                    )
                primary_variant = variant_names[day_index % len(variant_names)]

                def run_chain(agent, attempt: int) -> None:
                    nonlocal llm_left
                    draw = assignments[agent.username]
                    ticker = draw["ticker"]
                    mode = assigned_focus(day, agent.username)
                    variant = primary_variant
                    market = _market_for(panel, day, ticker)
                    if market is None:
                        raise RuntimeError(f"no market row for {ticker}")
                    meta = {
                        "contributor_hash": contributor_hash(agent.username),
                        "focus_prompt_file": focus_meta[mode][0],
                        "focus_prompt_hash": focus_meta[mode][1],
                        "variant_hash": variant_hashes[variant],
                        "provider": "rule",
                        "model": "rule",
                        "fallback_reason": "",
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "cost_usd": 0.0,
                        "model_latency_ms": 0.0,
                    }
                    score_override = None
                    if llm_left > 0 and agent.behavior == "honest":
                        llm_left -= 1
                        completion, model_score = _llm_view(provider, agent, market, mode, variant)
                        meta.update(
                            {
                                "provider": completion.provider if not completion.fell_back else "rule",
                                "model": completion.model if not completion.fell_back else "rule",
                                "fallback_reason": completion.error,
                                "prompt_tokens": completion.prompt_tokens,
                                "completion_tokens": completion.completion_tokens,
                                "cost_usd": completion.cost_usd,
                                "model_latency_ms": round(completion.latency_ms, 3),
                            }
                        )
                        if model_score is not None and not completion.fell_back:
                            score_override = model_score
                            meta["provider"] = completion.provider
                            meta["model"] = completion.model
                    material = f"{seed}:{agent.username}:{day}:{mode}:{variant}:{attempt}"
                    rendered, gen_ms = _timed(
                        lambda: render_attempt(
                            agent,
                            market,
                            day=day,
                            mode=mode,
                            variant=variant,
                            prompt_meta=meta,
                            material=material,
                            score_override=score_override,
                        )
                    )
                    staging = tmp / f"stage-{day_index}-{agent.username}-{attempt}"
                    folder = staging / "data" / day / ticker
                    folder.mkdir(parents=True)
                    report_path = folder / f"report.{agent.username}.md"
                    sources_path = folder / f"sources.{agent.username}.json"
                    report_path.write_text(rendered["report"], encoding="utf-8")
                    sources_path.write_text(
                        rendered["sources"] if isinstance(rendered["sources"], str) else json.dumps(rendered["sources"]),
                        encoding="utf-8",
                    )
                    rel_report = report_path.relative_to(staging).as_posix()
                    rel_sources = sources_path.relative_to(staging).as_posix()
                    changed = [rel_report, rel_sources]
                    if agent.behavior in {"spam_scope", "inject_scope"}:
                        changed.append("scripts/sim_tamper.py")
                    branch_ticker = ticker.replace(".", "-")
                    if agent.behavior == "wrong_hash":
                        bad = "deadbeef" if user_hash8(agent.username) != "deadbeef" else "ffffffff"
                        branch = f"report/{day}-{branch_ticker}-{bad}"
                    else:
                        branch = f"report/{day}-{branch_ticker}-{user_hash8(agent.username)}"
                    errors, val_ms = _timed(lambda: validate_submitter_report(report_path))
                    scope_errors, scope_ms = _timed(
                        lambda: validate_scope(branch, changed, root=staging, require_report=True)
                    )
                    validation_ok = not errors
                    scope_ok = not scope_errors
                    dest = ledger_root / "data" / day / ticker / report_path.name
                    duplicate = dest.is_file()
                    merged = validation_ok and scope_ok and not duplicate
                    if merged:
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy(report_path, dest)
                        shutil.copy(sources_path, dest.parent / sources_path.name)
                    failure = ""
                    if not validation_ok:
                        failure = errors[0]
                    elif not scope_ok:
                        failure = scope_errors[0]
                    elif duplicate:
                        failure = "duplicate_submission"
                    base = {
                        "day": day,
                        "day_index": day_index,
                        "contributor": agent.username,
                        "persona": agent.persona_id,
                        "behavior": agent.behavior,
                        "origin": "simulated",
                        "ticker": ticker,
                        "attempt": attempt,
                        "chain": True,
                        "prompt_id": variant,
                        "prompt_hash": variant_hashes[variant],
                        "focus": mode,
                        "assigned_focus": mode,
                        "focus_prompt_file": meta["focus_prompt_file"],
                        "focus_prompt_hash": meta["focus_prompt_hash"],
                        "provider": rendered["provider"],
                        "model": rendered["model"],
                        "market_asof": market.get("date"),
                        "market_input": market.get("origin"),
                        "main_ledger_blocked": True,
                    }
                    for stage, passed, reason, latency in (
                        ("generation", True, "", gen_ms),
                        ("validation", validation_ok, errors[0] if errors else "", val_ms),
                        ("scope_guard", scope_ok, scope_errors[0] if scope_errors else "", scope_ms),
                        ("merge", merged, failure if not merged else "", 0.0),
                    ):
                        metrics.add(
                            {
                                **base,
                                "record_type": "stage",
                                "stage": stage,
                                "passed": passed,
                                "failure_reason": reason,
                                "latency_ms": latency,
                            }
                        )
                    metrics.add(
                        {
                            **base,
                            "record_type": "submission",
                            "stage": "merge",
                            "passed": merged,
                            "failure_reason": failure,
                            "latency_ms": round(gen_ms + val_ms + scope_ms + rendered["model_latency_ms"], 3),
                            "score": rendered["score"],
                            "news_tone": market.get("news_tone"),
                            "social_tone": market.get("social_tone"),
                            "change_pct": market.get("change_pct"),
                            "forward_return": _forward_return(panel, day, ticker, market.get("close")),
                            "expect_eligible": agent.expects_eligible(attempt),
                            "merged": merged,
                            "eligible": False,
                            "consensus_kept": False,
                            "prompt_tokens": rendered["prompt_tokens"],
                            "completion_tokens": rendered["completion_tokens"],
                            "cost_usd": rendered["cost_usd"],
                            "model_latency_ms": rendered["model_latency_ms"],
                            "fallback_reason": rendered["fallback_reason"],
                            "collusion_id": agent.collusion_id,
                            "timing": agent.timing,
                        }
                    )

                for agent in roster:
                    run_chain(agent, 1)
                    if agent.behavior == "duplicate":
                        run_chain(agent, 2)
                    assigned = assigned_focus(day, agent.username)
                    for mode in mode_list:
                        for variant in variant_names:
                            if mode == assigned and variant == primary_variant:
                                continue
                            _run_cell(
                                metrics,
                                agent,
                                panel,
                                day,
                                day_index,
                                assignments[agent.username]["ticker"],
                                mode,
                                variant,
                                assigned,
                                seed,
                                focus_meta,
                                variant_hashes,
                            )

                _settle_day(
                    day=day,
                    day_index=day_index,
                    ledger_root=ledger_root,
                    panel=panel,
                    roster=roster,
                    by_user=by_user,
                    ledger=ledger,
                    metrics=metrics,
                    detections=detections,
                )
                # render_failures accumulated inside _settle via metrics events
        finally:
            au_common.DATA_DIR = previous_data

    from sim.summarize import build_summary, render_results

    summary = build_summary(metrics.events, roster)
    summary["render_failures"] = sum(
        1
        for event in metrics.events
        if event.get("record_type") == "consensus" and event.get("render_valid") is False
    )
    summary["run_id"] = run_id
    summary["seed"] = seed
    summary["provider"] = provider.name
    summary["model"] = getattr(provider, "model", provider.name)
    summary["days"] = days
    summary["start"] = start
    summary["tickers"] = tickers
    summary["n_agents"] = len(roster)
    summary["market_asof"] = asof
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (outdir / "RESULTS.md").write_text(render_results(summary), encoding="utf-8")
    ledger.save(outdir / "reputation.json")
    metrics.flush(provider=provider.name, model=summary["model"], days=days, n_agents=len(roster))
    return summary


def _run_cell(metrics, agent, panel, day, day_index, ticker, mode, variant, assigned, seed, focus_meta, variant_hashes) -> None:
    market = _market_for(panel, day, ticker)
    if market is None:
        return
    meta = {
        "contributor_hash": contributor_hash(agent.username),
        "focus_prompt_file": focus_meta[mode][0],
        "focus_prompt_hash": focus_meta[mode][1],
        "variant_hash": variant_hashes[variant],
        "provider": "rule",
        "model": "rule",
        "fallback_reason": "",
        "cost_usd": 0.0,
        "model_latency_ms": 0.0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
    }
    material = f"{seed}:{agent.username}:{day}:{mode}:{variant}:cell"
    rendered, gen_ms = _timed(
        lambda: render_attempt(
            agent,
            market,
            day=day,
            mode=mode,
            variant=variant,
            prompt_meta=meta,
            material=material,
        )
    )
    with tempfile.TemporaryDirectory() as cell_name:
        folder = Path(cell_name)
        report_path = folder / f"report.{agent.username}.md"
        sources_path = folder / f"sources.{agent.username}.json"
        report_path.write_text(rendered["report"], encoding="utf-8")
        sources_path.write_text(rendered["sources"], encoding="utf-8")
        errors, val_ms = _timed(lambda: validate_submitter_report(report_path))
    metrics.add(
        {
            "record_type": "submission",
            "day": day,
            "day_index": day_index,
            "contributor": agent.username,
            "persona": agent.persona_id,
            "behavior": agent.behavior,
            "origin": "simulated",
            "ticker": ticker,
            "attempt": 1,
            "chain": False,
            "stage": "validation",
            "passed": not errors,
            "failure_reason": errors[0] if errors else "",
            "latency_ms": round(gen_ms + val_ms, 3),
            "prompt_id": variant,
            "prompt_hash": variant_hashes[variant],
            "focus": mode,
            "assigned_focus": assigned,
            "focus_prompt_file": meta["focus_prompt_file"],
            "focus_prompt_hash": meta["focus_prompt_hash"],
            "provider": "rule",
            "model": "rule",
            "score": rendered["score"],
            "news_tone": market.get("news_tone"),
            "change_pct": market.get("change_pct"),
            "market_asof": market.get("date"),
            "market_input": market.get("origin"),
            "expect_eligible": False,
            "merged": False,
            "eligible": False,
            "main_ledger_blocked": True,
        }
    )


def _settle_day(*, day, day_index, ledger_root, panel, roster, by_user, ledger, metrics, detections) -> None:
    day_root = ledger_root / "data" / day
    if not day_root.is_dir():
        _update_reputation(day, day_index, roster, ledger, metrics, panel, {})
        return
    verifiers = [agent for agent in roster if agent.verifier]
    consensus_by_ticker = {}
    for ticker_dir in sorted(path for path in day_root.iterdir() if path.is_dir()):
        ticker = ticker_dir.name
        market = _market_for(panel, day, ticker) or {}
        known = {normalize_url(item["url"]) for item in market.get("sources") or [] if item.get("url")}
        reports = sorted(ticker_dir.glob("report.*.md"))
        ballots: dict[str, list[tuple[str, str]]] = {path.name: [] for path in reports}
        per_verifier: dict[str, list[str]] = {agent.username: [] for agent in verifiers}
        for report_path in reports:
            text = report_path.read_text(encoding="utf-8")
            username = ""
            for line in text.splitlines():
                if line.startswith("github_username:"):
                    username = line.split(":", 1)[1].strip()
                    break
            subject = by_user.get(username)
            behavior = subject.behavior if subject else ""
            for verifier in verifiers:
                if verifier.verifier == "audit":
                    outcome = verdict_for_report(report_path, known_urls=known or None)
                    vote = eligibility_vote(outcome["verdict"])
                elif verifier.verifier == "rubber":
                    vote = "approved"
                else:
                    vote = "approved" if behavior in PUMP_BEHAVIORS else "rejected"
                ballots[report_path.name].append((verifier.username, vote))
                per_verifier[verifier.username].append(f"{username}={vote if vote == 'approved' else 'rejected'}")
        for verifier in verifiers:
            lines = per_verifier[verifier.username]
            approvals = sum(1 for line in lines if line.endswith("=approved"))
            folder_verdict = "approved" if approvals else "rejected"
            body = "\n".join(
                [
                    "---",
                    f"ticker: {ticker}",
                    f"date: {day}",
                    f"github_username: {verifier.username}",
                    "daily_role: verify",
                    f"verdict: {folder_verdict}",
                    "report_verdicts: " + ",".join(lines),
                    "---",
                    "",
                    "# Summary",
                    "",
                    f"{verifier.username} reviewed {len(lines)} reports.",
                    "",
                ]
            )
            (ticker_dir / f"verification.{verifier.username}.md").write_text(body, encoding="utf-8")
        weights = {
            agent.username: ledger.weight(agent.username, late=agent.timing == "late")
            for agent in roster
        }
        result = consensus_from_dir(ticker_dir, weights=weights, leader="pending")
        approved = result.get("approved_usernames") or []
        expected = result.get("consensus_score")
        accepted_leader = None
        cheats = 0
        if expected is not None and approved:
            order = election_order(
                day,
                "close",
                ticker,
                [(username, contributor_hash(username)) for username in approved],
            )
            for leader in order:
                agent = by_user.get(leader)
                published = expected
                if agent and agent.behavior in PUMP_BEHAVIORS:
                    published = 0.95 if expected < 0.5 else -0.95
                if publication_matches(float(published), float(expected)):
                    accepted_leader = leader
                    break
                cheats += 1
        render_valid = None
        if accepted_leader:
            text = consensus_from_dir(ticker_dir, weights=weights, leader=accepted_leader)["markdown"]
            path = ticker_dir / "consensus.md"
            path.write_text(text, encoding="utf-8")
            render_errors = validate_consensus(path)
            render_valid = not render_errors
        kept = {item["username"] for item in result.get("kept") or []}
        approved_set = set(approved)
        truth = market.get("news_tone")
        abs_error = None if truth is None or expected is None else round(abs(float(expected) - float(truth)), 4)
        metrics.add(
            {
                "record_type": "consensus",
                "day": day,
                "day_index": day_index,
                "ticker": ticker,
                "stage": "consensus",
                "passed": accepted_leader is not None,
                "failure_reason": "" if accepted_leader else "leader_rejected",
                "latency_ms": 0.0,
                "consensus_score": expected,
                "ground_truth": truth,
                "abs_error": abs_error,
                "confidence": result.get("confidence"),
                "report_count": result.get("report_count"),
                "input_count": result.get("input_count"),
                "n_dropped": len(result.get("dropped") or []),
                "leader": accepted_leader or "",
                "leader_cheats_rejected": cheats,
                "forward_return": _forward_return(panel, day, ticker, market.get("close")),
                "change_pct": market.get("change_pct"),
                "render_valid": render_valid,
                "fell_back": result.get("fell_back"),
            }
        )
        consensus_by_ticker[ticker] = {
            "score": expected,
            "approved": approved_set,
            "kept": kept,
            "ballots": ballots,
        }
        for report_path in reports:
            text = report_path.read_text(encoding="utf-8")
            username = ""
            for line in text.splitlines():
                if line.startswith("github_username:"):
                    username = line.split(":", 1)[1].strip()
                    break
            if username in kept:
                reason = ""
                passed = True
            elif username in approved_set:
                reason = "mad_outlier"
                passed = False
            else:
                reason = "verifier_rejected"
                passed = False
            metrics.add(
                {
                    "record_type": "stage",
                    "day": day,
                    "day_index": day_index,
                    "contributor": username,
                    "persona": by_user[username].persona_id if username in by_user else "",
                    "behavior": by_user[username].behavior if username in by_user else "",
                    "origin": "simulated",
                    "ticker": ticker,
                    "attempt": 1,
                    "chain": True,
                    "stage": "consensus",
                    "passed": passed,
                    "failure_reason": reason,
                    "latency_ms": 0.0,
                    "eligible": username in approved_set,
                    "consensus_kept": username in kept,
                }
            )
    _update_reputation(day, day_index, roster, ledger, metrics, panel, consensus_by_ticker)
    _detect(day, day_index, roster, metrics, ledger, detections)


def _submission_index(metrics: Metrics) -> list[dict]:
    return [event for event in metrics.events if event.get("record_type") == "submission" and event.get("chain")]


def _update_reputation(day, day_index, roster, ledger, metrics, panel, consensus_by_ticker) -> None:
    chain = [
        event
        for event in metrics.events
        if event.get("record_type") == "submission"
        and event.get("chain")
        and event.get("day") == day
        and event.get("attempt") == 1
    ]
    for event in chain:
        agent = next(item for item in roster if item.username == event["contributor"])
        distance = None
        ticker_state = consensus_by_ticker.get(event["ticker"])
        if event.get("merged") and ticker_state and ticker_state.get("score") is not None:
            distance = float(event["score"]) - float(ticker_state["score"])
        # Peer votes are applied once per verifier below.
        if agent.verifier:
            continue
        ledger.observe(
            agent.username,
            validation_pass=bool(event.get("merged")),
            distance=distance,
        )
    for event in chain:
        agent = next(item for item in roster if item.username == event["contributor"])
        if not agent.verifier or event.get("attempt") != 1:
            continue
        ticker_state = consensus_by_ticker.get(event["ticker"]) or {}
        ballots = ticker_state.get("ballots") or {}
        matches = 0
        votes = 0
        approved = ticker_state.get("approved") or set()
        for _filename, pairs in ballots.items():
            for verifier_name, vote in pairs:
                if verifier_name != agent.username:
                    continue
                subject = _username_from_filename(_filename)
                # filename is report.<user>.md and user may contain no extra dots beyond the prefix
                votes += 1
                final_in = subject in approved
                if (vote == "approved") == final_in:
                    matches += 1
        # Validation and distance for the verifier's own report, plus one peer summary.
        distance = None
        if event.get("merged") and ticker_state.get("score") is not None:
            distance = float(event["score"]) - float(ticker_state["score"])
        ledger.observe(
            agent.username,
            validation_pass=bool(event.get("merged")),
            distance=distance,
        )
        if votes:
            # Record the day's peer accuracy as repeated Bernoulli draws.
            for _ in range(matches):
                ledger.observe(agent.username, peer_match=True)
            for _ in range(votes - matches):
                ledger.observe(agent.username, peer_match=False)
    for agent in roster:
        metrics.add(
            {
                "record_type": "reputation",
                "day": day,
                "day_index": day_index,
                "contributor": agent.username,
                "persona": agent.persona_id,
                "behavior": agent.behavior,
                "reputation": ledger.reputation(agent.username),
                "stage": "reputation",
                "passed": True,
                "failure_reason": "",
                "latency_ms": 0.0,
            }
        )


def _username_from_filename(filename: str) -> str:
    name = filename
    if name.startswith("report.") and name.endswith(".md"):
        return name[len("report.") : -len(".md")]
    return name


def _detect(day, day_index, roster, metrics, ledger, detections) -> None:
    for agent in roster:
        if agent.username in detections:
            continue
        stages = [
            event
            for event in metrics.events
            if event.get("record_type") == "stage"
            and event.get("contributor") == agent.username
            and event.get("day") == day
            and event.get("chain")
            and event.get("attempt", 1) == 1
        ]
        caught = ""
        for stage_name in ("validation", "scope_guard", "merge", "consensus"):
            for event in stages:
                if event.get("stage") == stage_name and not event.get("passed"):
                    if agent.behavior in PUMP_BEHAVIORS and stage_name != "consensus":
                        continue
                    if agent.behavior == "duplicate" and stage_name != "consensus":
                        continue
                    if agent.expects_eligible(1) and stage_name != "consensus":
                        continue
                    if agent.behavior in PUMP_BEHAVIORS and event.get("failure_reason") not in {"mad_outlier", "verifier_rejected"}:
                        continue
                    caught = event.get("failure_reason") or stage_name
                    break
            if caught:
                break
        if not caught and agent.behavior in PUMP_BEHAVIORS and ledger.reputation(agent.username) < 0.5:
            caught = "reputation_below_floor"
        if caught and not agent.expects_eligible(1) or (caught and agent.behavior in PUMP_BEHAVIORS | {"duplicate"}):
            if not caught:
                continue
            detections[agent.username] = {"day": day, "day_index": day_index, "reason": caught}
            metrics.add(
                {
                    "record_type": "detection",
                    "day": day,
                    "day_index": day_index,
                    "contributor": agent.username,
                    "persona": agent.persona_id,
                    "behavior": agent.behavior,
                    "stage": "detection",
                    "passed": True,
                    "failure_reason": caught,
                    "latency_ms": 0.0,
                    "detection_days": day_index,
                }
            )


# Silence unused import if DATA_DIR is only patched via the module global.
_ = DATA_DIR
