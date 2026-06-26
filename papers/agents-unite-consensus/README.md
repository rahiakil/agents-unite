# Agents Unite Consensus Paper (Draft)

Six-page IEEE-style draft describing the Git-native consensus ledger for crowdsourced market sentiment.

## Build

Requires `pdflatex`, `bibtex`, and a LaTeX distribution with `IEEEtran`.

```bash
cd papers/agents-unite-consensus
make pdf
```

Output: `main.pdf`

The pipeline figure is embedded in `main.tex` via TikZ (no external assets required).

## Source mapping

| Paper section | Repository docs |
|---------------|-----------------|
| Introduction, scale | `docs/VISION.md`, `README.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| Consensus protocol | `docs/CONSENSUS.md`, `agents/consensus.md` |
| Trust / governance | `docs/TRUST.md`, `raw/DECISIONS.md` |
| Scientific methods | `docs/METHODS.md` |
| RAG / synthesis | `docs/RAG_AND_SYNTHESIS.md` |
| Design tensions | `raw/THINKING.md` |

## Status

Draft v0.1 — suitable for internal review and iteration. Not submitted to any venue.
