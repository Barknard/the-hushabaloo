"""
One-shot: swap the placeholder circles in every spread for <use> of the real
characters defined in the character sheet.

Each replacement is an exact-string swap and asserts it matched, so a silent
partial edit is impossible.

    python tools/_place_characters.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAYER = ROOT / "player" / "index.html"

# (label, old, new)
SWAPS = [
    # ── SPREAD 1 — the three of them at home ──
    ("p1 trio",
     '''<g><circle cx="352" cy="236" r="21" fill="var(--etta)"/><circle cx="394" cy="248" r="15" fill="var(--kip)"/><circle cx="428" cy="250" r="15" fill="var(--mo)"/>
      <text x="341" y="284" font-family="system-ui" font-size="13" font-weight="800" fill="var(--etta)">Etta</text>
      <text x="384" y="284" font-family="system-ui" font-size="12" font-weight="800" fill="var(--kip)">Kip</text>
      <text x="418" y="284" font-family="system-ui" font-size="12" font-weight="800" fill="var(--mo)">Mo</text></g>''',
     '''<g>
      <use href="#ch-etta" x="326" y="182" width="53" height="80"/>
      <use href="#ch-kip"  x="384" y="204" width="47" height="60"/>
      <use href="#ch-mo"   x="430" y="204" width="47" height="60"/>
      <text x="334" y="280" font-family="system-ui" font-size="14" font-weight="800" fill="var(--etta)">Etta</text>
      <text x="394" y="280" font-family="system-ui" font-size="13" font-weight="800" fill="var(--kip)">Kip</text>
      <text x="442" y="280" font-family="system-ui" font-size="13" font-weight="800" fill="var(--mo)">Mo</text></g>'''),

    # ── SPREAD 2 — Mo's ear against the third door ──
    ("p2 trio",
     '''<g><circle cx="378" cy="236" r="17" fill="var(--mo)"/><circle cx="362" cy="231" r="5" fill="#fff"/></g>
    <circle cx="422" cy="244" r="22" fill="var(--etta)"/>
    <circle cx="462" cy="254" r="15" fill="var(--kip)"/>''',
     '''<use href="#ch-mo"   x="330" y="212" width="47" height="60"/>
    <use href="#ch-etta" x="386" y="192" width="53" height="80"/>
    <use href="#ch-kip"  x="444" y="212" width="47" height="60"/>'''),

    # ── SPREAD 3 — the vast room; the creature, and three very small people ──
    ("p3 hushabaloo",
     '''<g>
      <ellipse cx="450" cy="278" rx="98" ry="76" fill="var(--hush)"/>
      <circle cx="418" cy="256" r="16" fill="#fffaf0"/><circle cx="423" cy="259" r="7" fill="var(--ink)"/>
      <circle cx="476" cy="256" r="16" fill="#fffaf0"/><circle cx="481" cy="259" r="7" fill="var(--ink)"/>
      <path d="M424 306 q26 16 52 0" stroke="#fffaf0" stroke-width="5" fill="none" stroke-linecap="round" opacity=".85"/>
      <path d="M370 250 q-14 -22 4 -34 M530 250 q14 -22 -4 -34" stroke="var(--hush)" stroke-width="9" fill="none" stroke-linecap="round"/></g>''',
     '''<use href="#ch-hush" x="352" y="196" width="200" height="170"/>'''),
    ("p3 trio",
     '''<g><circle cx="66" cy="344" r="19" fill="var(--etta)"/><circle cx="104" cy="352" r="13" fill="var(--kip)"/><circle cx="136" cy="352" r="13" fill="var(--mo)"/></g>''',
     '''<g>
      <use href="#ch-etta" x="40" y="308" width="40" height="61"/>
      <use href="#ch-kip"  x="84" y="325" width="34" height="44"/>
      <use href="#ch-mo"   x="122" y="325" width="34" height="44"/></g>'''),

    # ── SPREAD 4 — the sleeve reaches for the door's click ──
    ("p4 hushabaloo",
     '''<ellipse cx="146" cy="180" rx="112" ry="94" fill="var(--hush)"/>
    <circle cx="110" cy="154" r="17" fill="#fffaf0"/><circle cx="115" cy="157" r="8" fill="var(--ink)"/>
    <circle cx="176" cy="154" r="17" fill="#fffaf0"/><circle cx="181" cy="157" r="8" fill="var(--ink)"/>
    <path d="M118 214 q28 18 56 0" stroke="#fffaf0" stroke-width="5" fill="none" stroke-linecap="round" opacity=".85"/>''',
     '''<use href="#ch-hush" x="34" y="86" width="224" height="190"/>'''),
    ("p4 trio",
     '''<g><circle cx="60" cy="288" r="16" fill="var(--etta)"/><circle cx="94" cy="294" r="11" fill="var(--kip)"/><circle cx="122" cy="294" r="11" fill="var(--mo)"/></g>''',
     '''<g>
      <use href="#ch-etta" x="268" y="248" width="36" height="55"/>
      <use href="#ch-kip"  x="308" y="264" width="30" height="38"/>
      <use href="#ch-mo"   x="342" y="264" width="30" height="38"/></g>'''),

    # ── SPREAD 5 — Etta stands up to him ──
    ("p5 hushabaloo",
     '''<ellipse cx="446" cy="168" rx="108" ry="90" fill="var(--hush)" opacity=".96"/>
    <circle cx="412" cy="144" r="16" fill="#fffaf0"/><circle cx="416" cy="147" r="7" fill="var(--ink)"/>
    <circle cx="476" cy="144" r="16" fill="#fffaf0"/><circle cx="480" cy="147" r="7" fill="var(--ink)"/>
    <path d="M416 204 q30 12 60 0" stroke="#fffaf0" stroke-width="5" fill="none" stroke-linecap="round" opacity=".6"/>''',
     '''<use href="#ch-hush" x="338" y="76" width="216" height="184"/>'''),
    ("p5 etta",
     '''<circle cx="112" cy="176" r="38" fill="var(--etta)"/>
    <rect x="92" y="214" width="40" height="56" rx="12" fill="var(--etta)"/>''',
     '''<use href="#ch-etta" x="66" y="110" width="72" height="109"/>'''),

    # ── SPREAD 6 — Kip, three shelves up ──
    ("p6 kip",
     '''<circle cx="190" cy="138" r="17" fill="var(--kip)"/>
    <rect x="178" y="156" width="24" height="34" rx="9" fill="var(--kip)"/>
    <path d="M176 158 q-20 -16 -24 -38 M204 158 q20 -12 34 -30" stroke="var(--kip)" stroke-width="8" fill="none" stroke-linecap="round"/>''',
     '''<use href="#ch-kip" x="160" y="106" width="54" height="69"/>'''),
    ("p6 pair",
     '''<g><circle cx="80" cy="300" r="20" fill="var(--etta)"/><circle cx="122" cy="308" r="14" fill="var(--mo)"/></g>''',
     '''<g>
      <use href="#ch-etta" x="54" y="258" width="46" height="70"/>
      <use href="#ch-mo"   x="108" y="282" width="36" height="46"/></g>'''),

    # ── SPREAD 7 — the quiet part ──
    ("p7 trio",
     '''<g><circle cx="268" cy="238" r="24" fill="var(--etta)" opacity=".95"/>
      <circle cx="312" cy="250" r="17" fill="var(--kip)" opacity=".95"/>
      <circle cx="346" cy="250" r="17" fill="var(--mo)" opacity=".95"/></g>''',
     '''<g opacity=".96">
      <use href="#ch-etta" x="238" y="196" width="46" height="70"/>
      <use href="#ch-kip"  x="290" y="216" width="40" height="51"/>
      <use href="#ch-mo"   x="334" y="216" width="40" height="51"/></g>'''),

    # ── SPREAD 8 — the rudest thing they know ──
    ("p8 trio",
     '''<g><circle cx="176" cy="224" r="28" fill="var(--etta)"/>
      <circle cx="248" cy="240" r="22" fill="var(--kip)"/><circle cx="300" cy="240" r="22" fill="var(--mo)"/>
      <path d="M266 262 q5 14 17 5 M318 262 q5 14 17 5" stroke="#fffaf0" stroke-width="5" fill="none" stroke-linecap="round"/></g>''',
     '''<g>
      <use href="#ch-etta" x="136" y="180" width="56" height="85"/>
      <use href="#ch-kip"  x="204" y="204" width="48" height="61"/>
      <use href="#ch-mo"   x="258" y="204" width="48" height="61"/></g>'''),

    # ── SPREAD 9 — the gift, and the way home ──
    ("p9 hushabaloo",
     '''<ellipse cx="150" cy="186" rx="92" ry="78" fill="var(--hush)" opacity=".95"/>
    <circle cx="120" cy="166" r="15" fill="#fffaf0"/><circle cx="124" cy="168" r="7" fill="var(--ink)"/>
    <circle cx="180" cy="166" r="15" fill="#fffaf0"/><circle cx="184" cy="168" r="7" fill="var(--ink)"/>
    <path d="M120 212 q30 24 60 0" stroke="#fffaf0" stroke-width="6" fill="none" stroke-linecap="round"/>''',
     '''<use href="#ch-hush-sad" x="58" y="106" width="184" height="156"/>'''),
    ("p9 etta",
     '''<circle cx="296" cy="212" r="23" fill="var(--etta)"/>''',
     '''<use href="#ch-etta" x="266" y="168" width="46" height="70"/>'''),
    ("p9 pair",
     '''<g><circle cx="376" cy="248" r="15" fill="var(--kip)"/><circle cx="406" cy="254" r="15" fill="var(--mo)"/></g>''',
     '''<g>
      <use href="#ch-kip" x="352" y="212" width="40" height="51"/>
      <use href="#ch-mo"  x="398" y="212" width="40" height="51"/></g>'''),
]


def main():
    src = PLAYER.read_text(encoding="utf-8")
    missed = []
    for label, old, new in SWAPS:
        if old not in src:
            missed.append(label)
            continue
        src = src.replace(old, new, 1)
    if missed:
        sys.exit("did not match: " + ", ".join(missed))
    PLAYER.write_text(src, encoding="utf-8")
    print(f"placed characters in {len(SWAPS)} positions")


if __name__ == "__main__":
    main()
