# Trust without trust-me — immutable prompts & CI guards

Contributors **may only edit `data/`** in PRs. Everything else is protected:

| Layer | What it blocks |
|-------|----------------|
| `contributor-guard.yml` | Edits to scripts, agents, CI from report branches |
| `validate-report.yml` | Bad schema, fake URLs, missing frontmatter |
| `prompt_hash` in reports | Proves which template version was used |
| `ci-integrity.yml` | Cloud anchor — guard scripts can't be silently removed |

## Prompt provenance

```yaml
prompt_hash: 16b431faca503ced
prompt_file: agents/investigation-social.md
```

Validator recomputes hash from repo template. **Tamper-evident research.**

## Multi-report integrity

One file per user per ticker per day:

```
report.alice.md   ← Alice can't overwrite Bob's file
report.bob.md
```

## Roadmap anti-manipulation

- HEAD check on source URLs
- MAD outlier rejection in consensus
- Sybil caps + proof-of-human
- Reputation ledger (`contributors/reputation.json`)

Open source **means auditable rules**, not "trust our black box."

---

**[TRUST.md](https://github.com/rahiakil/agents-unite/blob/main/docs/TRUST.md)**

Series: Market AI on Git · #13 of 15
