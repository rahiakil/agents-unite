# Open Questions (deferred)

_Resolved items moved to [DECISIONS.md](DECISIONS.md)._

## Trust & scale (future)

- [ ] **Per-IP rate limits** — cap submissions per IP/day (anti-Sybil)
- [ ] **Proof-of-human** — when coordinated attacks appear
- [ ] **Automated outlier rejection** — MAD/quorum on coordinated pumps (GME scenario)
- [ ] **Minimum stake to verify** — reputation threshold before verifier PRs count
- [ ] **URL live-check in CI** — HEAD request; 404 → flag (bandwidth cost)

## Assignment (future)

- [ ] **Fair token load** — same user getting NVDA daily vs obscure ticker; rotation policy
- [ ] **K slots per ticker** — max N submitters per (date, ticker) before reassignment

## Wiki / second brain

- [ ] **Auto wiki ingest** — trigger after N days of live data or on consensus merge
- [ ] **Index canonical/ only** — skip raw conflicting reports in LLM wiki

## Economics

- [ ] **Reputation benefits** — what verifiers/submitters unlock (trading strategies, etc.)

## Infrastructure

- [ ] **Hosted aggregator API** — read-only view of consensus layer
- [ ] **Hourly shards** — `data/DATE/TICKER/HH/`
