# Self-audit: The Hushabaloo vs. the DATATRAX build

Requested check: *does it work like the DATATRAX book, with the lessons learned applied?*
This is the honest answer, including the things that are still open.

Audited 2026-08-01 against `moe/archive/datatrax/`.

---

## Parity — everything DATATRAX did, this does

| DATATRAX capability | Here | Notes |
| --- | --- | --- |
| Multi-voice cast via ElevenLabs | ✅ | 5 voices vs 3 |
| Word-by-word karaoke highlight | ✅ | Same three-state model, same 50 ms lead |
| Character-level timestamps → word timings | ✅ | Same aggregation, same `[tag]` stripping |
| Illustrated spreads, inline SVG | ✅ | 11 spreads, all art inline |
| Auto-advance page to page | ✅ | |
| Tap to pause, swipe to turn, keyboard | ✅ | Plus a scrubbable progress bar |
| Self-contained standalone HTML | ✅ | 13.7 MB, no server, no network |
| GitHub Pages deploy | ✅ | With gates DATATRAX had none of |

**Verified:** 36 Playwright tests green on desktop Chromium, iPad WebKit, iPhone WebKit.
`tools/audit.py --audio` passes: 88/88 blocks, 69/69 speech blocks matched word-for-word,
zero timing-count mismatches.

---

## Lessons applied

**1. The API key is not in the source.**
DATATRAX's `generate_datatrax_v2.py:21` carried a live key as a default argument, and it
reached pushed git history. Here the key loads from `.env` only, with no fallback literal
— `tools/generate.py` exits if it is unset. *(The DATATRAX key is still live and still in
history; rotating it is outstanding and is on Eddie.)*

**2. Script and player are one contract, checked mechanically.**
DATATRAX kept its text in Python and again in HTML with nothing comparing them. Drift by
one word desynced every highlight after that point, silently. `tools/audit.py` now fails
the build on block coverage, ordering, kind, SFX definition, direction leakage, and
word-for-word text parity. It was negative-tested — a deliberately altered word and a
renamed id both produce precise failures.

**3. No audio splitting.**
DATATRAX merged same-voice blocks into one call for prosody, then cut the audio apart at
timestamp midpoints with ffmpeg. That cut is where drift originates. Blocks here are
complete verse units, one call each — more requests, no cutting, no drift. ffmpeg is no
longer a dependency at all.

**4. Stale audio invalidates itself.**
`audio/provenance.json` fingerprints text + voice + model per block. Change a line and
only that block regenerates. No "delete the audio folder and start again" step, which is
the class of manual reset that produces confidently wrong builds.

**5. The standalone build has a declared seam.**
DATATRAX's builder string-matched fragments of its own player source and rewrote them —
edit the player and the replacements silently no-op, yielding a "standalone" file that
quietly fetches audio that isn't there. Here the player reads
`window.__HUSHABALOO_INLINE__` if present, and the builder **exits** if that seam is
missing rather than shipping a broken file.

**6. Missing audio is loud.**
DATATRAX logged to console and moved on after 2 s. Here a failed block shows an on-screen
error and continues, so a gap is visible rather than merely audible.

**7. Tests hit the URL shape that ships.**
The suite serves the site from `/the-hushabaloo/`, matching Pages, because a root-served
suite goes green while every visitor 404s. The CI workflow additionally greps the built
HTML for absolute asset paths and refuses to deploy if it finds any. `reuseExistingServer`
is off, so no run can pass against a stale build.

**8. No dead code.**
DATATRAX shipped `showSubtitle()`/`hideSubtitle()` as empty stubs that were still called.
There are none here.

**9. Controls say what they do.**
The play button carries a visible "Play story" / "Pause story" label and a matching
`aria-label`, asserted by test.

---

## Found and fixed during this audit

**An init race in the player.** Timings load asynchronously and the cover is raised in
that promise's `.finally()`. Anything driving the book before then was silently undone.
Surfaced by a Playwright failure that looked like a test bug and wasn't. Fixed by
publishing `window.__book.ready`.

**Two moderation rejections, same root cause.** The ElevenLabs child-voice policy blocked
Etta's original voice description ("a girl of about five", "plays a child") and later the
`raspberry_big` effect ("two small children blowing raspberries"). Both fixed by
describing the **sound** rather than the person — which is the more useful brief anyway.
Recorded as a standing rule in `script/voice-casting.md`.

---

## Open items — deliberate, not forgotten

**The startle guard now runs — for the eight CC0 effects only.** `tools/fetch_sfx.py`
trims, applies a 50 ms fade-in (above the 30 ms floor), fades out, and loudness-normalises
every fetched effect to its per-effect LUFS target. The three *generated* effects
(`shloop`, `shloop_soft`, `pop_cascade`) still come back as whatever ElevenLabs produced
and are **not** put through that chain — spread 8's cascade in particular was *prompted*
to rise over four seconds rather than being *guaranteed* to. Narration is likewise
un-normalised. A `tools/mix.py` covering generated audio and narration is still the gap.

**The bedtime toggle is not built.** Designed, not implemented. One master ships.

**The twins' unison raspberry is Kip's voice with a two-raspberry effect under it.** Two
sequential TTS clips would read as a queue, not a unison. Deliberate.

**Art is schematic.** Bold flat SVG shapes — the children are coloured circles with name
labels. It reads as a designed style rather than an unfinished one, but it is not
illustration. Each spread now carries a `--tint` that washes the page in that scene's
colour, so the palette follows the same arc as the loudness curve: warm at home, deep in
the collection, near-black at the low point, gold at the win, sunrise on the way home.

**One light clearance check on "Hushabaloo".** Nothing found in children's publishing.
That is a name search, not a trademark search.

---

## Second pass (2026-08-01, after first live review)

**Verse was rendering as prose — fixed.** The book is anapestic tetrameter and the line
breaks *are* the meter, but `wrapWords` rebuilt each block from its `textContent`, which
flattened the markup and ran every line together. It now walks text nodes with a
TreeWalker and wraps words in place, preserving `<span class="ln">`. A test asserts four
lines on four distinct screen rows, so it cannot silently regress. Wrapped continuations
get a hanging indent, the way poetry has always been set.

**Narrator inflection.** All 45 narrator blocks carry phrase-level `[direction]` rather
than one tag per block, and the narrator runs at `stability: 0.0` (Creative) where
eleven_v3 follows direction hardest. Characters stay at 0.5 so they remain recognisably
themselves. A guard in `tools/_retag_narrator.py` verified the *visible words* never moved.

**Open-source sound.** Eight effects now come from The Designer's Choice UCS Collection
(CC0) on archive.org, replacing generated approximations — including a real door latch, a
real ceramic clink and a real raspberry. Wikimedia Commons was tried first and has
essentially no everyday-object Foley; Freesound has the best library but needs an API
token. Three new sounds were added where the story already motivated them: a stair creak
on spread 1, rain going home on spread 6, and room tone in spread 7's silence. Credits in
`audio/sfx/CREDITS.md`; `tools/generate.py` now refuses to overwrite CC0 files.

**Typography.** Body text runs `clamp(1.35rem, 4.9vw, 1.85rem)` — roughly a third larger
than the first pass.

---

## Verdict

Feature parity with DATATRAX, with the failure modes that book left open now closed by
mechanical gates rather than by care. The gap between this and finished is **audio
mastering** — the startle guard and the bedtime master are specified, researched, and
unbuilt. Everything else is shippable and tested.
