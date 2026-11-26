# Contributors next to the study

Real people join the same way the repo already describes. They run `./scripts/run-agent.sh`, get one ticker, and push a `report/DATE-TICKER-HASH8` or `batch/DATE-HASH8` branch. The pull request is the block. Contributor Guard and `validate_report.py` gate it. Their GitHub login is the identity. `contributor_hash` is the SHA256 of that login.

Simulated personas never take that path. Usernames are `sim-<archetype>-NN`. Reports carry `simulated: true` and `origin: simulated`. The harness writes them into a temp ledger, scores them, and archives the metrics on the `sim-data` branch.

The partition check is `validate_scope --block-simulated`, which Contributor Guard passes. It rejects a username that starts with `sim-` and a report whose frontmatter says `simulated: true`, `yes`, or `1`. A human login should stay clear of that prefix. The study calls `validate_scope` without the flag so the personas still exercise path and hash checks, and it marks every row `main_ledger_blocked: true`.

You can tell the two populations apart three ways:

- Username prefix and the `simulated` frontmatter flag, enforced on the way into `main`.
- `origin` on study rows (`simulated`). Human reports omit it.
- Storage. Human reports live under `data/` on `main`. Study attempts live in `sim/attempts.jsonl` for the seeded proof and under `history/runs/` on `sim-data` after that.

A person who shows up on a Tuesday is just another research report in that day's directory. The learnings rollup reads the archive, which contains only simulated rows, so their pull request does not enter the persona tables. If a later study wants both populations in one table, join on `date` and `ticker` and keep `origin` in the key.

Reputation for humans, when you turn it on, is `contributors/reputation.json`. The seeded run writes its own ledger to `sim/reputation.json` and does not fill the production file. The production file ships empty.
