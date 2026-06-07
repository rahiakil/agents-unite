# Liquidity filters and event-risk blocks

Not every ticker in the universe is tradable on every day.

**Liquidity filter** (from `tickers/universe.json`):

- `active: true`
- Average daily volume above configurable threshold
- ETFs blocked unless strategy opts in

**Event risk block:**

If **Notable Events** include earnings within ±2 sessions or FDA/binary catalyst, signal is **blocked** unless strategy sets `allow_event_risk: true`.

Sentiment around binary events is loud and often wrong. Gating forces an explicit opt-in.

---

**[TRADING.md](https://github.com/rahiakil/agents-unite/blob/main/docs/TRADING.md)**

Series: Signal Gating Criteria · #4 of 5
