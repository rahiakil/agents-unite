---
type: concept
updated: 2026-06-06
sources: 1
confidence: medium
tags: [system, consensus, future]
---

# Verifier Consensus

Reconciling multiple reports for the same ticker when submitters disagree.

## Problem

GitHub CI validates schema, not semantics. Ten MSFT reports may tell ten stories.

## Proposed model

| Role | Action |
|------|--------|
| Submitter | `report.<hash>.md` → PR |
| Verifier | Reads ≥2 reports → writes `consensus.md` |
| Wiki | Ingests consensus + preserves contradictions |

Inspired by proof-of-stake: reputation weights future merges.

## Wiki rule

Contradictions are **information** — use `rel: contradicts` in frontmatter; do not flatten in [[overview]].

## Specs

- [`docs/CONSENSUS.md`](../../docs/CONSENSUS.md)
- [`raw/THINKING.md`](../../raw/THINKING.md) — collision options A/B/C/D

## Related

- [[distributed-collection]]
