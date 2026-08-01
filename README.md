# read-along

An illustrated, narrated, word-by-word-highlighted read-along book for young children.

Built for three specific listeners: 2-year-old twin boys and their 5-year-old sister,
listening together.

## Status

**Pre-production.** Research complete; story and spec not yet written.

## What this is

A rhyming picture-book adventure delivered as a self-contained web page. Full cast
narration, sound effects authored into the story itself, and karaoke-style word
highlighting synced to the audio so a new reader can follow along.

The production pipeline is adapted from an earlier project (`DATATRAX`), which
established the core machinery:

| Stage | What it does |
| --- | --- |
| Script | Human-readable script — cast, performance notes, per-spread verse |
| Generate | Blocks → ElevenLabs TTS with character-level timestamps → per-block MP3 + word timings |
| Player | Single HTML page; audio blocks, inline SVG art, word highlighting, auto-advance |
| Build | Base64-inlines all audio into one standalone HTML file — works offline |

## Research

Four deep-research passes ground the design. Findings, with citations, in `research/`:

- `01-developmental-psychology.md` — attention, fear calibration, participation, and
  what actually holds a 2-year-old and a 5-year-old in the same story
- `02-seussian-craft.md` — anapestic tetrameter, rhyme schemes, word coinage,
  page-turn mechanics, failure modes, and the legal line between style and infringement
- `03-audio-sfx-and-elevenlabs.md` — loudness and startle targets for children's audio,
  SFX density, and the current ElevenLabs API surface
- `04-story-architecture.md` — preschool beat templates, safe peril, sibling-team
  competency design, and beat maps of eight acclaimed picture books

## Layout

```
research/   Cited research findings (see above)
script/     The book — verse, cast, performance direction
audio/      Generated narration and sound effects (gitignored; regenerable)
player/     The read-along web player
tools/      Generation and build scripts
```

## Legal

Original work. Written in the *tradition* of read-aloud children's verse — meter,
rhyme scheme, and structural patterns are unprotectable craft. No characters, text,
or artwork from any existing work are used. See the legal section of
`research/02-seussian-craft.md` for the specific line being respected.
