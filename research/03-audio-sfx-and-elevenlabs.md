# Sound Design + ElevenLabs API Research
### For a narrated children's audiobook (audience: 2-year-old twins + 5-year-old; iPad/phone/laptop, often at bedtime)
Compiled 2026-08-01. All claims cited inline; items I could not verify from a primary source are flagged in **Risks & Gotchas** and inline as `[UNVERIFIED]`.

---

## EXECUTIVE SUMMARY

### The sound design spec (concrete numbers to build to)

| Parameter | Daytime / adventure mode | Bedtime mode |
|---|---|---|
| Integrated loudness (narration master) | −18 LUFS integrated | −20 to −23 LUFS integrated |
| True peak ceiling | −3 dBTP (never exceed −1 dBTP) | −3 dBTP |
| Loudness range (LRA) | ≤ 10–12 LU | ≤ 6–8 LU (compress harder) |
| Max SFX transient jump above narration RMS | +6 dB, and only with attack ≥ 30–50 ms (no <10 ms clicks/bangs) | +3 dB max; prefer no surprise SFX at all in the final chapter |
| Pre-roll before any "big" SFX | 150–300 ms rising anticipation swell | mandatory, longer (300–500 ms), softer |
| SFX density in active scenes | ~1 meaningful effect per 10–20 s (~3–5/min), synthesized craft guideline — **not** a documented industry standard (see §4 and Risks) | drop to near-zero; ambient bed only |
| Music bed under narration | −18 to −24 dB below narration peak; for the 2-year-olds, default to **no music under active narration**, music only in transitions | −24 to −30 dB, slow (<70 BPM), no lyrics |
| Ambient atmosphere bed (non-music) | −24 to −30 dB below narration, high-pass at 150–200 Hz | same, lower still |
| Narration EQ | gentle +2–3 dB presence boost at 2–4 kHz | same, no boost above 8 kHz |
| SFX/bed EQ carving | cut 2–4 kHz in beds/SFX by 2–3 dB so voice presence band stays clear; high-pass ambient beds at 150–200 Hz | same |
| Target playback assumption | WHO safe-listening: ≤ 80 dB SPL average, device volume ≤ 60% of max, prefer built‑in speakers over headphones for young children [who.int](https://www.who.int/news-room/questions-and-answers/item/deafness-and-hearing-loss-safe-listening) | same |
| Signature "adventure starts" cue | ONE fixed 2–4 s sound, unchanged take-to-take, always at the same story beat | keep if used, but bedtime episodes may drop it entirely |

### What the ElevenLabs API can / can't do (2026)

| Capability | Can | Can't / caveat |
|---|---|---|
| TTS with character-level timestamps | Yes. `text_to_speech.convert_with_timestamps()` (single voice; endpoint default model `eleven_multilingual_v2`, override with `model_id`) or `text_to_dialogue.convert_with_timestamps()` (multi-speaker; default `eleven_v3`). Both return `character_start_times_seconds` / `character_end_times_seconds` arrays. [elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps](https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps) | Alignment accuracy depends on clean audio + clear punctuation; `eleven_v3`'s expressive pacing/tags plausibly reduces alignment precision vs. Flash/Multilingual v2 — not documented either way `[UNVERIFIED]` |
| Expressive narration with emotional direction | `eleven_v3` is GA (not alpha, not deprecated), honors inline bracket **audio tags** like `[whispers]`, `[excited]`, `[giggles]`, 70+ languages [elevenlabs.io/blog/v3-audiotags](https://elevenlabs.io/blog/v3-audiotags) | No SSML `<break>` tag support in v3 — use tags/ellipses for pacing instead; tag adherence is probabilistic, expect to regenerate some lines |
| Sound effects generation | `text_to_sound_effects.convert()` — up to **30.0 s hard cap** per call, `prompt_influence` 0–1 (default 0.3), `loop=True` for seamless ambient loops (only on `eleven_text_to_sound_v2`) [elevenlabs.io/docs/api-reference/text-to-sound-effects/convert](https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert) | Cannot generate a single clip longer than 30 s — for a longer ambient bed you must generate a 30 s (or shorter) **loop** and repeat it in code/DAW, not one long render |
| Child-sounding character voice | Voice Library has "youthful" / "playful" / "squeaky" **adult-performed** voices [elevenlabs.io/voice-library/youthful](https://elevenlabs.io/voice-library/youthful); Voice Design (text-to-voice) can attempt a young-sounding voice from a text prompt | Genuinely **child-like/children's voices are explicitly barred from the public Voice Library**, for both real minors' voices and adult voices designed to mimic children [help.elevenlabs.io article, via search excerpt — primary page 403'd for direct fetch] `[UNVERIFIED primary source]`. Cloning a real child (e.g., your own daughter/twins) is ToS-gated: users under 13 cannot use the service at all, 13–18 requires guardian consent, and any voice replication requires "consent or legal right" [elevenlabs.io/use-policy](https://elevenlabs.io/use-policy) — treat cloning your kids' actual voices as high-risk/likely against policy intent; do not do it without direct legal review |
| Batch job (~60–100 short clips) | Feasible on Creator/Pro tier with a concurrency-aware queue + 429 backoff | Concurrency is capped per plan; secondary sources report **Creator ≈ 5 concurrent, Pro ≈ 10 concurrent** for TTS [drdroid.io](https://drdroid.io/integration-diagnosis-knowledge/elevenlabs-concurrent-request-limit-exceeded) — **I could not confirm this from the primary ElevenLabs help-center page** (it 403'd for automated fetch) `[UNVERIFIED — reverify against account dashboard or support before relying on it]` |
| Python SDK | `pip install elevenlabs`, `from elevenlabs.client import ElevenLabs` | Could not confirm the exact current pinned version number on PyPI from this research pass `[UNVERIFIED]` — run `pip install -U elevenlabs` and check `pip show elevenlabs` before the batch job |

---

# PART A — CHILDREN'S AUDIO SOUND DESIGN

## 1. Loudness and dynamic range

**Safe listening levels (hearing-health guidance, not mix-engineering guidance):**
- WHO: sound levels **below 80 dB are unlikely to cause hearing damage**; at 80 dB average, safe listening is up to **40 hours/week**; at 90 dB, that drops to **4 hours/week**; at 85 dB → 12h30m/week; 95 dB → 1h15m/week; 100 dB → 20 min/week. WHO explicitly recommends keeping device volume **at or below 60% of maximum**, and for children specifically: prefer **built-in or external speakers over headphones where possible**, and use well-fitted, ideally noise-cancelling headphones with volume-limiting when headphones are used, with regular breaks in a quiet space. [WHO Safe Listening Q&A](https://www.who.int/news-room/questions-and-answers/item/deafness-and-hearing-loss-safe-listening); [WHO-ITU Safe Listening Devices and Systems standard](https://www.who.int/publications-detail/safe-listening-devices-and-systems-a-who-itu-standard); [WHO Make Listening Safe brochure (PDF)](https://cdn.who.int/media/docs/default-source/documents/health-topics/deafness-and-hearing-loss/mls-brochure-english-2021.pdf)
- Secondary summaries of AAP guidance describe a **"60/60 rule"**: volume ≤ 60% of max, sessions ≤ 60 minutes, then a 15-minute break; AAP's 2023 policy statement on excessive noise exposure in infants/children frames the practical goal as making headphone use "as safe as possible" (device-level volume limiting, parental controls) given that some headphone use is now unavoidable for schooling. **The AAP primary article (`publications.aap.org`) returned HTTP 403 on automated fetch, so this is relayed via secondary sources, not directly quoted from the peer‑reviewed text** `[UNVERIFIED primary source]`. [AAP News summary](https://publications.aap.org/aapnews/news/26437/New-AAP-policy-technical-report-offer-advice-on); [Stanford Children's Health blog](https://healthier.stanfordchildrens.org/en/preventing-hearing-loss-in-kids-beware-of-unsafe-listening-habits-during-video-gaming-and-other-activities/); [iClever 85dB guide](https://iclever.com/blogs/child-s-growth/the-complete-guide-to-hearing-safe-kids-headphones-why-85db-matters); [ATA](https://www.ata.org/protecting-young-people-from-noise-induced-hearing-loss/)
- Practical takeaway for this project: **the mix itself can't enforce device volume**, but design choices should assume the device may be near max volume on a small phone/tablet speaker with a 2-year-old holding it close to their ear — so err toward a *quieter, more compressed* master than a "cinematic" one.

**LUFS targets for spoken-word / audiobook:**
- Audible/ACX's underlying spec is **RMS between −23 and −18 dB**, peak no higher than −3 dB, noise floor below −60 dB RMS (ACX historically speaks in RMS, not LUFS, but is commonly translated to roughly **−18 LUFS integrated** in modern tooling). [Auphonic — RMS Loudness Normalization for Audible/ACX](https://auphonic.com/blog/2026/01/15/rms-loudness-normalization-for-audible-acx/); [Narration Box mastering guide](https://narrationbox.com/blog/audiobook-mastering-rms-lufs-noise-floor-acx-guide); [HumanizeAudio](https://blog.humanizeaudio.com/audiobook-mastering-levels-rms-lufs/)
- General spoken-word audiobooks commonly land **−19 to −16 LUFS integrated**; comfortable spoken-word range is described as roughly **−18 to −21 LUFS**. Podcasts skew a bit louder: Apple Podcasts recommends **≈ −16 LUFS integrated**. [Gearspace mastering forum](https://gearspace.com/board/mastering-forum/1375667-target-mastering-loudness-spoken-word-poetry.html); [Hanna Eng LUFS guide](https://www.hanna-eng.com/guides/audio-loudness-lufs/); [Violet Recording podcast loudness](https://violetrecording.com/podcast-loudness-lufs-standards/)
- **Recommendation for this project**: target **−18 LUFS integrated / −3 dBTP** for daytime, **−20 to −23 LUFS / −3 dBTP** for bedtime content, sitting comfortably inside the audiobook norm but pulled quieter and with a tighter loudness range for bedtime.

**Why heavy compression matters on tiny speakers:** phone/tablet/laptop speakers have far less headroom and dynamic range than studio monitors or even decent headphones; a wide-dynamic-range mix will either bury quiet narration under phone-speaker noise floor or blast the loud parts through speaker distortion. Tight dynamic range (high average loudness, low LRA) is standard practice for small-speaker/podcast delivery specifically because of this — one clear, consistent finding across mixing-guide sources. [Journalism University EQ/mixing guide](https://journalism.university/audio-podcast/equalising-sound-mixing-professional-audio/); [Sound Radix — mixing dialogue in audio storytelling](https://www.soundradix.com/articles/mixing-dialogue-in-audio-storytelling/)

## 2. Startle response

**What causes it (general child-development / audiology literature, not audio-production-specific):**
- The startle/Moro reflex is a brainstem-level defensive reaction to *sudden or unexpected* stimuli — sharpness/suddenness of onset matters more than raw loudness. In infants it manifests as flailing/crying and usually fades by 5–6 months, but many young children continue to show marked dislike/anxiety toward loud or unexpected sounds well beyond infancy. [Wikipedia — Startle response](https://en.wikipedia.org/wiki/Startle_response); [WebMD — Moro Reflex](https://www.webmd.com/baby/what-is-the-moro-reflex); [NHS Gloucestershire — Sound sensitivity in children](https://www.gloshospitals.nhs.uk/your-visit/patient-information-leaflets/sound-sensitivity-children-ghpi1602/); [JLD Therapy — startle reflex in babies](https://jldtherapy.com/everything-you-need-to-know-about-the-startle-reflex-in-babies/); [Lovevery — helping toddlers cope with loud noises](https://blog.lovevery.com/child-development/5-tips-to-help-your-toddler-cope-with-loud-noises/)
- **I could not find a peer-reviewed or industry-published numeric threshold** (e.g., "a jump of X dB in Y ms triggers startle in toddlers") specific to recorded audio content for children. What follows are **synthesized best-practice rules**, not a verified standard — extrapolated from (a) the general startle-reflex literature's emphasis on *suddenness/sharpness of onset* over absolute level, and (b) standard broadcast-audio practice around avoiding jarring loudness jumps. `[UNVERIFIED as a pediatric-audio-specific standard]`

**Concrete rules to be "exciting" without "scary" (synthesized):**
1. **Cap the jump, not just the peak.** No SFX or musical hit should exceed the current program RMS by more than **+6 dB** in daytime content, **+3 dB** at bedtime — measured over a short window, not just instantaneous peak.
2. **Soften the attack.** Avoid true broadband transients with attack times under ~10 ms (the "bang"/"clap"/"gunshot" shape). Give hits a **30–50 ms rise** — even a fast whoosh-in or swell reads as "exciting" without the click-transient shock of an unshaped hit.
3. **Pre-roll everything big.** A **150–300 ms rising anticipation cue** (a swell, a rising whoosh, a "here it comes" musical gesture) before any surprising sound gives a young child's auditory system a ramp instead of a cliff. This is standard scoring practice (the "sting" is preceded by a rise) and maps directly onto reducing perceived suddenness.
4. **Roll off the extremes on impact sounds.** High-pass below ~100 Hz and low-pass above ~10 kHz on "big" hits — full-bandwidth transients read as harsher/scarier than band-limited ones at the same loudness.
5. **Never combine "loud" with "sudden" with "unfamiliar."** A loud-but-expected sound (the signature whoosh they've heard 20 times) is exciting; a loud, sudden, novel sound is what triggers startle/fear. Reuse familiar SFX for high-energy moments; save genuinely novel sounds for quiet, gentle presentation.

## 3. Bedtime vs. daytime listening

- Purpose-built children's sleep-story products calibrate **every element — pacing, tone, language, music, story arc — to reduce arousal**: the narrator never raises their voice, tension is minimal, drama is essentially absent, and the goal is sleep onset, not excitement. [Clear Minds — Sleep Stories for Kids 2026 guide](https://clearminds.com/blogs/interesting-reads/sleep-stories-for-kids-the-complete-parents-guide-to-bedtime-audio-in-2026)
- Children as young as **18 months–2 years** can benefit from simple, calm audio at bedtime, where the narrator's tone matters more than plot content — reinforcing that for the 2-year-old twins specifically, *voice quality and steadiness* carry more weight than sound-design cleverness. [Clear Minds guide, same source]
- Feasibility/acceptability research on audio-based sleep aids for parent-child sleep health exists as a formal study (PMC), and the broader "Sonic Sleep Aids" literature (Oxford/SLEEP journal) categorizes bedtime audio into sleep music, ambient/nature soundscapes, bedtime stories, and guided-relaxation content, noting **music-based relaxation has demonstrated efficacy for sleep quality**, while evidence for ambient/nature sounds specifically is **inconclusive**. [PMC — Out Like a Light feasibility study](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9368592/); [Oxford SLEEP — Between sound and sleep: Sonic Sleep Aids](https://academic.oup.com/sleep/article/48/11/zsaf275/8251384)
- Practical volume guidance from sleep-sound sources: **~30 dB** for a purely soothing presence without masking the room, **40–50 dB** if actively masking background/household noise during sleep. [Good Night Sleep Site — sound machine safety](https://goodnightsleepsite.com/2024/06/24/sound-machine-safety/)
- **Design implication**: bedtime chapters should be a genuinely different mix, not just "the same mix, quieter" — tighter LRA, no startle-risk SFX at all, slower tempo beds (<70 BPM if music is used), and a narrator performance that stays level rather than building to excited peaks.

## 4. SFX density — children's audio drama craft guidance

- I searched specifically for **numeric SFX-density production guidelines from BBC, Sesame Workshop, Pinna, Wow in the World, and Circle Round** and **could not find any publicly published numeric standard** (e.g., "N effects per minute") from any of these producers. What is publicly available is qualitative: Wow in the World is described as featuring "immersive sound design" and episodes designed to be "visualized with your eyes closed"; Circle Round is described as turning folktales into "sound- and music-rich radio plays," crediting a dedicated sound designer/composer (Eric Shimelonis) and named sound designers on crossover episodes (Mira Burt-Wintonick, Joe Plourde). [Wow in the World — Apple Podcasts](https://podcasts.apple.com/us/podcast/wow-in-the-world/id1233834541); [WBUR Circle Round](https://www.wbur.org/circleround/2025/11/18/turkey-got-its-gobble); [Radiolab for Kids — podcast crossover](https://radiolab.org/podcast/a-podcast-turducken-with-wow-in-the-world-terrestrials-and-circle-round); [NPR — Wow in the World presents Circle Round](https://www.npr.org/2019/10/31/775218577/wow-in-the-world-presents-circle-round-the-chattering-clams) — `[No numeric density standard found — treat any specific "X effects/minute" figure as inferred/synthesized, including the one in this doc's Executive Summary]`
- General audio-drama/podcast production guidance (not children-specific) does converge on a qualitative principle that's directly relevant: **SFX should support comprehension by marking scene/action changes, not decorate every line** — over-scoring masks narration and adds cognitive load; under-scoring leaves the story audio-flat. This is consistent with (and likely the origin of) common craft advice to place SFX at **scene entrances/exits, key actions, and emotional beats**, with quiet, effect-free stretches for dialogue-heavy narration.
- **Ducking**: standard practice is to duck any bed/SFX under overlapping narration via sidechain compression or manual automation, with EQ carving (cut the bed's energy in the narrator's core frequency range) as a complementary, non-destructive technique. [Sound Radix — mixing dialogue in audio storytelling](https://www.soundradix.com/articles/mixing-dialogue-in-audio-storytelling/); [SFX Engine — VO sound effects tips 2026](https://sfxengine.com/blog/voice-over-sound-effects-tips)
- **Recommendation**: adopt the synthesized ~3–5 effects/minute density as a *starting point*, but validate empirically by listening with the actual 2- and 5-year-old audience — this number has no external authority behind it.

## 5. Participatory sound — signature/anticipation cues

- Developmental literature on infant/child auditory pattern perception establishes that children **build expectations from repeated audio patterns** and can use probabilistic/contextual cues to anticipate upcoming sounds — evidenced by studies on infants' rhythmic audiovisual synchrony attention and children's (ages 7–9) reduced orienting response to sounds once a pattern becomes predictable (via pupil dilation/ERP measures). This is the developmental mechanism a "signature sound" exploits: repetition turns a sound into a *reliable cue* the child can anticipate and eventually vocally/physically imitate. [Frontiers — Developmental origins of natural sound perception](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2024.1474961/full); [Tandfonline — probabilistic cues, pupil dilation & ERP in 7–9-year-olds](https://www.tandfonline.com/doi/full/10.1080/25742442.2022.2048592); [Frontiers — infant attention to rhythmic audiovisual synchrony](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2024.1393295/full)
- An arXiv paper on Disney-inspired scaffolds for child-AI interaction design references **leitmotifs and sound effects as tools to cue emotional responses that are "emotionally expressive, developmentally salient, and tightly synchronized with visual/narrative shifts"** — supporting the design instinct behind a recurring, unchanging cue, though I was only able to retrieve this via search-result summarization; **the PDF itself would not extract cleanly for direct quotation** `[UNVERIFIED — could not directly read primary source text]`. [arXiv 2504.08670 — Once Upon an AI](https://arxiv.org/pdf/2504.08670)
- **Design implication (well-supported by the general mechanism, if not by a named children's-audio study)**: pick ONE unchanging sound (~2–4 s) for "the adventure starts," place it at the identical story beat every time, and resist the temptation to vary it for freshness — the repetition *is* the feature. The same logic applies to a "helper found something!" chime, a per-character motif, etc. — consistency lets the child anticipate and eventually imitate it, which is the entire developmental payoff.

## 6. Music — ambient beds / leitmotifs, comprehension effects by age

- An EEG study on children aged 5–7 found their **general alerting/arousal level was significantly higher in the condition WITHOUT background music or noise**, with a significant interaction between background music and background noise on alertness — i.e., background music measurably changes children's alertness state, not just their enjoyment. **I could not fetch the primary ScienceDirect article directly (403); this is relayed from a search-engine summary of the abstract** `[UNVERIFIED primary source]`. [ScienceDirect — background music/noise and alertness in 5–7 year olds](https://www.sciencedirect.com/science/article/abs/pii/S0885201422001435)
- Auditory/musical discrimination is still maturing across this age range: at **age 2, children show immature neural responses (pMMR)** to changes in melody/rhythm/tuning/timbre, shifting toward more adult-like discrimination (MMN-like response) by around **age 6**. Practical reading: a 2-year-old is much less equipped to "parse around" competing musical/narration streams than a 5-year-old is — supporting **less or no music under narration for the 2-year-olds**, more tolerance for it with the 5-year-old. [Nature Scientific Reports — musical playschool activities and auditory development](https://www.nature.com/articles/s41598-019-47467-z)
- A related finding (screen-based, not audio-only, so apply with caution): **hyperconnectivity during screen-based story listening was associated with LOWER narrative comprehension** in preschoolers compared to dialogic reading — a general caution that richer, more "connected"/busy audio-visual stimulation doesn't automatically help comprehension and can compete with it. [PMC — hyperconnectivity and narrative comprehension in preschoolers](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6874384/)
- A systematic review of background music in preschool/primary education found **positive impacts on cognitive/socio-emotional development in preschool settings**, with the primary-school-age benefits more specifically tied to reading comprehension and task performance — but also notes **active music participation produces much stronger developmental benefits than passive background listening**, and background music's effect is context- and task-dependent, not uniformly positive. [Systematic review — background music in preschool/primary education](https://journals.um.si/index.php/education/en/article/view/5528); [Music Scientist Singapore — music & language development birth–6](https://www.themusicscientist.com/music-and-language-development-evidence-across-birth-to-age-6/)
- **Design implication**: treat music-under-narration as **age-gated**, not universal — safe default is instrumental-only (no lyrics), low level (−18 to −24 dB under narration), and for the 2-year-old audience, prefer music in **transitions/non-verbal beats only**, not simultaneous with active narration.

## 7. Practical mixing recipe

- **Speech frequency range**: male voices roughly 200–6,500 Hz, female voices roughly 400–8,000 Hz; intelligibility/"presence" concentrates in the **2–4 kHz** band — a gentle +2–3 dB boost there brings narration forward without harshness. [Behind The Mixer — EQ speech for max intelligibility](https://www.behindthemixer.com/how-eq-speech-maximum-intelligibility/); [Larry Jordan — channel EQ for narration](https://larryjordan.com/articles/channel-eq-makes-narration-sound-great/)
- **Frequency carving**: use EQ to *remove* competing energy from beds/SFX in the narrator's core bands rather than only boosting the narrator — e.g., if the narrator's vocal body sits around 250 Hz, cut that same region slightly in ambient/music beds; cut clashing content out of SFX generally. [Journalism University — equalising & mixing](https://journalism.university/audio-podcast/equalising-sound-mixing-professional-audio/)
- **Level recipe** (converging across sources): background music **18–20 dB lower than speech** as a floor recommendation; ambient/ducking sources recommend combining EQ carving with sidechain ducking and automation as complementary (not either/or) techniques. [Pure Audio Insight — background music volume](https://pureaudioinsight.com/blogs/content-production/background-music-volume-how-loud-should-it-be); [SFX Engine — VO/SFX tips 2026](https://sfxengine.com/blog/voice-over-sound-effects-tips)
- **Applied recipe for this project**:
  - Narration: reference 0 dB, gentle 2–4 kHz presence boost, high-pass below ~80–100 Hz to remove rumble/plosive thump.
  - SFX (story-relevant, foreground): peaks −3 to −6 dB relative to narration peak; ducked further (−6 to −10 dB additional) whenever overlapping spoken lines.
  - Music bed: −18 to −24 dB below narration peak, high-passed at 150–200 Hz, 2–4 kHz gently cut to stay out of the narrator's presence band.
  - Ambient atmosphere (non-musical bed, e.g. forest/rain): −24 to −30 dB, same high-pass treatment, essentially "felt, not heard" under dialogue.

---

# PART B — ELEVENLABS TECHNICAL CAPABILITY (2026)

## 8. Text-to-Speech models + timestamps

**Current models** (per `elevenlabs.io/docs/overview/models`):

| Model ID | Description | Languages | Char limit | Notes |
|---|---|---|---|---|
| `eleven_v3` | Most expressive/human-like; GA (out of alpha), not deprecated | 70+ | 5,000 `[UNVERIFIED — single-source figure, reverify before relying on it for chunking logic]` | Best for expressive narration; supports audio tags |
| `eleven_multilingual_v2` | "Most lifelike," rich emotional expression | 29 | 10,000 | Default model for the plain `/with-timestamps` TTS endpoint |
| `eleven_flash_v2_5` | Ultra-fast, ~75 ms latency (excl. network) | 32 | 40,000 | ~50% lower per-character cost; best for real-time, not narration nuance |
| `eleven_flash_v2` | Fast, English only | English | 30,000 | — |

**Deprecated**: `eleven_monolingual_v1` and `eleven_multilingual_v1` are removed **2026-07-09** — migrate to `eleven_multilingual_v2` or newer. `eleven_turbo_v2`/`eleven_turbo_v2_5` are effectively superseded by the Flash equivalents (lower latency, same/better results) though not confirmed as hard-removed. [elevenlabs.io/docs/changelog/2026/6/8](https://elevenlabs.io/docs/changelog/2026/6/8); [elevenlabs.io/docs/overview/models](https://elevenlabs.io/docs/overview/models)

**Timestamps — two distinct endpoints, easy to conflate**:
1. `POST /v1/text-to-speech/{voice_id}/with-timestamps` — single voice. Body: `text` (required), `model_id` (**defaults to `eleven_multilingual_v2`**, override to use `eleven_v3`), `language_code`, `voice_settings`, `apply_text_normalization`, `seed`, `pronunciation_dictionary_locators` (max 3). Response: `{ audio_base64, alignment: { characters[], character_start_times_seconds[], character_end_times_seconds[] }, normalized_alignment: {...} }`. [API reference](https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps)
2. `POST /v1/text-to-dialogue/with-timestamps` — multi-speaker dialogue. **Defaults to `eleven_v3`**, returns the same style of character-level alignment metadata, intended for auto-subtitles/karaoke/lip-sync/talking-avatar use cases. [API reference](https://elevenlabs.io/docs/api-reference/text-to-dialogue/convert-with-timestamps); [stream variant](https://elevenlabs.io/docs/api-reference/text-to-dialogue/stream-with-timestamps)

**Best model for expressive narration with timestamps**: **`eleven_v3`**, explicitly called out as the default for the dialogue-with-timestamps endpoint and the current top-of-line expressive model. Caveat: alignment accuracy generally "depends on audio quality... clear speech and minimal background noise produce word-level precision within milliseconds," and **punctuation/clear sentence boundaries improve rhythm and alignment accuracy** — so keep script punctuation clean going in. No source explicitly confirms or denies degraded alignment quality specifically *because of* v3's expressive tag-driven delivery — flagged `[UNVERIFIED]`. [Best practices doc](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)

## 9. Audio tags / emotional direction

- Audio tags are **bracketed, natural-language performance cues** — `[laughs]`, `[gasps]`, `[excited]`, `[whispers]`, `[sighs]`, `[shouts]`, `[softly]`, accents, etc. — read as **direction, not spoken text**, honored specifically by **`eleven_v3`**. [elevenlabs.io/blog/v3-audiotags](https://elevenlabs.io/blog/v3-audiotags)
- Syntax: place the tag immediately before the passage it should affect, e.g. `[excited] This is the product that changes everything. [whispers] Don't tell anyone I told you this.` Multiple tags can be combined/layered in one sentence. [jonathanmast.com v3 audio tags guide](https://jonathanmast.com/elevenlabs-v3-audio-tags-user-guide-mastering-emotional-voice-control/); [elevenlabs.io/blog/eleven-v3-situational-awareness](https://elevenlabs.io/blog/eleven-v3-situational-awareness)
- v3's architecture reads context more deeply than earlier models, following emotional cues/tone shifts/speaker transitions **without a separate parameter/setting** — it's driven entirely by the bracketed text and surrounding prose. [elevenlabs.io/blog/eleven-v3-audio-tags-expressing-emotional-context-in-speech](https://elevenlabs.io/blog/eleven-v3-audio-tags-expressing-emotional-context-in-speech)
- **Known caveat**: v3 **does not support SSML `<break>` tags** or the rest of the SSML tag set — use tag/prose-based pacing techniques instead (e.g., ellipses, explicit pacing tags) for pause control. [Best practices doc](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)
- Practical caveat for a bedtime-audiobook pipeline: tag adherence is **probabilistic**, not guaranteed — budget for spot-checking/regenerating lines where the emotional read didn't land, especially for tags used sparingly.

## 10. Sound effects API

- Python SDK method: **`client.text_to_sound_effects.convert(...)`**, returns `Iterator[bytes]` (sync) or `AsyncIterator[bytes]` (async) — i.e., a streamed/chunked audio response, not a single blob or base64 string. [GitHub source](https://github.com/elevenlabs/elevenlabs-python/blob/main/src/elevenlabs/text_to_sound_effects/client.py)
- **Exact parameters** (from the live API reference):
  - `text` (required, string) — the sound description.
  - `model_id` (optional) — defaults to `eleven_text_to_sound_v2`.
  - `duration_seconds` (optional, number|null) — **must be between 0.5 and 30**; omit for auto-detected duration based on the prompt.
  - `prompt_influence` (optional, number, 0–1, default **0.3**) — higher = follow the prompt more literally; lower = more creative variation.
  - `loop` (optional, boolean, default `false`) — creates a **seamlessly loopable** effect; **only available on `eleven_text_to_sound_v2`**.
  - `output_format` (query param) — `codec_samplerate_bitrate`, e.g. `mp3_44100_128`; supports mp3 (several sample-rate/bitrate combos), pcm (8k–48k), ulaw_8000, alaw_8000, opus_48000 (several bitrates). [API reference](https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert)
- **Loopable ambient beds**: yes, via `loop=True` + `model_id="eleven_text_to_sound_v2"` — this is the mechanism to build the ambient forest/rain/adventure beds described in Part A. **Max single-call duration is still capped at 30 s even for loop-mode** — for a longer bed, generate one clean loop and repeat it programmatically (in your audio pipeline, not via the API) rather than requesting a longer render.
- **Pricing/credit cost — conflicting figures found, not reconciled**: one source states **40 credits per second when `duration_seconds` is explicitly specified** (undocumented cost when auto-determined); a separate pricing-aggregator source states a flat **200 credits per generation**. `[UNVERIFIED / CONFLICTING — do not budget a 60–100-clip batch against either number without confirming against your live ElevenLabs account/credit balance with one test call first]`
- Minimal working example (from the official cookbook): `elevenlabs.text_to_sound_effects.convert(text="Cinematic Braam, Horror")` with no other parameters — duration auto-detected. [Cookbook](https://elevenlabs.io/docs/eleven-api/guides/cookbooks/sound-effects)

## 11. Voice options for child-sounding characters

- **Voice Library**: has tag-filtered adult-performed categories useful for "young-sounding" characters — "Squeaky," "Playful," "Youthful" — explicitly marketed for cartoons/kids' content. [voice-library/squeaky-voices](https://elevenlabs.io/voice-library/squeaky-voices); [voice-library/playful](https://elevenlabs.io/voice-library/playful); [voice-library/youthful](https://elevenlabs.io/voice-library/youthful)
- **Explicit policy**: per a help-center article title/summary (the article itself 403'd on direct fetch, so this is via search-engine excerpt, `[UNVERIFIED primary source]`): **children's voices or voices that sound child-like cannot be added to the (public) Voice Library — this applies both to real minors' voices and to adult voices designed to mimic/sound like children**, specifically to align with the Prohibited Use Policy's child-safety provisions. [help.elevenlabs.io article (title only verified)](https://help.elevenlabs.io/hc/en-us/articles/30183901911313-Can-Children-s-or-Child-Like-Voices-Be-Added-to-the-Voice-Library)
- **Voice Design (text-to-voice)**: generates a *new* synthetic voice from a text prompt via `/v1/text-to-voice` — you generate several previews, pick a `generated_voice_id`, then create a persistent voice from it usable through normal TTS. This is a **private** voice creation flow (not automatically published to the shared Library), so it is a plausible route to a young-sounding **original/synthetic** character voice, though whether ElevenLabs' automated content moderation would still reject a prompt that too closely targets "child voice" is not documented either way `[UNVERIFIED]`. [Voice Design quickstart](https://elevenlabs.io/docs/eleven-api/guides/how-to/voices/voice-design); [Create a voice — API ref](https://elevenlabs.io/docs/api-reference/text-to-voice/create); [Design a voice — API ref](https://elevenlabs.io/docs/api-reference/text-to-voice/design)
- **Ethical/ToS constraints on cloning a real child's voice — be explicit**:
  - Service age gate: **under-13s cannot use the service at all**; **13–18 requires parental/guardian consent**. [elevenlabs.io/use-policy](https://elevenlabs.io/use-policy)
  - Voice replication rule: creating/using ElevenLabs output to "intentionally replicate the voice of another person... without consent or legal right" is prohibited outright — this is a general rule that would cover cloning a child's voice using a parent's account, since the "legal right/consent" bar for a minor is murkier than for a consenting adult.
  - Prohibited-use policy separately and explicitly bars anything sexualizing/exploiting minors and "age-inappropriate material that targets minors" — a strict, unambiguous line.
  - **My explicit recommendation given the above**: do **not** attempt to Instant-Voice-Clone one of your actual daughters/twins' real voices for this project, even with your own parental consent as the account holder — the combination of (a) the platform's own Library ban on child-like voices, (b) the ambiguity of a minor's ability to "consent" to voice cloning under ToS, and (c) the reputational/legal exposure of any child-voice-cloning product, makes this a bright-line "don't" rather than a judgment call. Use an adult VA / Voice Library "youthful" tag / Voice Design synthetic voice instead. [Prateeksha — ethical voice cloning guide](https://prateeksha.com/blog/ethical-voice-cloning-elevenlabs-permissions-scripts-best-practices); [terms.law forum thread on consent policy](https://terms.law/forum/thread/elevenlabs-voice-clone-legal.html)

## 12. Rate limits, concurrency, credit costs (batch-job risk)

- **Credits per character**: Multilingual v2 (and presumably v3, similarly full-featured) ≈ **1 credit per character**; Flash/Turbo models ≈ **0.5–1 credit per character** (roughly half price). As a rough planning rule, **~1,000 credits ≈ 1 minute of spoken audio**. [pricing aggregator summary](https://smallest.ai/blog/elevenlabs-pricing-plans-cost-what-you-get-in-2026)
- **Plan credit allocations** (secondary-source table, not the live pricing page verbatim): Free 10,000 / Starter 30,000 / Creator 121,000 / Pro 600,000 / Scale 1,800,000 / Business 6,000,000 credits/month.
- **Concurrency**: secondary sources report **Creator ≈ 5 concurrent requests, Pro ≈ 10 concurrent requests** for the TTS API, with Enterprise offering "elevated concurrency limits" on request; exceeding the limit surfaces as a `too_many_concurrent_requests` / **HTTP 429** error, for which the documented fix is request queuing or a tier upgrade, not a documented automatic retry-after value. **The primary ElevenLabs help-center pages for this (`help.elevenlabs.io/.../How-many-Text-to-Speech-requests-can-I-make...` and `/API-Error-Code-429`) both returned HTTP 403 on automated fetch, so none of these concurrency numbers are confirmed from the primary source** `[UNVERIFIED — reverify via your account's dashboard/docs before sizing the batch queue]`. [drdroid.io concurrency diagnosis](https://drdroid.io/integration-diagnosis-knowledge/elevenlabs-concurrent-request-limit-exceeded); [Deepgram — ElevenLabs production limits](https://deepgram.com/learn/elevenlabs-production-limits-concurrency-credits-compliance); [ElevenLabs — AI rate limiting for voice](https://elevenlabs.io/blog/ai-rate-limiting-for-voice)
- **What would bite a 60–100-clip batch job**: (1) hitting the concurrency ceiling if you fire requests in an unbounded loop — wrap generation in a semaphore sized to your tier's limit, with exponential backoff on 429; (2) credit exhaustion mid-batch if the SFX per-generation cost is the higher of the two conflicting figures found (200 credits × 100 clips = 20,000 credits, which would burn through a Free or Starter plan's entire monthly allocation on SFX alone) — run one test generation and check the account credit balance delta before committing to a full batch; (3) `eleven_v3`'s lower character-limit-per-call (5,000, `[UNVERIFIED]`) versus Multilingual v2's 10,000 means long chapters may need chunking regardless of which model you pick for expressiveness.

## 13. Python SDK — package, version, call signatures

- **Package**: `elevenlabs` (PyPI). `pip install elevenlabs`. **Could not confirm the exact current pinned version number** from this research pass — the searches surfaced version numbers for *related* packages (`elevenlabs-mcp` 0.11.0/1.0.0, `livekit-plugins-elevenlabs` 1.6.7, `vision-agents-plugins-elevenlabs` 0.5.9) but not a clean current number for the core `elevenlabs` package itself `[UNVERIFIED — run `pip index versions elevenlabs` or check pypi.org/project/elevenlabs directly before pinning]`. [piwheels elevenlabs project page](https://www.piwheels.org/project/elevenlabs/); [PyPI elevenlabs 1.4.1 (an old version, seen in search, not confirmed as latest)](https://pypi.org/project/elevenlabs/1.4.1)

**(a) TTS with timestamps** (single voice):
```python
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key="YOUR_API_KEY")

response = client.text_to_speech.convert_with_timestamps(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    text="[whispers] Once upon a time... [excited] the adventure began!",
    model_id="eleven_v3",                 # or omit -> defaults to eleven_multilingual_v2
    output_format="mp3_44100_128",
)

# response.audio_base64                              -> base64-encoded MP3 bytes
# response.alignment.characters                       -> list[str], one per character
# response.alignment.character_start_times_seconds     -> list[float]
# response.alignment.character_end_times_seconds       -> list[float]
```
(Method signature confirmed from SDK source: `convert_with_timestamps(self, voice_id: str, *, text: str, enable_logging=None, optimize_streaming_latency=None, output_format=None, model_id=OMIT, language_code=OMIT, voice_settings=OMIT, pronunciation_dictionary_locators=OMIT, seed=OMIT, previous_text=OMIT, next_text=OMIT, previous_request_ids=OMIT, next_request_ids=OMIT, use_pvc_as_ivc=OMIT, apply_text_normalization=OMIT, apply_language_text_normalization=OMIT, request_options=None) -> AudioWithTimestampsResponse`. An `async` variant with the identical signature exists on the async client. [GitHub source](https://github.com/elevenlabs/elevenlabs-python/blob/main/src/elevenlabs/text_to_speech/client.py))

**(a-alt) Multi-speaker dialogue with timestamps** (for scenes with more than one character voice in one call):
```python
from elevenlabs import ElevenLabs
from elevenlabs.types import DialogueInput

client = ElevenLabs(api_key="YOUR_API_KEY")

dialogue = [
    DialogueInput(text="[excited] Come on, follow me!", voice_id="VOICE_ID_HERO"),
    DialogueInput(text="[curious] Wait... what's that sound?", voice_id="VOICE_ID_SIDEKICK"),
]

# plain (no timestamps):
audio = client.text_to_dialogue.convert(inputs=dialogue)
with open("scene.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)

# with-timestamps variant is the analogous client.text_to_dialogue.convert_with_timestamps(...)
# — endpoint defaults to model_id="eleven_v3"; exact SDK method name inferred from the
# documented REST endpoint (POST /v1/text-to-dialogue/with-timestamps) and the SDK's
# naming convention (text_to_speech.convert_with_timestamps) but NOT directly confirmed
# by reading the text_to_dialogue client source in this pass. [UNVERIFIED method name]
```

**(b) Sound effects generation:**
```python
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key="YOUR_API_KEY")

# One-shot effect
audio = client.text_to_sound_effects.convert(
    text="a gentle magical whoosh, sparkling, adventure begins",
    duration_seconds=3.0,      # 0.5–30.0, or omit for auto
    prompt_influence=0.3,      # 0.0–1.0, default 0.3
    model_id="eleven_text_to_sound_v2",
    output_format="mp3_44100_128",
)
with open("whoosh.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)

# Loopable ambient bed (max 30s per call; loop it yourself for a longer bed)
loop_audio = client.text_to_sound_effects.convert(
    text="soft rustling forest ambience, birds, gentle breeze, calm",
    duration_seconds=20.0,
    loop=True,                          # only honored on eleven_text_to_sound_v2
    model_id="eleven_text_to_sound_v2",
    prompt_influence=0.3,
    output_format="mp3_44100_128",
)
with open("forest_loop.mp3", "wb") as f:
    for chunk in loop_audio:
        f.write(chunk)
```
(Method signature confirmed from SDK source: `convert(self, *, text: str, output_format=None, loop: Optional[bool]=OMIT, duration_seconds: Optional[float]=OMIT, prompt_influence: Optional[float]=OMIT, model_id: Optional[str]=OMIT, request_options=None) -> Iterator[bytes]`, plus an identical `async def convert(...) -> AsyncIterator[bytes]`. [GitHub source](https://github.com/elevenlabs/elevenlabs-python/blob/main/src/elevenlabs/text_to_sound_effects/client.py); [Mintlify SDK docs mirror](https://www.mintlify.com/elevenlabs/elevenlabs-python/advanced/sound-effects))

---

# RISKS & GOTCHAS

1. **SFX credit cost is unresolved and conflicting.** One source says 40 credits/sec (explicit duration), another says a flat 200 credits/generation. For a 60–100 clip batch these imply very different budgets (e.g., a 5 s effect: 200 credits either way, coincidentally similar at that duration — but a 20 s ambient loop would be 800 credits under the per-second model vs. 200 flat). **Run one real call, check the account credit-usage delta in the dashboard, and extrapolate from that — do not trust either published number blind.**
2. **Concurrency and rate-limit numbers are all secondary-sourced.** Every ElevenLabs help-center page I attempted to fetch directly for rate limits, concurrency, and the 429 error returned HTTP 403 to the automated fetch tool. The "Creator 5 / Pro 10 concurrent" figures came from third-party aggregator sites quoting (not linking a live screenshot of) the help center. **Before wiring a batch job for 60–100 clips, log into the ElevenLabs dashboard/docs directly (authenticated) to confirm your actual plan's concurrency and RPM limits.**
3. **`eleven_v3`'s 5,000-character limit is single-sourced** from one synthesized doc fetch and was not cross-checked against `elevenlabs.io/v3` directly. If your longest chapter's per-line or per-chunk text approaches this, verify the real limit before building chunking logic around it.
4. **Child-voice policy was read via search-engine excerpt, not the live help-center page** (also 403'd). Treat "child-like voices banned from the public Voice Library" as highly likely true (consistent with the Prohibited Use Policy's child-safety language) but not word-for-word confirmed. If this policy is legally load-bearing for the project (e.g., you're deciding whether to attempt any kind of "young voice" generation), have a human re-check the live page in a browser before finalizing an approach.
5. **AAP's primary peer-reviewed guidance was not directly readable** (403). The "60/60 rule" and specific dB framing came from secondary summarization. This doesn't change the overall design direction (keep it quiet, keep it consistent) but shouldn't be cited as a verbatim AAP quote.
6. **The children's-audio-drama SFX-density numbers (BBC/Sesame Workshop/Pinna/Wow in the World/Circle Round) are NOT a documented external standard.** I found no public numeric production guideline from any of these producers. The "~3–5 effects/minute" figure in this document's spec is a synthesized starting point for this project, not an industry citation — label it as such if it's forwarded further (e.g., to a coder building density-check tooling), so nobody mistakes it for a verified benchmark.
7. **The "max +6 dB jump / 30–50 ms attack / 150–300 ms pre-roll" startle-avoidance rules are synthesized**, not drawn from a published pediatric-audio study. They're a reasonable extrapolation from general startle-reflex literature plus standard broadcast loudness-jump practice, but should be treated as a hypothesis to validate by actually listening with the target 2- and 5-year-old audience, not as a clinically validated threshold.
8. **`elevenlabs` PyPI package's current version number is unconfirmed.** Pin and verify (`pip install -U elevenlabs && pip show elevenlabs`) at implementation time rather than assuming any version number from this research.
9. **Two different "with-timestamps" endpoints exist** (`text-to-speech/{voice_id}/with-timestamps` for single-voice, `text-to-dialogue/with-timestamps` for multi-speaker) with **different default models** (`eleven_multilingual_v2` vs. `eleven_v3` respectively) — easy to accidentally call the wrong one and get a different default voice/model behavior than expected. The multi-speaker `text_to_dialogue.convert_with_timestamps(...)` SDK method name is inferred from naming convention and the documented REST endpoint, not directly confirmed by reading that specific client's source file in this pass — verify it exists with that exact name before depending on it in production code.
10. **v3 does not support SSML `<break>` tags** — if any existing project code assumes SSML-style pause control, it will not work with `eleven_v3` and needs to be rewritten using audio-tag/prose-based pacing instead.
