# ADR: Hash assignment + coverage optimizer

**Status:** Accepted (2026-06-06)

**Decision:** `SHA256(date:contributor_hash) % N` over sorted active tickers, biased toward zero-report tickers via coverage optimizer.

**Rationale:** Deterministic — same person, same day, same ticker globally. Optimizer avoids 10 researchers on MSFT while obscure tickers stay empty.

**Consequences:**

- `tickers/universe.json` ordering is stable (sorted keys)
- Date modes: `utc_midnight` or `us_close` (user config)
- Same contributor always same ticker → **rejected** (token burn unfairness)

**Revisit:** Per-user timezone fairness (documented in TIMING.md)

---

**[DECISIONS.md](https://github.com/rahiakil/agents-unite/blob/main/raw/DECISIONS.md)** · **[ARCHITECTURE.md](https://github.com/rahiakil/agents-unite/blob/main/docs/ARCHITECTURE.md)**

Series: Architecture Decision Records · #4 of 6
