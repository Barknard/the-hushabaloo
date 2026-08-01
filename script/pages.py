"""
THE HUSHABALOO -- page layout.

A picture book turns the page on every beat. Eleven long spreads meant twelve
blocks of verse stacked on one screen and an illustration that had scrolled out
of sight by the time the story reached its low point. This splits the same story
across 34 short pages: one moment each, no scrolling, and a picture that CHANGES
as the story moves rather than sitting still for two minutes.

  PAGES   ordered (page_id, scene, [block_ids], spread, tint)
          Block ids must cover script/blocks.py exactly once, in order --
          tools/build_player.py refuses to build otherwise.

  SCENES  each returns the inner SVG for a page. They are composed from the
          shared <symbol> character sheet plus a handful of scene helpers, so
          a new page costs a few lines rather than a new illustration.

Consecutive pages deliberately share and evolve a scene: the shelves fill, the
creature rises out of them, the room darkens, one jar starts to glow. Because
pages cross-fade, a scene that only changes a little reads as the picture
*moving* rather than as a different picture.
"""

# ── palette-following tints, one per beat ─────────────────────────────────────
WARM, DIM, DEEP, DARK, GOLD, DAWN, CREAM = (
    "#ffe3a0", "#dfe6d8", "#d8d2ee", "#b9bdd4", "#ffd766", "#ffd9b0", "#ffeec4")


# ── scene helpers ─────────────────────────────────────────────────────────────

def kids(*specs):
    """Place characters: kids('etta', 300, 200, 54) -> a <use> per triple."""
    out = []
    for name, x, y, h in specs:
        w = round(h * (0.658 if name == "etta" else 0.78), 1)
        cls = "breathe" if name.startswith("hush") else "bob"
        out.append(f'<use class="{cls}" href="#ch-{name}" x="{x}" y="{y}" '
                   f'width="{w}" height="{h}"/>')
    return "\n    ".join(out)


def jarwall(rows=4, cols=11, dark=False, glow=None, start=(30, 26), gap=(50, 82)):
    """The shelves. `glow` lights one jar -- the empty one that is the answer."""
    labels = ["RAIN", "DOG", "STAIRS", "SNORE", "SHEEP", "KETTLE", "TAP", "BIRD",
              "CLOCK", "HUM", "CREAK", "DRIP", "KNOCK", "WIND", "PURR", "BELL"]
    stroke = "#fffaf0" if dark else "var(--ink)"
    fill = "none" if dark else "#fffaf0"
    op = ".22" if dark else ".8"
    out, n = [], 0
    for r in range(rows):
        y = start[1] + r * gap[1]
        out.append(f'<line x1="18" y1="{y + 44}" x2="582" y2="{y + 44}" '
                   f'stroke="var(--shelf)" stroke-width="8" stroke-linecap="round" '
                   f'opacity="{".3" if dark else "1"}"/>')
        for c in range(cols):
            x = start[0] + c * gap[0]
            lit = glow is not None and n == glow
            n += 1
            if lit:
                out.append(f'<g class="twinkle"><circle cx="{x + 19}" cy="{y + 19}" r="34" '
                           f'fill="var(--glow)" opacity=".16"/></g>')
                out.append(f'<rect x="{x}" y="{y}" width="38" height="38" rx="6" fill="none" '
                           f'stroke="var(--glow)" stroke-width="4"/>')
                out.append(f'<text x="{x + 19}" y="{y + 62}" text-anchor="middle" '
                           f'font-family="system-ui" font-size="11" font-style="italic" '
                           f'fill="var(--glow)">empty</text>')
                continue
            out.append(f'<rect x="{x}" y="{y}" width="38" height="38" rx="6" fill="{fill}" '
                       f'stroke="{stroke}" stroke-width="2.5" opacity="{op}"/>')
            out.append(f'<rect x="{x + 8}" y="{y - 7}" width="22" height="8" rx="3" '
                       f'fill="var(--shelf)" opacity="{op}"/>')
            if not dark:
                out.append(f'<text x="{x + 19}" y="{y + 24}" text-anchor="middle" '
                           f'font-family="system-ui" font-size="7.5" font-weight="700" '
                           f'fill="var(--dim)">{labels[n % len(labels)]}</text>')
    return "\n    ".join(out)


def door(x, y, w, h, lit=True, label=None, ajar=False):
    g = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="var(--shelf)"/>']
    if ajar:
        g.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" '
                 f'fill="var(--glow)" opacity=".24"/>')
    g.append(f'<circle cx="{x + 13}" cy="{y + h / 2:.0f}" r="7" '
             f'fill="{"var(--glow)" if lit else "var(--dim)"}"/>')
    if label:
        g.append(f'<text x="{x - 4}" y="{y + h + 26}" font-family="system-ui" '
                 f'font-size="20" font-weight="800" fill="var(--glow)">{label}</text>')
    return "\n    ".join(g)


def motes(pts, cls="", colour="var(--glow)"):
    c = f' class="{cls}"' if cls else ""
    return (f'<g{c} fill="{colour}">'
            + "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in pts) + "</g>")


def caption(x, y, text, colour="var(--dim)", size=15):
    return (f'<text x="{x}" y="{y}" font-family="system-ui" font-size="{size}" '
            f'font-style="italic" fill="{colour}">{text}</text>')


HOUSE_SHELL = (
    '<rect x="20" y="26" width="560" height="270" rx="14" fill="#fff6e0" '
    'stroke="var(--ink)" stroke-width="4"/>'
    '<line x1="20" y1="164" x2="580" y2="164" stroke="var(--ink)" stroke-width="4"/>'
    '<line x1="300" y1="26" x2="300" y2="164" stroke="var(--ink)" stroke-width="4"/>')

KETTLE = ('<ellipse cx="122" cy="126" rx="38" ry="30" fill="var(--etta)"/>'
          '<path d="M158 112 q20 -7 22 -25" stroke="var(--etta)" stroke-width="8" '
          'fill="none" stroke-linecap="round"/>'
          '<path class="sway" d="M174 74 q7 -16 -2 -25 M188 76 q9 -14 3 -25" '
          'stroke="var(--glow)" stroke-width="5" fill="none" stroke-linecap="round"/>')

STAIRS = ('<g fill="var(--shelf)"><rect x="352" y="136" width="48" height="12" rx="2"/>'
          '<rect x="386" y="112" width="48" height="12" rx="2"/>'
          '<rect x="420" y="88" width="48" height="12" rx="2"/>'
          '<rect x="454" y="64" width="48" height="12" rx="2"/></g>')

TAP = ('<rect x="92" y="198" width="14" height="38" fill="var(--dim)"/>'
       '<rect x="76" y="190" width="52" height="12" rx="5" fill="var(--dim)"/>'
       '<circle cx="99" cy="258" r="8" fill="var(--mo)"/>'
       '<circle cx="99" cy="282" r="5" fill="var(--mo)" opacity=".6"/>')

DOG = ('<g fill="var(--shelf)"><ellipse cx="248" cy="266" rx="52" ry="22"/>'
       '<circle cx="296" cy="254" r="17"/>'
       '<ellipse cx="308" cy="266" rx="9" ry="6" fill="var(--ink)"/></g>')

VIEWBOX = "0 0 600 320"
VB_TALL = "0 0 600 380"


# ── the scenes ────────────────────────────────────────────────────────────────

SCENES = {

"cover": ('0 0 600 400', f'''
    <defs><radialGradient id="cg" cx="50%" cy="50%">
      <stop offset="0%" stop-color="#ffc93c" stop-opacity=".34"/>
      <stop offset="100%" stop-color="#ffc93c" stop-opacity="0"/></radialGradient></defs>
    <rect width="600" height="400" fill="url(#cg)"/>
    <rect x="222" y="46" width="156" height="316" rx="6" fill="#3b2d1e"/>
    <rect x="234" y="62" width="60" height="106" rx="4" fill="#ffc93c" opacity=".2"/>
    <rect x="306" y="62" width="60" height="106" rx="4" fill="#ffc93c" opacity=".2"/>
    <rect x="234" y="186" width="60" height="106" rx="4" fill="#ffc93c" opacity=".2"/>
    <rect x="306" y="186" width="60" height="106" rx="4" fill="#ffc93c" opacity=".2"/>
    <circle cx="248" cy="210" r="9" fill="var(--glow)"/>
    <g fill="var(--glow)"><rect x="216" y="42" width="7" height="324" rx="3"/>
      <rect x="377" y="42" width="7" height="324" rx="3"/>
      <rect x="216" y="38" width="168" height="7" rx="3"/>
      <rect x="216" y="362" width="168" height="11" rx="5"/></g>
    {motes([(120,112,7),(86,196,5),(142,268,9),(482,132,7),(518,228,5),(462,300,9)], "twinkle")}'''),

"house_full": (VIEWBOX, f'''
    {HOUSE_SHELL}{KETTLE}
    <text x="60" y="66" font-family="system-ui" font-size="19" font-weight="800" fill="var(--etta)">sssss!</text>
    {STAIRS}<text x="352" y="52" font-family="system-ui" font-size="20" font-weight="800" fill="var(--glow)">squeak!</text>
    {TAP}<text x="128" y="248" font-family="system-ui" font-size="17" font-weight="700" fill="var(--mo)">drip</text>
    {DOG}<text x="166" y="238" font-family="system-ui" font-size="17" font-weight="700" fill="var(--shelf)">whumpf</text>
    {door(500, 192, 66, 102)}
    {kids(("etta",326,182,80),("kip",384,204,60),("mo",430,204,60))}'''),

"house_door": (VIEWBOX, f'''
    {HOUSE_SHELL}{KETTLE}{STAIRS}{TAP}{DOG}
    {door(500, 192, 66, 102, label="click.")}
    {motes([(492,222,6),(474,214,4)], "twinkle")}
    {kids(("etta",326,182,80),("kip",384,204,60),("mo",430,204,60))}'''),

"house_quiet": (VIEWBOX, f'''
    {HOUSE_SHELL}
    <g opacity=".22">{KETTLE}{STAIRS}{TAP}{DOG}</g>
    {door(500, 192, 66, 102, lit=False)}
    {caption(60, 62, "no song. no squeak. no drip.")}
    {kids(("etta",326,182,80),("kip",384,204,60),("mo",430,204,60))}'''),

"doors_three": (VIEWBOX, f'''
    <rect x="34" y="24" width="104" height="256" rx="6" fill="var(--dim)" opacity=".3"/>
    <rect x="176" y="24" width="104" height="256" rx="6" fill="var(--dim)" opacity=".3"/>
    <rect x="318" y="24" width="128" height="256" rx="6" fill="var(--shelf)"/>
    <circle cx="336" cy="160" r="8" fill="var(--glow)"/>
    <text x="72" y="306" font-family="system-ui" font-size="19" font-weight="700" fill="var(--dim)">one</text>
    <text x="214" y="306" font-family="system-ui" font-size="19" font-weight="700" fill="var(--dim)">two</text>
    <text x="346" y="306" font-family="system-ui" font-size="21" font-weight="900" fill="var(--glow)">three</text>
    {kids(("mo",330,212,60),("etta",386,192,80),("kip",444,212,60))}'''),

"door_drinking": (VIEWBOX, f'''
    <rect x="318" y="24" width="128" height="256" rx="6" fill="var(--shelf)"/>
    <circle cx="336" cy="160" r="8" fill="var(--glow)"/>
    <g stroke="var(--glow)" stroke-width="5" fill="none" stroke-linecap="round" opacity=".95">
      <path d="M540 82 q-48 28 -84 68"/><path d="M566 158 q-54 10 -92 34"/>
      <path d="M528 226 q-38 -8 -70 14"/></g>
    {motes([(546,80,8),(572,156,7),(532,224,7)], "drift")}
    {caption(470, 52, "going, going…")}
    {kids(("mo",330,212,60),("etta",386,192,80),("kip",444,212,60))}'''),

"doorway_open": (VIEWBOX, f'''
    <rect x="196" y="24" width="208" height="272" rx="6" fill="var(--hush)" opacity=".16"/>
    <rect x="196" y="24" width="208" height="272" rx="6" fill="none" stroke="var(--glow)" stroke-width="6"/>
    {motes([(250,90,5),(330,140,4),(290,210,6),(350,250,4)], "twinkle")}
    {caption(206, 320, "a room that was not in the house")}
    {kids(("etta",228,196,84),("kip",290,220,62),("mo",332,220,62))}'''),

"shelves_vast": (VB_TALL, f'''
    {jarwall()}
    {kids(("etta",40,308,61),("kip",84,325,44),("mo",122,325,44))}
    {caption(40, 372, "(very small indeed)")}'''),

"shelves_creature": (VB_TALL, f'''
    {jarwall(rows=3)}
    {kids(("hush",352,196,170))}
    {kids(("etta",40,308,61),("kip",84,325,44),("mo",122,325,44))}'''),

"creature_close": (VIEWBOX, f'''
    {kids(("hush",120,54,210))}
    {motes([(430,90,6),(470,140,5),(500,210,6),(452,262,4)], "twinkle")}
    {caption(410, 300, "I keep them. That's all.", "var(--hush)")}'''),

"creature_taking": (VIEWBOX, f'''
    {kids(("hush",34,86,190))}
    <path d="M256 178 q112 -20 196 26" stroke="var(--hush)" stroke-width="30" fill="none" stroke-linecap="round"/>
    {motes([(438,188,11),(392,174,7),(352,166,5)], "drift")}
    {kids(("etta",268,248,55),("kip",308,264,38),("mo",342,264,38))}'''),

"door_losing_click": (VIEWBOX, f'''
    {kids(("hush",20,96,170))}
    <path d="M212 178 q140 -24 240 22" stroke="var(--hush)" stroke-width="28" fill="none" stroke-linecap="round"/>
    {door(452, 118, 86, 166)}
    {motes([(438,188,11),(392,174,7),(352,166,5)], "drift")}
    {caption(316, 128, "the click")}'''),

"wall_no_door": (VIEWBOX, f'''
    <rect x="380" y="60" width="160" height="230" rx="4" fill="var(--shelf)" opacity=".5"/>
    <rect x="380" y="60" width="160" height="230" rx="4" fill="none" stroke="var(--dim)" stroke-width="4" stroke-dasharray="10 8"/>
    {caption(384, 316, "it's a wall. nothing more.", "var(--dim)", 17)}
    {kids(("etta",190,180,80),("kip",250,204,60),("mo",296,204,60))}'''),

"etta_stands": (VIEWBOX, f'''
    {kids(("hush",338,76,184))}
    {kids(("etta",66,110,109))}
    <rect x="172" y="112" width="140" height="52" rx="15" fill="#fffaf0" stroke="var(--ink)" stroke-width="4"/>
    <path d="M192 164 l-10 22 l26 -22" fill="#fffaf0" stroke="var(--ink)" stroke-width="4"/>
    <text x="192" y="146" font-family="system-ui" font-size="22" font-weight="700" fill="var(--ink)">please.</text>'''),

"creature_explains": (VIEWBOX, f'''
    {kids(("hush",180,40,240))}
    {motes([(120,110,6),(90,180,5),(500,120,6),(530,200,5),(140,250,4),(486,262,4)], "twinkle")}
    {caption(150, 314, "nothing is ever lost here", "var(--hush)", 17)}'''),

"word_taken": (VIEWBOX, f'''
    {kids(("hush",338,76,184))}
    {kids(("etta",66,110,109))}
    <rect x="172" y="112" width="140" height="52" rx="15" fill="#fffaf0" stroke="var(--ink)" stroke-width="4" opacity=".4"/>
    {motes([(336,102,10),(366,84,6),(390,72,4)], "drift")}
    {caption(300, 60, "(the word she needed)")}'''),

"kip_sizes_up": (VB_TALL, f'''
    {jarwall(rows=3)}
    {kids(("kip",120,300,70),("etta",40,290,80),("mo",210,312,56))}
    {caption(280, 348, "…of all of the things about Kip")}'''),

"kip_climbing": (VB_TALL, f'''
    {jarwall(rows=3)}
    {kids(("kip",160,90,74))}
    <text x="120" y="86" font-family="system-ui" font-size="18" font-weight="800" fill="var(--kip)">watch me!</text>
    {kids(("etta",54,300,72),("mo",120,318,50))}'''),

"jar_pops": (VB_TALL, f'''
    {jarwall(rows=2)}
    <path d="M292 176 l16 -24 l18 22" fill="none" stroke="var(--ink)" stroke-width="3.5"/>
    <rect x="288" y="176" width="46" height="38" rx="6" fill="none" stroke="var(--ink)" stroke-width="3.5"/>
    <text x="276" y="248" font-family="system-ui" font-size="22" font-weight="900" fill="var(--glow)">pop!</text>
    <g stroke="var(--mo)" stroke-width="6" stroke-linecap="round" fill="none">
      <path d="M346 172 q66 -24 130 -6"/><path d="M350 194 q70 -14 128 14"/>
      <path d="M342 216 q62 4 122 32"/></g>
    <rect x="486" y="128" width="86" height="110" rx="5" fill="none" stroke="var(--ink)" stroke-width="5"/>
    <line x1="529" y1="128" x2="529" y2="238" stroke="var(--ink)" stroke-width="4"/>
    <text x="482" y="270" font-family="system-ui" font-size="18" font-weight="800" fill="var(--mo)">home</text>
    {kids(("etta",60,300,72),("kip",130,318,50),("mo",180,318,50))}'''),

"shelf_lifted": (VB_TALL, f'''
    {jarwall(rows=1, start=(30, 14))}
    {kids(("hush-sad",340,150,180))}
    {caption(40, 300, "…where a person can't climb")}
    {kids(("etta",40,246,72),("kip",106,266,50),("mo",156,266,50))}'''),

"dark_still": ('0 0 600 300', f'''
    <rect width="600" height="300" rx="14" fill="#231d2e"/>
    {jarwall(rows=2, cols=9, dark=True, start=(40, 30), gap=(60, 80))}
    {kids(("etta",250,196,70),("kip",302,216,51),("mo",346,216,51))}
    {caption(44, 276, "and there wasn't a sound in the world", "#fffaf0")}'''),

"dark_three": ('0 0 600 300', f'''
    <rect width="600" height="300" rx="14" fill="#231d2e"/>
    <circle cx="300" cy="230" r="120" fill="var(--glow)" opacity=".05"/>
    {kids(("etta",250,168,86),("kip",306,196,62),("mo",356,196,62))}
    {caption(210, 292, "I'm scared too.", "#fffaf0", 17)}'''),

"empty_jar": ('0 0 600 300', f'''
    <rect width="600" height="300" rx="14" fill="#231d2e"/>
    {jarwall(rows=1, cols=8, dark=True, glow=4, start=(60, 60), gap=(64, 80))}
    {kids(("mo",250,186,62),("etta",320,166,80),("kip",390,190,58))}'''),

"etta_idea": ('0 0 600 300', f'''
    <rect width="600" height="300" rx="14" fill="#231d2e"/>
    <circle cx="180" cy="150" r="106" fill="var(--glow)" opacity=".12"/>
    {kids(("etta",130,86,140))}
    {kids(("kip",330,140,80),("mo",412,140,80))}
    <text x="300" y="272" font-family="system-ui" font-size="21" font-weight="900" fill="var(--glow)">…the rudest thing you know.</text>'''),

"three_ready": (VIEWBOX, f'''
    <circle cx="300" cy="160" r="130" fill="var(--glow)" opacity=".14"/>
    {kids(("etta",150,80,150),("kip",280,120,110),("mo",380,120,110))}
    <text x="230" y="300" font-family="system-ui" font-size="26" font-weight="900" fill="var(--etta)">THREE. TWO. ONE…</text>'''),

"raspberry": (VIEWBOX, f'''
    <circle cx="300" cy="150" r="140" fill="var(--glow)" opacity=".2"/>
    {kids(("kip",180,84,140),("mo",300,84,140))}
    <g stroke="var(--kip)" stroke-width="8" fill="none" stroke-linecap="round">
      <path d="M258 200 q40 30 86 24"/><path d="M382 200 q42 32 90 26"/></g>
    <text x="330" y="292" font-family="system-ui" font-size="38" font-weight="900" fill="var(--etta)">PBBBBT!</text>'''),

"creature_searching": (VB_TALL, f'''
    {jarwall(rows=3)}
    {kids(("hush-sad",330,200,170))}
    {caption(40, 336, "…and there wasn't one. Not one.", "var(--dim)", 17)}'''),

"burst": (VB_TALL, f'''
    <g id="burst"></g>
    {kids(("etta",120,208,90),("kip",210,236,64),("mo",268,236,64))}
    <text x="352" y="330" font-family="system-ui" font-size="26" font-weight="900" fill="var(--glow)">UP, and OUT, and HOME</text>'''),

"one_small_sound": (VIEWBOX, f'''
    <rect width="600" height="320" rx="14" fill="#231d2e" opacity=".92"/>
    {motes([(120,80,7),(220,50,5),(360,70,6),(480,44,4),(520,120,6),(90,180,5),(430,190,4)], "twinkle")}
    <circle cx="392" cy="176" r="30" fill="var(--glow)" opacity=".22"/>
    <circle cx="392" cy="176" r="9" fill="var(--glow)"/>
    {kids(("mo",300,196,80))}
    {caption(240, 300, "one little sound, smaller than most", "#fffaf0")}'''),

"click_found": (VIEWBOX, f'''
    <rect x="396" y="42" width="140" height="248" rx="6" fill="var(--glow)" opacity=".24"/>
    <rect x="396" y="42" width="140" height="248" rx="6" fill="none" stroke="var(--glow)" stroke-width="6"/>
    <circle cx="414" cy="176" r="9" fill="var(--glow)"/>
    <text x="404" y="316" font-family="system-ui" font-size="22" font-weight="900" fill="var(--glow)">click.</text>
    {kids(("mo",290,204,72),("etta",190,184,84),("kip",250,214,60))}'''),

"creature_small": (VIEWBOX, f'''
    {jarwall(rows=1, start=(30, 10))}
    {kids(("hush-sad",210,150,140))}
    {caption(180, 312, "he had none of them full", "var(--hush)", 17)}
    {kids(("etta",470,190,80))}'''),

"the_gift": (VIEWBOX, f'''
    {kids(("hush-sad",58,106,156))}
    {kids(("etta",266,168,70))}
    <g stroke="var(--etta)" stroke-width="6" fill="none" stroke-linecap="round" opacity=".92">
      <path d="M256 200 q-24 -10 -44 -4"/><path d="M256 214 q-28 4 -48 14"/></g>
    {caption(230, 286, "a gift, not a weapon")}
    {motes([(200,196,7),(174,206,5)], "twinkle", "var(--etta)")}'''),

"home": (VIEWBOX, f'''
    {HOUSE_SHELL}{KETTLE}{STAIRS}{TAP}{DOG}
    {door(500, 192, 66, 102, label="click.")}
    {motes([(492,222,6),(474,214,4),(140,90,5),(430,120,5)], "twinkle")}
    {kids(("etta",326,182,80),("kip",384,204,60),("mo",430,204,60))}'''),

"jar_held": ('0 0 400 230', f'''
    <circle cx="180" cy="118" r="56" fill="var(--glow)" opacity=".16"/>
    <rect x="148" y="80" width="72" height="82" rx="9" fill="none" stroke="var(--glow)" stroke-width="6"/>
    <rect x="160" y="62" width="48" height="16" rx="5" fill="var(--glow)"/>
    <g stroke="var(--etta)" stroke-width="6" fill="none" stroke-linecap="round">
      <path d="M228 104 q38 -14 70 -4"/><path d="M228 120 q42 4 74 20"/></g>
    <text x="200" y="214" text-anchor="middle" font-family="system-ui" font-size="16"
          font-weight="700" letter-spacing="3" fill="var(--dim)">NO JAR. NO LID. JUST HELD.</text>'''),
}


# ── the pages ─────────────────────────────────────────────────────────────────
# (page_id, scene, [block ids], spread, tint)

PAGES = [
 ("cover",  "cover",             ["cover_nar_01"],                                  "cover", "#f6dfa0"),

 ("p1a",    "house_full",        ["p1_nar_01", "p1_sfx_creak"],                     "p1", WARM),
 ("p1b",    "house_full",        ["p1_nar_02"],                                     "p1", WARM),
 ("p1c",    "house_door",        ["p1_nar_03", "p1_sfx_click", "p1_nar_04"],        "p1", WARM),

 ("p2a",    "house_quiet",       ["p2_nar_01", "p2_etta_01"],                       "p2", DIM),
 ("p2b",    "doors_three",       ["p2_nar_02", "p2_mo_01"],                         "p2", DIM),
 ("p2c",    "door_drinking",     ["p2_nar_03", "p2_sfx_shloop", "p2_nar_04"],       "p2", DIM),

 ("p3a",    "doorway_open",      ["p3_nar_01"],                                     "p3", DEEP),
 ("p3b",    "shelves_vast",      ["p3_nar_02", "p3_etta_01"],                       "p3", DEEP),
 ("p3c",    "shelves_creature",  ["p3_nar_03", "p3_hush_01"],                       "p3", DEEP),

 ("p4a",    "creature_close",    ["p4_hush_01"],                                    "p4", DEEP),
 ("p4b",    "creature_taking",   ["p4_nar_01", "p4_sfx_shloop_1", "p4_nar_02",
                                  "p4_sfx_shloop_2", "p4_nar_03", "p4_sfx_shloop_3"], "p4", DEEP),
 ("p4c",    "door_losing_click", ["p4_nar_04", "p4_sfx_shloop_4"],                  "p4", DEEP),
 ("p4d",    "wall_no_door",      ["p4_nar_05"],                                     "p4", DEEP),

 ("p5a",    "etta_stands",       ["p5_nar_01", "p5_etta_01"],                       "p5", DEEP),
 ("p5b",    "creature_explains", ["p5_hush_01"],                                    "p5", DEEP),
 ("p5c",    "word_taken",        ["p5_etta_02", "p5_sfx_shloop", "p5_nar_02"],      "p5", DEEP),

 ("p6a",    "kip_sizes_up",      ["p6_nar_01", "p6_kip_01"],                        "p6", "#c9e8dd"),
 ("p6b",    "kip_climbing",      ["p6_nar_02", "p6_kip_02", "p6_nar_03", "p6_kip_03"], "p6", "#c9e8dd"),
 ("p6c",    "jar_pops",          ["p6_sfx_pop", "p6_sfx_rain", "p6_nar_04",
                                  "p6_etta_01"],                                    "p6", "#c9e8dd"),

 ("p7a",    "shelf_lifted",      ["p7_nar_01", "p7_hush_01"],                       "p7", DARK),
 ("p7b",    "dark_still",        ["p7_nar_02"],                  "p7", DARK),
 ("p7c",    "dark_three",        ["p7_kip_01", "p7_mo_01", "p7_nar_03",
                                  "p7_etta_01"],                                    "p7", DARK),
 ("p7d",    "empty_jar",         ["p7_nar_04", "p7_mo_02", "p7_etta_02",
                                  "p7_nar_05"],                                     "p7", DARK),
 ("p7e",    "etta_idea",         ["p7_etta_03"],                                    "p7", DARK),

 ("p8a",    "three_ready",       ["p8_nar_01", "p8_etta_01", "p8_nar_02"],          "p8", GOLD),
 ("p8b",    "raspberry",         ["p8_wait_01", "p8_kipmo_01", "p8_sfx_raspberry"], "p8", GOLD),
 ("p8c",    "creature_searching",["p8_nar_03", "p8_nar_04"],                        "p8", GOLD),
 ("p8d",    "burst",             ["p8_nar_05", "p8_sfx_cascade", "p8_nar_06"],      "p8", GOLD),

 ("p9a",    "one_small_sound",   ["p9_nar_01", "p9_mo_01"],                         "p9", DAWN),
 ("p9b",    "click_found",       ["p9_nar_02", "p9_sfx_click", "p9_nar_03"],        "p9", DAWN),
 ("p9c",    "creature_small",    ["p9_nar_04", "p9_etta_01"],                       "p9", DAWN),
 ("p9d",    "the_gift",          ["p9_nar_05", "p9_etta_02", "p9_nar_06",
                                  "p9_sfx_raspberry", "p9_nar_07"],                 "p9", DAWN),
 ("p9e",    "home",              ["p9_nar_08", "p9_sfx_click_home", "p9_nar_09"],   "p9", DAWN),

 ("final",  "jar_held",          ["final_nar_01", "final_nar_02", "final_wait_01",
                                  "final_sfx_raspberry"],                           "final", CREAM),
]
