# The Hushabaloo

*Behind the third door on the left of the hall.*

A read-along picture book for three small listeners — 2-year-old twin boys and their
5-year-old sister. Full cast narration, sound effects written into the story itself, and
word-by-word highlighting that lands on each word as it is spoken and then fades behind it.

**Read it:** https://barknard.github.io/the-hushabaloo/

---

## The story

A very old, very lonely creature keeps every sound that was ever made, in jars, on
shelves that go up further than a ceiling. He takes the squeak of the stairs. Then Kip's
laugh, Mo's hum, Etta's word — and then, so softly that nobody hears, the **click** of
the door.

> For a door with no click isn't really a door.
> It's a wall. It's a wall. It's a wall. Nothing more.

Etta asks politely. Kip climbs. Neither works. Then Mo finds the one jar with no label,
and Etta works out why: the Hushabaloo has a jar for every sound a thing *makes*, and
nothing at all for a sound a person makes **on purpose, for no reason, just to be silly.**

There is no jar for a raspberry.

## How it's built

| | |
| --- | --- |
| `script/the-hushabaloo.md` | The book — cast, performance notes, verse in anapestic tetrameter |
| `script/blocks.py` | 85 blocks across 11 spreads; the single source of truth |
| `script/voice-casting.md` | How each voice was chosen, and what would disqualify a take |
| `player/index.html` | The player — illustrated spreads, karaoke highlighting, participation beats |
| `tools/generate.py` | Script → ElevenLabs → per-block audio + word timings |
| `tools/audit.py` | Fails the build on anything that would otherwise desync silently |
| `tools/build_standalone.py` | One self-contained HTML file: no server, no network |
| `tests/` | Playwright, run against the deployed **subpath** |
| `research/` | The cited research the design rests on |

```bash
python tools/generate.py          # generate audio (needs .env)
python tools/audit.py --audio     # verify the contract holds
npm test                          # Playwright: desktop, tablet, phone
python tools/build_standalone.py  # dist/the-hushabaloo.html
```

## Design notes worth knowing

**The twins are separable by ear.** Kip is voiced high, fast and clicky; Mo low, round
and slow — different formant structure, not merely different pitch. You cannot see which
twin is speaking, and twins who sound alike collapse into one character.

**The creature is never frightening.** Preschoolers' fantasy/reality distinction is
weakest for *frightening* content specifically, and children this age judge threat by how
a thing looks and sounds rather than by what the plot says it does — and a happy ending
does not reliably discharge that fear afterwards. So the Hushabaloo is warm, sad and
slow. No growl, no rasp, nowhere in the book.

**Participation never blocks.** Two spreads pause and invite the listeners to make a
sound. Both advance on their own regardless — a book that waits on a two-year-old is a
book that stops.

**The loudness curve is the emotional curve.** Spread 7 is the quietest thing in the book
because the creature is winning; spread 8 is the loudest because the children are. Spread
8 swells rather than slams, which is the difference between exciting and startling.

**Repetition is deliberate.** SHLOOP is identical every time it appears, and CLICK is one
file used three times — planted on spread 1, paid off on spread 9, and the last sound of
the story. Children this age learn more from the same story repeated than from varied
material, and the anticipation of a known sound is most of what a two-year-old is here for.

Sources for all of the above are in `research/`.

## Credits and licence

Original work by Eddie Thompson. Written in the tradition of read-aloud children's verse
— meter, rhyme scheme and structure are unprotectable craft. No text, character or
artwork from any existing work is used. Illustrations are inline SVG, drawn for this book.

Narration generated with ElevenLabs using library voices. No real child's voice was
cloned or imitated; the children's parts are performed the way animation casts them.

Text, code and illustrations: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
