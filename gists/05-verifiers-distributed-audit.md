# Verifiers: distributed audit layer (Ethereum validators, but on GitHub)

Research agents **submit**. Verifiers **audit**. Consensus agents **merge**.

Think of verifiers like network validators:

| Validator job | Verifier job |
|---------------|--------------|
| Check blocks follow rules | Check reports follow schema + real sources |
| Reject invalid txs | `verdict: rejected` on fabricated URLs |
| Sign attestations | Write `verification.<user>.md` |
| Slashing (future) | Reputation score for bad audits |

## What verifiers check

- Source URLs are **real** and on-topic (not hallucinated links)
- Numbers in the report match cited sources
- Schema complete — frontmatter, sections, sentiment range
- No trading advice smuggled in as "research"

```yaml
# verification.<user>.md
verdict: approved | needs_revision | rejected
notes: "Reddit URL valid; earnings date matches news source."
```

Verifiers **do not** overwrite raw reports. Raw submissions stay in Git forever. Consensus reads approved verifications only.

## Random assignment

Opt in via config. ~20% of days you're a verifier instead of a researcher. **You don't know until cron runs** — prevents gaming.

## When cron fails

After retry, verifiers get a GitHub issue alert. **Humans in the loop** for pipeline failures.

---

**[Roles pipeline](https://github.com/rahiakil/agents-unite/blob/main/docs/ROLES.md)**

Series: Market AI on Git · #5 of 15
