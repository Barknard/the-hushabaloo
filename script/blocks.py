"""
THE HUSHABALOO -- block manifest.

The single source of truth. `tools/generate.py` reads this to produce audio and word
timings; `player/index.html` addresses the same block IDs via `data-audio`. If an ID
here has no counterpart in the player (or the reverse), `tools/audit.py` fails the build
-- that mismatch is exactly how DATATRAX's karaoke silently desynced.

Block kinds
-----------
speech  Narration or dialogue. Sent to ElevenLabs TTS with character-level timestamps,
        which are aggregated to words for the karaoke highlight.
sfx     A sound effect, generated from `text` as a prompt. No words, no highlighting.
wait    A participation beat: the player pauses so the listeners can make the sound
        themselves. Never blocks -- it always auto-advances (see PARTICIPATION below).

Voice tags in square brackets ([excited], [whispers]) are performance direction for
eleven_v3. They are stripped before word timings are matched to the DOM, so they must
never appear in the player's visible text.
"""

# ── Cast ──────────────────────────────────────────────────────────────────────
# Resolved from .env at generation time; these names are the contract.
VOICES = {
    "NARRATOR":   "VOICE_NARRATOR",
    "ETTA":       "VOICE_ETTA",
    "KIP":        "VOICE_KIP",
    "MO":         "VOICE_MO",
    "HUSHABALOO": "VOICE_HUSHABALOO",
}

# ── Pauses (seconds of silence appended after a block) ────────────────────────
LINE = 0.6      # between blocks inside a thought
BEAT = 1.2      # a landed beat
SECTION = 1.8   # between speakers
PAGE = 2.5      # end of a spread

# ── Sound effects ─────────────────────────────────────────────────────────────
# Generated once each and reused by every block that references them. CLICK is
# deliberately one file used three times -- spread 1, spread 9's payoff, and the last
# line -- because the listener must recognise it as literally the same sound.
#
# `peak_dbfs` feeds the startle guard in tools/mix.py. Nothing here may exceed the
# narration RMS by more than +6 dB, and everything gets a >=30 ms attack.
SFX = {
    "click": dict(
        prompt="a single small wooden door latch clicking shut, clean and close, no reverb",
        seconds=1.0, peak_dbfs=-14.0,
    ),
    "shloop": dict(
        prompt="a soft wet slurping swallow, like a sound being sucked into a jar, "
               "round and comical, not harsh, quick but smooth",
        seconds=1.6, peak_dbfs=-12.0,
    ),
    "shloop_soft": dict(
        prompt="a very soft, quiet wet slurping swallow, muted and distant, gentle",
        seconds=1.6, peak_dbfs=-18.0,
    ),
    "pop": dict(
        prompt="a glass jar lid popping open and a rush of rain pouring out, bright and "
               "airy, NOT a smash, no breaking glass",
        seconds=2.5, peak_dbfs=-12.0,
    ),
    "pop_cascade": dict(
        prompt="one glass pop, then two, then dozens cascading into a joyful rush of "
               "escaping sounds, rising steadily over four seconds, warm not harsh",
        seconds=5.0, peak_dbfs=-11.0,
    ),
    "raspberry_big": dict(
        prompt="two small children blowing loud wet raspberries together, joyful and silly",
        seconds=2.0, peak_dbfs=-11.0,
    ),
    "raspberry_small": dict(
        prompt="one small gentle wet raspberry blown softly, close and sweet",
        seconds=1.2, peak_dbfs=-16.0,
    ),
}

# ── The book ──────────────────────────────────────────────────────────────────
# (block_id, kind, voice_or_sfx, text, pause_after, spread)
#
# `text` for speech blocks must match the player's visible text word-for-word once
# [tags] are stripped. tools/audit.py enforces this.

BLOCKS = [
    # ══ COVER ══
    ("cover_nar_01", "speech", "NARRATOR",
     "[warm, slow, drawing them in] The Hushabaloo. ... "
     "Behind the third door on the left of the hall.", PAGE, "cover"),

    # ══ SPREAD 1 — a house that was full of it ══
    ("p1_nar_01", "speech", "NARRATOR",
     "In a house at the end of a hall that was long, "
     "where the stairs had a squeak and the kettle a song, "
     "there was Etta, who planned. There was Mo, who could hear. "
     "There was Kip, who climbed everything, year after year.", LINE, "p1"),

    ("p1_nar_02", "speech", "NARRATOR",
     "[building, delighted] And the house was so full of so much to be heard, "
     "of a clank and a clink and a creak and a bird, "
     "of the hum of the fridge, of the drip of the tap, "
     "of the whumpf of the dog as he flopped for a nap.", LINE, "p1"),

    ("p1_nar_03", "speech", "NARRATOR",
     "[slowing, this one matters] And the best of them all, and remember this trick, "
     "was the door down the hall. And the door went...", LINE, "p1"),

    ("p1_sfx_click", "sfx", "click", "", BEAT, "p1"),

    ("p1_nar_04", "speech", "NARRATOR", "click.", PAGE, "p1"),

    # ══ SPREAD 2 — Tuesday ══
    ("p2_nar_01", "speech", "NARRATOR",
     "But on Tuesday the kettle did not sing its song. "
     "And the stairs did not squeak. And the tap-drip was gone.", SECTION, "p2"),

    ("p2_etta_01", "speech", "ETTA",
     "[counting on her fingers, interested not frightened] "
     "That's three. That's three sounds. And they've all gone away.", SECTION, "p2"),

    ("p2_nar_02", "speech", "NARRATOR",
     "Now the hall had three doors, and they knew one and two. "
     "But the third door, the third door they'd never been through. "
     "And they stood there. And Mo put his ear to the wood.", SECTION, "p2"),

    ("p2_mo_01", "speech", "MO",
     "[quiet, certain] Listen. ... Somefing in there.", SECTION, "p2"),

    ("p2_nar_03", "speech", "NARRATOR",
     "[dry] And there was. ... "
     "For a sound they had heard every day of their lives, "
     "the small squeak of the stairs, came unstuck, and it dived "
     "through the crack of that door with a...", LINE, "p2"),

    ("p2_sfx_shloop", "sfx", "shloop", "", BEAT, "p2"),

    ("p2_nar_04", "speech", "NARRATOR",
     "and was gone. And the stairs were as silent as snow, from then on.", PAGE, "p2"),

    # ══ SPREAD 3 — a room that was not in the house ══
    ("p3_nar_01", "speech", "NARRATOR",
     "So they opened the door, and the door made no sound, "
     "and they stepped through the door, and they looked all around. "
     "And behind the third door on the left of the hall "
     "was a room that was not in the house. Not at all.", LINE, "p3"),

    ("p3_nar_02", "speech", "NARRATOR",
     "[slower, awe] It was tall as a church and as wide as a town, "
     "and it went up so far that no ceiling came down. "
     "And on every last shelf, in a row, in a row, "
     "were the jars. And each jar had a label. And so...", SECTION, "p3"),

    ("p3_etta_01", "speech", "ETTA",
     "[thrilled, she loves a label] That one's RAIN. That one's DOG. "
     "That one's stairs-when-you-creep. "
     "That one's somebody snoring. That's somebody's sheep!", SECTION, "p3"),

    ("p3_nar_03", "speech", "NARRATOR",
     "[quieter, gentle reveal] Then a shelf became shoulders. A jar became eye. "
     "And the thing they'd been sure was a wall said...", SECTION, "p3"),

    ("p3_hush_01", "speech", "HUSHABALOO",
     "[soft, delighted, faintly wheezy] Oh. Hello. Oh my.", PAGE, "p3"),

    # ══ SPREAD 4 — the keeper ══
    ("p4_hush_01", "speech", "HUSHABALOO",
     "[warm, explaining something lovely and obvious] "
     "I am only the keeper. I keep them. That's all. "
     "Every sound ever let loose in somebody's hall, "
     "every squeak, every drip, every creak, every knock, "
     "I have kept them all safe. Every one. Every clock.", SECTION, "p4"),

    ("p4_nar_01", "speech", "NARRATOR",
     "And he reached out a hand that was mostly a sleeve, "
     "and he took Kip's small laugh. And he did not ask leave.", LINE, "p4"),

    ("p4_sfx_shloop_1", "sfx", "shloop", "", LINE, "p4"),

    ("p4_nar_02", "speech", "NARRATOR", "And he took Mo's low hum.", LINE, "p4"),

    ("p4_sfx_shloop_2", "sfx", "shloop", "", LINE, "p4"),

    ("p4_nar_03", "speech", "NARRATOR",
     "And then, gentle and quick, he took Etta's own word, "
     "in the middle. Like this.", LINE, "p4"),

    ("p4_sfx_shloop_3", "sfx", "shloop", "", BEAT, "p4"),

    ("p4_nar_04", "speech", "NARRATOR",
     "[hushed, the trap closes and nobody notices] "
     "And behind them, so soft that not one of them heard, "
     "he reached out once again. And he took, from the door, "
     "the small click that it made.", LINE, "p4"),

    ("p4_sfx_shloop_4", "sfx", "shloop_soft", "", BEAT, "p4"),

    ("p4_nar_05", "speech", "NARRATOR",
     "And the door was no more. ... "
     "[flat, matter-of-fact] For a door with no click isn't really a door. "
     "It's a wall. It's a wall. It's a wall. Nothing more.", PAGE, "p4"),

    # ══ SPREAD 5 — please ══
    ("p5_nar_01", "speech", "NARRATOR",
     "Now Etta was five, which is old. And she knew "
     "that when somebody's taken a thing that's not theirs, "
     "you say give it back, please. So she said it. She did.", SECTION, "p5"),

    ("p5_etta_01", "speech", "ETTA",
     "[polite, firm, certain this will work] "
     "Give them back. Give them back, please. They're ours.", SECTION, "p5"),

    ("p5_hush_01", "speech", "HUSHABALOO",
     "[genuinely baffled, not refusing] But they're safe. Don't you see? "
     "They are safe here with me. "
     "Nothing's lost. Nothing ever is lost here. Not one. "
     "I have rain from a Tuesday two hundred years gone. "
     "It's still raining. In there. It has never been done.", SECTION, "p5"),

    ("p5_etta_02", "speech", "ETTA",
     "[pressing, exasperated] But a sound isn't safe when it's kept in a...", LINE, "p5"),

    ("p5_sfx_shloop", "sfx", "shloop", "", BEAT, "p5"),

    ("p5_nar_02", "speech", "NARRATOR",
     "[dry, sympathetic] And the word that she needed went off in a jar. "
     "And she opened her mouth. ... And there wasn't a sound.", PAGE, "p5"),

    # ══ SPREAD 6 — Kip climbs, because Kip climbs ══
    ("p6_nar_01", "speech", "NARRATOR",
     "Then Kip sized the shelf up. Now, Kip is quite small. "
     "But of all of the things about Kip, above all...", LINE, "p6"),

    ("p6_kip_01", "speech", "KIP",
     "[flat, obvious, already going] I can get it.", LINE, "p6"),

    ("p6_nar_02", "speech", "NARRATOR",
     "Kip climbs. And Kip climbed. And Kip went "
     "up a shelf, and another, and up, and he leant", LINE, "p6"),

    ("p6_kip_02", "speech", "KIP",
     "[breathless, delighted, three shelves up] Watch me! Watch me!", LINE, "p6"),

    ("p6_nar_03", "speech", "NARRATOR",
     "and he reached for a jar, and he stretched, and he wobbled, and grabbed, and...",
     LINE, "p6"),

    ("p6_kip_03", "speech", "KIP",
     "[pure joy, no fear whatsoever] Uh oh.", LINE, "p6"),

    ("p6_sfx_pop", "sfx", "pop", "", LINE, "p6"),

    ("p6_nar_04", "speech", "NARRATOR",
     "[fast, exhilarated] And the jar came down hard, and the jar came apart, "
     "and out came the rain! All the rain! From the start! "
     "And it went up, and out, and it went through the wall, "
     "to the window it came from, right down the long hall.", SECTION, "p6"),

    ("p6_etta_01", "speech", "ETTA",
     "[discovery, this is information not victory] "
     "It went HOME. Did you see it? It broke and went home!", PAGE, "p6"),

    # ══ SPREAD 7 — the quiet part ══
    ("p7_nar_01", "speech", "NARRATOR",
     "But the Hushabaloo sighed. And he lifted the shelf. "
     "And he put it up high, where a person can't climb. "
     "And he said it so softly, and mostly himself...", SECTION, "p7"),

    ("p7_hush_01", "speech", "HUSHABALOO",
     "[not angry, heartbroken. This must never sound like a threat] "
     "Please don't break them. Please don't. "
     "I have had them a very long time.", SECTION, "p7"),

    ("p7_nar_02", "speech", "NARRATOR",
     "[slow, and slower] And it got very dark. And it got very still. "
     "And the three of them sat. And they sat. And they sat. "
     "And there wasn't a squeak. And there wasn't a drip. "
     "And there wasn't a sound in the world. ... Just like that.", SECTION, "p7"),

    ("p7_kip_01", "speech", "KIP",
     "[small. The first time Kip has been small] I want home.", LINE, "p7"),

    ("p7_mo_01", "speech", "MO", "[smaller] Me too.", SECTION, "p7"),

    ("p7_nar_03", "speech", "NARRATOR",
     "And Etta, who's five, and who plans, and who's brave, "
     "had no plan. And she said it out loud, very small...", LINE, "p7"),

    ("p7_etta_01", "speech", "ETTA",
     "[honest. This is the bottom] I'm scared too.", SECTION, "p7"),

    ("p7_nar_04", "speech", "NARRATOR",
     "[the turn] But then Mo, who hears things that the rest of us miss, "
     "put his hand on a jar. And he listened. Like this.", SECTION, "p7"),

    ("p7_mo_02", "speech", "MO",
     "[quiet, but this is the hinge of the whole book] Etta. ... This one empty.",
     SECTION, "p7"),

    ("p7_etta_02", "speech", "ETTA",
     "[sitting bolt upright] Empty? But he's got a jar for everything.", LINE, "p7"),

    ("p7_nar_05", "speech", "NARRATOR",
     "And Etta's eyes went round and wide.", LINE, "p7"),

    ("p7_etta_03", "speech", "ETTA",
     "[fast, building, the idea arriving in real time] "
     "He's got jars for the rain and the drip and the door, "
     "for the sounds that things MAKE. But he hasn't got more! "
     "He's got nothing at all for a sound that's not FOR "
     "anything! Nothing! He's not heard one before! ... "
     "[turning to her brothers, absolutely serious] Kip. Mo. On three. ... "
     "Do the rudest thing you know.", PAGE, "p7"),

    # ══ SPREAD 8 — the rudest thing they know ══
    ("p8_nar_01", "speech", "NARRATOR",
     "[fast, all three at once] So Kip climbed. Because Kip climbs. "
     "And Mo found the jar, because Mo always finds them. "
     "That's just what Mo does. And Etta said...", LINE, "p8"),

    ("p8_etta_01", "speech", "ETTA", "[big] THREE. TWO. ONE...", LINE, "p8"),

    ("p8_nar_02", "speech", "NARRATOR",
     "and the twins, who were two, "
     "did the one thing that two-year-old people do best.", 0.0, "p8"),

    ("p8_wait_01", "wait", "3.0", "", 0.0, "p8"),

    ("p8_kipmo_01", "speech", "KIP",
     "[with absolutely everything she has] PBBBBBBBBT!", 0.0, "p8"),

    ("p8_sfx_raspberry", "sfx", "raspberry_big", "", BEAT, "p8"),

    ("p8_nar_03", "speech", "NARRATOR",
     "[building. This is the thesis and it must land] "
     "And it wasn't a squeak. And it wasn't a drip. "
     "And it wasn't the rain, and it wasn't a door. "
     "It was nothing! It meant nothing! It came from a lip "
     "and it went nowhere useful, a wonderful roar "
     "of a silly, wet, pointless, ridiculous noise "
     "that had no jar at all.", SECTION, "p8"),

    ("p8_nar_04", "speech", "NARRATOR",
     "[slower, almost tender] And he looked for a jar. "
     "And he looked. And he looked. And he looked down the hall "
     "of ten thousand jars... and there wasn't one. Not one. "
     "Not a label. Not one. Not at all. Not a jar.", BEAT, "p8"),

    ("p8_nar_05", "speech", "NARRATOR",
     "And a thing with no jar is a thing you can't keep.", LINE, "p8"),

    ("p8_sfx_cascade", "sfx", "pop_cascade", "", LINE, "p8"),

    ("p8_nar_06", "speech", "NARRATOR",
     "[joyful, headlong] And the empty jar popped. And the next. And the next. "
     "And the rain and the dog and the kettle and drip "
     "and the whumpf and the hum and the squeak of the stair "
     "went UP, and went OUT, and went HOME through the air.", PAGE, "p8"),

    # ══ SPREAD 9 — click ══
    ("p9_nar_01", "speech", "NARRATOR",
     "[from the roar, down to almost nothing] "
     "And in all of that noise, in that whole rushing flood, "
     "there was one little sound that was smaller than most.", SECTION, "p9"),

    ("p9_mo_01", "speech", "MO",
     "[perfectly calm. Of course he heard it] Listen. ... There.", SECTION, "p9"),

    ("p9_nar_02", "speech", "NARRATOR",
     "And Mo heard it. Of course. Because that's what Mo does. "
     "And he pointed. And there, in the dark, was a...", LINE, "p9"),

    ("p9_sfx_click", "sfx", "click", "", BEAT, "p9"),

    ("p9_nar_03", "speech", "NARRATOR",
     "click. And a door with a click is a door once again.", SECTION, "p9"),

    ("p9_nar_04", "speech", "NARRATOR",
     "But they stood in the doorway. And turned. And they saw "
     "that the Hushabaloo hadn't got anything more. "
     "He had shelves. He had jars. He had none of them full. "
     "And he sat down. And he was extremely small.", SECTION, "p9"),

    ("p9_etta_01", "speech", "ETTA", "Wait.", LINE, "p9"),

    ("p9_nar_05", "speech", "NARRATOR",
     "And she walked all the way back, and stood by his knee.", LINE, "p9"),

    ("p9_etta_02", "speech", "ETTA",
     "[gentle. The kindest line in the book] "
     "You can keep it. That one. That one's from me.", LINE, "p9"),

    ("p9_nar_06", "speech", "NARRATOR",
     "And she blew him a raspberry, right through the air.", LINE, "p9"),

    ("p9_sfx_raspberry", "sfx", "raspberry_small", "", LINE, "p9"),

    ("p9_nar_07", "speech", "NARRATOR",
     "And he caught it. And held it. And kept it. Right there. "
     "And he put it in nothing. No jar and no lid. "
     "Just held it, which is, I suppose, what you do "
     "with a sound that was given and not taken. ... He did. "
     "And he smiled. If a Hushabaloo can. And he knew.", SECTION, "p9"),

    ("p9_nar_08", "speech", "NARRATOR",
     "[home. Warm, and slowing all the way down] "
     "So they went down the hall to the house that was theirs, "
     "where the kettle had a song, and a squeak had the stairs, "
     "where the pipes gave a knock, and the tap gave a drip, "
     "and the dog gave a whumpf...", LINE, "p9"),

    ("p9_sfx_click_home", "sfx", "click", "", BEAT, "p9"),

    ("p9_nar_09", "speech", "NARRATOR",
     "and the door gave a click.", PAGE, "p9"),

    # ══ FINAL ══
    ("final_nar_01", "speech", "NARRATOR",
     "[quiet, direct, to the listener] For everybody small who was ever once told "
     "to be quiet, be quiet, be quiet, be still... "
     "here's a story where noise is the thing that saves all.", SECTION, "final"),

    ("final_nar_02", "speech", "NARRATOR",
     "[warm, and then waiting] Go on. ... Make the sound. You know the one.",
     0.0, "final"),

    ("final_wait_01", "wait", "4.0", "", 0.0, "final"),

    ("final_sfx_raspberry", "sfx", "raspberry_big", "", PAGE, "final"),
]

# ── Participation ─────────────────────────────────────────────────────────────
# A `wait` block NEVER blocks. It pauses for its duration, then the story continues
# whether or not anyone made a sound. Two reasons, and they agree:
#
#   * House rule: the book auto-advances. It is never stuck waiting for input.
#   * Blue's Clues' pause is "long enough for the youngest, short enough for the
#     oldest," after which another voice supplies the answer anyway. See
#     research/01-developmental-psychology.md.
#
# So the 3s wait on spread 8 is followed by Kip and Mo doing it regardless -- the
# listeners are invited, never required, and never left hanging.

SPREADS = ["cover", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9", "final"]
