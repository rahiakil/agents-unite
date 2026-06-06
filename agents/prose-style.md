# Prose style for agents-unite reports

Apply when writing **report markdown**, wiki pages, or contributor-facing text. Based on [stop-slop](https://github.com/hardikpandya/stop-slop) (MIT).

**Scope:** Sentiment sections and Key Themes bullets. Not JSON, frontmatter, or schema labels.

## Report writing rules

1. **Facts over narrative.** State what sources say. No throat-clearing ("Here's what's interesting about NVDA").
2. **No filler.** Cut "it's worth noting", "landscape", "delve", "robust", "compelling", "navigate", "headwinds/tailwinds" unless quoting a source.
3. **Specific beats vague.** Name the thread, headline, or metric. Not "sentiment is mixed" alone — say what bulls and bears cite.
4. **Short sentences.** 2–4 sentences in `# Sentiment`. Bullets in `# Key Themes` are one line each when possible.
5. **Active voice.** "Reddit threads cite X" not "X was cited by various discussions".
6. **No advice.** Sentiment reporting only — no "you should buy/sell".
7. **No invented drama.** Skip rhetorical contrasts ("not X, but Y"). State Y.
8. **Cite in JSON.** URLs and quotes belong in `sources.json`; the report summarizes mix and tone.

## Banned in reports (non-exhaustive)

| Avoid | Use instead |
|-------|-------------|
| Here's the thing / Let me be clear | (delete, start with fact) |
| The narrative around… | Thread / posts / headlines about… |
| Mixed signals abound | Bulls cite X; bears cite Y |
| Robust / solid / compelling | (delete or name the data) |
| Delve / unpack / lean into | (delete) |
| Game-changer / landscape | Significant / sector / market |
| really, very, significantly | (delete adverbs) |

## Self-check before validate

- Sentiment section: justified score in plain language?
- Each theme bullet: one concrete claim?
- Anything sound like generic AI filler? Rewrite or cut.
- All URLs in sources JSON, not pasted as prose filler?

Cursor users: full skill at [`.cursor/skills/stop-slop/`](../.cursor/skills/stop-slop/SKILL.md).
