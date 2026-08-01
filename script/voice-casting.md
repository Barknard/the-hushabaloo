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

---

## Etta — the sister, 5, the plan

**Description**

> A small, bright, quick-witted girl of about five, performed the way a skilled animation
> actor plays a child — light and high-pitched but crisp and confident, never babyish or
> cutesy. American. Fast, decisive delivery with a faint bossy edge, like someone who has
> already worked out the plan and is explaining it to people moving too slowly. Warm
> underneath the impatience. Clean, close, dry studio recording.

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

> A very small boy, barely more than a toddler, performed the way cartoons cast a tiny
> fearless kid. High, bright, slightly nasal, with a hard clicky consonant attack.
> American. Speaks only in bursts of one to three words, loud and certain and utterly
> undaunted, as though everything he says is obvious. A slight breathlessness, like he is
> already halfway up something. Never whiny, never sad. Clean, close, dry studio recording.

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

> A very small boy, barely more than a toddler, performed the way cartoons cast a quiet,
> watchful child. Low for his size — round, soft, slightly husky, with long open vowels
> and a slow, unhurried delivery. American. Speaks only in one to three words, usually
> quietly, as if reporting something he has just noticed that nobody else did. Calm and
> certain rather than shy or timid. Warm. Clean, close, dry studio recording.

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
