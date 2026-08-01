# Voice Casting

Design prompts for ElevenLabs **Voice Design** (text-to-voice), one per character.

Paste the **description** into the description box and the **preview text** into the
preview box. The preview text is real material — the book's actual meter and each
character's actual speech pattern — because a voice auditioned on generic sample text
can fall apart the moment it meets anapestic tetrameter or a two-word toddler line.

Voice Design returns three candidates per run and is genuinely probabilistic. Expect to
regenerate, especially for the twins. Drop the IDs you settle on into `.env`, then run:

```
python tools/check_voices.py
```

> **Why Voice Design and not the Voice Library.** The Library prohibits child and
> child-like voices outright. Voice Design output is private to the account, so it isn't
> subject to that restriction. Separately: cloning the voice of a real child is a
> bright-line no under ElevenLabs' terms, and this project does not do it. Etta, Kip and
> Mo are performed the way animation casts children — designed voices, no real minor
> involved.

> **Describe the register, never the age.** ElevenLabs rejected an earlier draft of
> Etta's description (2026-08-01) for the phrases "a girl of about five" and "plays a
> child" — their child-voice policy screens on exactly that language. Every description
> below is written the way the part is actually cast: an **animated character voice** in a
> particular register. Bart Simpson is Nancy Cartwright; every child in every cartoon is
> an adult character actor working high and bright. That is not a workaround for the
> policy, it is a more accurate brief — "two years old" was never actionable information
> for a synthesis model, only pitch, nasality, consonant attack and vowel length are.
> Synthesized real-toddler timbre also sounds uncanny and bad, so this is the better
> product regardless.
>
> **The rule for any future character: name the sound, never the age.**

---

## Etta — the sister, 5, the plan

**Description**

> A bright, light, high-register character voice with a quick, energetic, slightly
> diminutive quality — the sort of voice cast for a plucky animated sidekick. American.
> Crisp diction and a fast, decisive delivery, with a faint bossy edge, like someone who
> has already worked out the plan and is impatient explaining it to people moving too
> slowly. Confident rather than sweet, warm underneath. Clean, close, dry studio recording.

**Preview text**

> I have counted the jars. There are hundreds. And LOOK —
> every jar has a label, like pages in a book!
> That one's RAIN. That one's DOG. That one's stairs-when-you-creep.
> Kip — can you climb it? Mo — what do you hear?
> Don't be scared. I'm right here. I am RIGHT here. Stay near.

**Reject if** it reads as a grown woman doing a small voice, or if it goes syrupy. Etta is
*competent* — she is the one holding it together.

---

## Kip — twin, 2, the climber

**Description**

> A very high, bright, slightly nasal character voice with a hard, clicky consonant attack
> — a fast, comic, pint-sized animated character. American. Delivers short loud bursts of
> one to three words, certain and completely undaunted, as though everything said is
> obvious. Slightly breathless, constantly in motion. Never whiny, never sad. Clean, close,
> dry studio recording.

**Preview text**

> Kip climb.
> I got it.
> Up! Up! Up!
> S'high.
> I can fit.
> Watch me. Watch me!
> Uh oh.
> No — I got it. I GOT it.
> Pbbbbbt!

**Reject if** it sounds sweet or tentative. Kip has no concept of being unable to do
something.

---

## Mo — twin, 2, the ear

**Description**

> A soft, round, slightly husky character voice, pitched low and delivered slowly, with
> long open vowels — a calm, watchful, pint-sized animated character. American. Speaks
> quietly in short phrases of one to three words, as if reporting something just noticed
> that nobody else caught. Calm and certain rather than timid or shy. Warm. Clean, close,
> dry studio recording.

**Preview text**

> Listen.
> Somefing in there.
> I hear it.
> Shhh. Shhh.
> It go shloop.
> Etta. Etta, listen.
> There. That one.
> Home.
> Pbbbbbt!

**Reject if** it comes back at the same pitch or pace as Kip. Play the two takes back to
back — if you can't tell them apart with your eyes shut, regenerate. Distinguishing the
twins by ear is the entire reason these two were designed as phonetic opposites.

---

## The Hushabaloo — the creature

**Description**

> An enormous, gentle, terribly lonely creature — the voice of a very old museum curator
> who has been alone with his collection for a hundred years. Deep and wide and soft-edged,
> with long round vowels and a slow, careful, faintly mournful delivery. Warm and breathy
> rather than growling; there is absolutely nothing threatening, monstrous, or predatory in
> it. Sounds genuinely puzzled and a little hurt that anyone would object to what he does.
> A soft wheeze between phrases. Clean recording with a large, soft room around it.

**Preview text**

> Oh. Oh, but you mustn't be cross with me. Truly, you mustn't.
> I only keep them. I keep them all safe. Every one.
> That is the rain. That is the stairs. That small one — that is a kettle. I have had it a
> hundred years, and it has never once gone quiet.
> Nothing is lost. Nothing is ever lost here. It is only... kept.
> You are not going to cry, are you? Oh dear. Oh dear, oh dear.

**Reject** anything with a growl, a rasp, a hiss, or a low menacing rumble — however good
it sounds. If the instinct on a take is "ooh, that's got a nice edge to it," that is the
take to throw away.

> **This is the one audition where "close enough" isn't.** Preschoolers' fantasy/reality
> distinction is weakest specifically for *frightening* content, and children of this age
> judge threat by how a thing looks and sounds rather than by what the plot says it does
> (Cantor). Zillmann & Cantor further found that a happy ending does not reliably discharge
> a child's fear the way it does an adult's. So a Hushabaloo that *sounds* frightening
> cannot be repaired by a warm resolution — the damage lands at the moment of hearing.
> Full citations in `research/01-developmental-psychology.md`.

---

## Narrator — *optional*

The default is reusing `Seuss Narrator` (`a8pNemkm8gTT9tjT2kne`) from the DATATRAX
project, already wired into `.env`. That voice was cast for an adult audience, though —
stately, rich baritone. For something lighter and more delighted:

**Description**

> A warm, playful storyteller reading a rhyming picture book aloud to small children. Light
> American accent, medium-low pitch with a bright, smiling quality — never solemn, never
> sleepy. Unhurried and musical, landing naturally on the rhythm of the verse and pausing
> at the end of each rhyme. Sounds genuinely delighted by the story being told, as if
> impatient to get to the next bit. Clean, close, intimate studio recording.

**Preview text**

> In a house at the end of a hall that was long,
> where the stairs had a squeak and the kettle a song,
> there were three. There was Etta. There's Mo. And there's Kip.
> And the third door stayed shut. And they gave it the slip.

Those four lines scan clean in anapestic tetrameter, the meter the whole book runs on. A
narrator take that fights that rhythm — or flattens it into prose — will fight every line
in the book.

---

## Fallbacks

If a description is rejected, or Voice Design simply won't produce a usable take, neither
of these costs the book anything.

**1. Cast from the Voice Library and pitch in post.** `Jessica – Playful, Bright`
(`cgSgspJ2msm6clMCkdW9`) is already on the account and is a plausible Etta as-is.
Pitch-shifting an adult voice up a few semitones is a standard production technique, and
`tools/mix.py` is already going to own per-block gain and transient shaping for the
startle guard — pitch is a small addition to a stage that has to exist regardless.

**2. Age Etta up.** She is the planner. Nothing in the story depends on her being exactly
five; she reads fine a year or two older, and a slightly older-sounding Etta actually
sharpens the contrast with the twins.

The twins are the genuinely constrained parts, and fallback 1 is the likely landing place
for both. Note that pitching Kip and Mo from the *same* source voice would collapse the
distinction the whole design rests on — if it comes to that, they need two different
source voices, shifted by different amounts.
