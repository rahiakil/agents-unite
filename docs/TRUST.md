# Trust & Governance

## Immutable core

Contributors **may only modify files under `data/`** in pull requests.

Protected by:

- [`.github/workflows/contributor-guard.yml`](../.github/workflows/contributor-guard.yml) — on every push to `report/**` and every PR to `main`: enforces **one folder only** (`data/DATE/TICKER/`), validates report schema, blocks scripts/agents/CI edits
- [`.github/workflows/ci-integrity.yml`](../.github/workflows/ci-integrity.yml) — on `main`: verifies workflow files still call guard scripts (cloud trust anchor)
- [`.github/CODEOWNERS`](../.github/CODEOWNERS) — maintainer review for core paths

Rationale: users must not alter Python validators, agent prompts, or assignment logic.

## Prompt provenance

Every new report must include:

```yaml
prompt_hash: <sha256 prefix of template file>
prompt_file: agents/investigation-sentiment.md
```

CI validation (`scripts/validate_report.py`) verifies hash matches repo template.

The daily role prompt is selected by `scripts/assign_role.py` — not user-editable.

## Reputation

- Tied to **GitHub username** (`github_username` in frontmatter)
- One report file per user per ticker per day: `report.<slug>.md`
- Future: reputation scores from merged PR quality, verifier accuracy

## Verifier duties

- Check URLs (fabricated links, wrong domains)
- Cross-check numbers vs cited sources
- Write `consensus.md` — canonical view; raw reports preserved
- On cron failure after retry: verifiers alerted via GitHub issue

## Anti-manipulation (roadmap)

| Threat | Mitigation |
|--------|------------|
| Fake URLs | Verifier audit; future CI HEAD check |
| Hallucinated earnings | Verifier cross-check; contradiction in consensus |
| Sybil (many emails) | Future: per-IP cap, proof-of-human |
| Coordinated pump | Outlier MAD rejection; flag in consensus (automate later) |
| Prompt tampering | contributor-guard + prompt_hash + ci-integrity on main |

## Auto-merge policy

- **Platform code (maintainer):** Rahil / `@agents-unite/maintainers` merge directly when CI green — no sentiment pipeline.
- **Contributor data PRs:** Must pass Contributor Guard + Validate Report + security_review comment + verify/consensus as applicable — then merge.
- **Verification** is always part of the intended pipeline for external contributors.
- `consensus.md` becomes downstream canonical input for wiki/analytics.

See [GOVERNANCE.md](GOVERNANCE.md), [DATA_CORRECTIONS.md](DATA_CORRECTIONS.md), [CONSENSUS.md](CONSENSUS.md), [raw/DECISIONS.md](../raw/DECISIONS.md).
