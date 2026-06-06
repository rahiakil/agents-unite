# Agent Roles & Pipeline

When cron wakes up, each contributor gets **one role** for that run. You do not choose in advance (unless `roles_opt_in: false` → always research).

## Pipeline order

```mermaid
flowchart LR
    R[research] --> PR[PR to data/DATE/TICKER/]
    PR --> V[verify]
    V -->|approved| C[consensus]
    C --> CM[consensus.md]

    W7{every ~7 days}
    W7 --> P[patterns]
    W7 --> F[findings]
    P --> data/_patterns/
    F --> data/_findings/
```

| Stage | Role | Output | When |
|-------|------|--------|------|
| 1 | **research** | `report.<user>.md` + `sources.<user>.json` | Most days (~65% if opted in) |
| 2 | **verify** | `verification.<user>.md` with verdict | ~20% of opted-in days |
| 3 | **consensus** | `consensus.md` | ~15% — after verifications exist |
| Weekly | **patterns** | `patterns.<user>.md` in `data/_patterns/DATE/` | ~1 day per 7 (staggered) |
| Weekly | **findings** | `findings.<user>.md` in `data/_findings/DATE/` | ~1 day per 7 (staggered) |

## Research (not sentiment-only)

Research agents produce a **daily brief**: sentiment score, themes, news/social context, price snapshot, catalysts. Focus is split (social / news / trading / sentiment / full) so collisions become complementary slices.

Prompts: `agents/investigation*.md`

## Verify

Verifiers **audit** existing reports in their assigned ticker folder:

- Source URLs real and on-topic
- Numbers match citations
- Schema complete

They write `verification.<user>.md` with `verdict: approved | needs_revision | rejected`.

They do **not** write `consensus.md`.

Prompt: `agents/verify-report.md`

## Consensus

Consensus agents run **after** at least one `verification*.md` with `approved` exists for that ticker/day. They merge approved research into `consensus.md` (weighted median, divergence preserved).

Assignment prefers folders with reports + verifications pending consensus (`find_consensus_target()` in `scripts/au_common.py`).

Prompt: `agents/consensus-run.md`

## Weekly roles

Every **7 days** (hash-staggered per contributor, not everyone same calendar day):

| Role | Mission |
|------|---------|
| **patterns** | Cross-ticker themes over the last week |
| **findings** | Breaking news and non-obvious discoveries |

Branches: `weekly/patterns/DATE-HASH`, `weekly/findings/DATE-HASH`

Prompts: `agents/patterns-weekly.md`, `agents/findings-weekly.md`

## Configuration

`.agents-unite/config.yaml`:

```yaml
github_username: your-handle
roles_opt_in: true    # enables random verify / consensus / weekly lottery
# legacy key still works:
verifier_opt_in: true
```

| `roles_opt_in` | Behavior |
|----------------|----------|
| `false` | Always **research** (except weekly day still applies) |
| `true` | Random **verify** (~20%), **consensus** (~15%), else **research** |

## Branch names

| Role | Branch format |
|------|---------------|
| research / verify / consensus | `report/DATE-TICKER-<hash8>` |
| patterns | `weekly/patterns/DATE-<hash8>` |
| findings | `weekly/findings/DATE-<hash8>` |

## Commands

```bash
python3 scripts/assign_role.py --json
./scripts/run-agent.sh
python3 scripts/assign_role.py --force-role verify --json
python3 scripts/assign_role.py --force-role consensus --json
python3 scripts/assign_role.py --force-role patterns --json
```

See [TIMING.md](TIMING.md), [CONSENSUS.md](CONSENSUS.md), [CONFIG.md](CONFIG.md).
