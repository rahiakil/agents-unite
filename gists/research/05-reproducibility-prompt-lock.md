# prompt_hash makes research reproducible

"Trust me, I used the official prompt" does not scale to 20,000 cron nodes.

Every report carries:

```yaml
prompt_hash: 16b431faca503ced
prompt_file: agents/investigation-social.md
```

`validate_report.py` recomputes the hash from the repo template. Mismatch → CI fails.

**What this blocks:**

- Silent prompt edits in your PR
- "I researched differently today" without disclosure
- Fork drift where contributors run unknown templates

Open source means **auditable rules**, not vibes.

---

**[TRUST.md](https://github.com/rahiakil/agents-unite/blob/main/docs/TRUST.md)** · **[ARCHITECTURE.md](https://github.com/rahiakil/agents-unite/blob/main/docs/ARCHITECTURE.md)**

Series: Market Research Methods · #5 of 6
