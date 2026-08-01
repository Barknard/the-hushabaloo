"""
Fail the build on anything DATATRAX let pass silently.

    python tools/audit.py            # structure only -- runs without audio
    python tools/audit.py --audio    # also verify generated files and timings

Every check here exists because its absence produced a real defect, or could:

  1  Block coverage      -- an id in blocks.py with no player counterpart (or the
                            reverse) means audio that never plays, or a block that
                            plays with no text to highlight.
  2  Block order         -- the player walks the DOM in order; if it disagrees with
                            the manifest, the story is told out of sequence.
  3  Text parity         -- the highlight maps timing[i] onto word-span[i]. If the
                            player's visible text differs from the generated text by
                            even one word, every subsequent word lights up wrong.
                            This is THE karaoke desync bug and it is silent.
  4  SFX definition      -- a data-sfx with no entry in SFX generates nothing and
                            404s at read time.
  5  Direction leakage   -- [performance direction] must never reach visible text.
  6  Audio presence      -- (--audio) every block has a file on disk.
  7  Timing parity       -- (--audio) timing count equals visible word count.
  8  Spoken direction    -- (--audio) eleven_v3 sometimes READS a [tag] aloud instead
                            of applying it; ElevenLabs documents this. Word timings are
                            absolute, so a spoken tag pushes the first visible word
                            late. Normal onset is under half a second. This caught the
                            Hushabaloo reading his own stage direction for 2.5s.
  9  Tag vocabulary      -- only short canonical tags. A long descriptive direction
                            matches nothing v3 recognises and gets read aloud.
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "script"))
import blocks as B  # noqa: E402

PLAYER = ROOT / "player" / "index.html"
AUDIO = ROOT / "audio"

fails, warns = [], []


def fail(check, msg):
    fails.append(f"[{check}] {msg}")


def warn(check, msg):
    warns.append(f"[{check}] {msg}")


def visible(text):
    """The words a reader sees -- direction and pause markers removed."""
    t = re.sub(r"\[.*?\]", " ", text)
    t = re.sub(r"\.{2,}", " ", t)
    return " ".join(t.split())


def normalise(text):
    """Compare on words alone: punctuation and case never reach the timing map."""
    t = html.unescape(text)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"[^\w\s']", " ", t)
    return " ".join(t.lower().split())


def parse_player():
    """Ordered [(block_id, kind, sfx_name, visible_text)] as the DOM presents them."""
    src = PLAYER.read_text(encoding="utf-8")
    body = src.split('<div class="book"', 1)[-1].split("</script>")[0]
    out = []
    for m in re.finditer(
        r'<div class="(audio-block|sfx-block|wait-block)"([^>]*)>(.*?)</div>',
        body, re.S,
    ):
        cls, attrs, inner = m.group(1), m.group(2), m.group(3)
        bid = re.search(r'data-audio="([^"]+)"', attrs)
        if not bid:
            continue
        sfx = re.search(r'data-sfx="([^"]+)"', attrs)
        kind = {"audio-block": "speech", "sfx-block": "sfx", "wait-block": "wait"}[cls]
        out.append((bid.group(1), kind, sfx.group(1) if sfx else None, inner))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", action="store_true", help="also verify generated audio")
    args = ap.parse_args()

    print("\n  THE HUSHABALOO -- audit\n")

    dom = parse_player()
    dom_ids = [d[0] for d in dom]
    man_ids = [b[0] for b in B.BLOCKS]

    # 1 -- coverage
    missing = [i for i in man_ids if i not in dom_ids]
    extra = [i for i in dom_ids if i not in man_ids]
    for i in missing:
        fail("coverage", f"{i} is in blocks.py but not in the player")
    for i in extra:
        fail("coverage", f"{i} is in the player but not in blocks.py")

    # 2 -- order
    if not missing and not extra and dom_ids != man_ids:
        for n, (a, b) in enumerate(zip(man_ids, dom_ids)):
            if a != b:
                fail("order", f"position {n}: manifest has {a}, player has {b}")
                break

    dom_by_id = {d[0]: d for d in dom}
    checked = 0

    for bid, kind, ref, text, _pause, _spread in B.BLOCKS:
        d = dom_by_id.get(bid)
        if not d:
            continue
        _, dom_kind, dom_sfx, dom_text = d

        if dom_kind != kind:
            fail("kind", f"{bid}: manifest says {kind}, player renders {dom_kind}")

        # 4 -- sfx definition
        if kind == "sfx":
            if ref not in B.SFX:
                fail("sfx", f"{bid} references undefined effect '{ref}'")
            elif dom_sfx != ref:
                fail("sfx", f"{bid}: manifest '{ref}' vs player '{dom_sfx}'")

        # 3 -- text parity (the silent one)
        if kind == "speech":
            want, got = normalise(visible(text)), normalise(dom_text)
            if want != got:
                w, g = want.split(), got.split()
                where = next((n for n, (x, y) in enumerate(zip(w, g)) if x != y),
                             min(len(w), len(g)))
                fail("text", f"{bid}: diverges at word {where + 1} "
                             f"({len(w)} manifest / {len(g)} player)\n"
                             f"           manifest: ...{' '.join(w[where:where + 6])}\n"
                             f"           player:   ...{' '.join(g[where:where + 6])}")
            else:
                checked += 1

            # 5 -- direction leakage
            if "[" in dom_text and "]" in dom_text:
                fail("leak", f"{bid}: performance direction reached visible text")

    # 9 -- tag vocabulary (runs without audio)
    VETTED = {"whispers", "excited", "curious", "sad", "warmly",
              "shouts", "sighs", "laughs", "nervously", "mischievously"}
    for bid, kind, _r, text, _p, _s in B.BLOCKS:
        if kind != "speech":
            continue
        for tag in re.findall(r"\[(.*?)\]", text):
            if tag not in VETTED:
                fail("tag", f"{bid}: [{tag[:44]}] is not a canonical v3 tag -- "
                            "long directions get read aloud")

    # 6/7/8 -- audio
    if args.audio:
        timings = {}
        tpath = AUDIO / "timestamps.json"
        if tpath.exists():
            timings = json.loads(tpath.read_text())
        else:
            fail("audio", "audio/timestamps.json not found -- run tools/generate.py")

        for bid, kind, ref, text, _p, _s in B.BLOCKS:
            if kind == "speech":
                if not (AUDIO / "lines" / f"{bid}.mp3").exists():
                    fail("audio", f"{bid}.mp3 missing")
                    continue
                t = timings.get(bid)
                if t is None:
                    fail("audio", f"{bid} has no word timings")
                elif len(t) != len(visible(text).split()):
                    warn("timing", f"{bid}: {len(t)} timings vs "
                                   f"{len(visible(text).split())} words -- "
                                   "highlight will drift at the tail")
                # 8 -- spoken direction
                if t and t[0]["start"] > 0.9:
                    fail("spoken-tag",
                         f"{bid}: first spoken word starts at {t[0]['start']:.2f}s -- "
                         f"the [direction] was almost certainly read aloud")
            elif kind == "sfx" and not (AUDIO / "sfx" / f"{ref}.mp3").exists():
                fail("audio", f"sfx/{ref}.mp3 missing")

    # -- report --
    print(f"  blocks    {len(man_ids)} manifest / {len(dom_ids)} player")
    print(f"  text      {checked} speech blocks matched word-for-word")
    print(f"  spreads   {len(B.SPREADS)}")
    print(f"  effects   {len(B.SFX)} defined\n")

    for w in warns:
        print(f"  WARN  {w}")
    for f in fails:
        print(f"  FAIL  {f}")

    if fails:
        print(f"\n  {len(fails)} failure(s). Build is not shippable.\n")
        return 1
    print(f"  Audit passed{f' with {len(warns)} warning(s)' if warns else ''}.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
