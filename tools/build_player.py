"""
Generate player/index.html from the manifest.

    python tools/build_player.py

The verse used to live twice -- once in script/blocks.py for the audio, once
hand-marked into lines in the player. tools/audit.py exists because those two
could drift a word apart and desync every highlight after it, silently.

Now the manifest is the only source and the player is generated from it, so that
class of bug is not detected -- it is impossible. Splitting the book from 11 long
spreads to 34 short pages became a data change instead of thirty hand-edits.

Inputs
  script/blocks.py         blocks, voices, sfx, ambience
  script/pages.py          page order, scene art, tints
  script/verse_lines.json  the authored line breaks (the meter lives here)
  player/template.html     everything that is not pages, with <!--PAGES-->
"""

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "script"))
import blocks as B      # noqa: E402
import pages as P       # noqa: E402

TEMPLATE = ROOT / "player" / "template.html"
OUT = ROOT / "player" / "index.html"
LINES = ROOT / "script" / "verse_lines.json"

SPEAKER = {"ETTA": "Etta", "KIP": "Kip", "MO": "Mo", "HUSHABALOO": "The Hushabaloo"}
SPEAKER_OVERRIDE = {"p8_kipmo_01": "Kip &amp; Mo"}

SFX_LABEL = {
    "click": "click", "creak": "creeeak", "shloop": "shloop", "shloop_soft": "shloop",
    "pop": "pop", "pop_cascade": "pop, pop, pop&hellip;", "rain": "rain, going home",
    "raspberry_big": "raspberry", "raspberry_small": "raspberry",
    "amb_drips": "drip&hellip; drip&hellip;",
}
WAIT_LABEL = {"p8_wait_01": "Your turn! Blow a raspberry!", "final_wait_01": "Go on&hellip;"}

# A blank line inside a block: where the verse takes a breath.
STANZA_BREAK = {
    "cover_nar_01": [1], "p2_nar_03": [1], "p4_nar_05": [1], "p5_nar_02": [2],
    "p7_nar_02": [4], "p9_nar_07": [4], "final_nar_01": [2],
}


def render_block(bid, kind, ref, spread, lines):
    if kind == "wait":
        secs = ref
        label = WAIT_LABEL.get(bid, "Your turn!")
        return (f'  <div class="wait-block" data-audio="{bid}" '
                f'data-wait="{secs}">{label}</div>')

    if kind == "sfx":
        label = SFX_LABEL.get(ref, ref.replace("_", " "))
        return (f'  <div class="sfx-block" data-audio="{bid}" data-sfx="{ref}">'
                f'<span class="ring"></span><span>{label}</span></div>')

    attrs = f'data-audio="{bid}"'
    if ref in SPEAKER:
        who = SPEAKER_OVERRIDE.get(bid, SPEAKER[ref])
        attrs += f' data-voice="{ref.lower()}" data-speaker="{who}"'
    breaks = set(STANZA_BREAK.get(bid, []))
    out = [f'  <div class="audio-block" {attrs}>']
    for n, line in enumerate(lines):
        cls = "ln stanza-gap" if n in breaks else "ln"
        out.append(f'    <span class="{cls}">{html.escape(line, quote=False)}</span>')
    out.append("  </div>")
    return "\n".join(out)


def main():
    verse = json.loads(LINES.read_text(encoding="utf-8"))
    by_id = {b[0]: b for b in B.BLOCKS}

    # -- the contract: pages must cover every block exactly once, in order --
    laid_out = [bid for _p, _s, ids, _sp, _t in P.PAGES for bid in ids]
    manifest = [b[0] for b in B.BLOCKS]
    if laid_out != manifest:
        missing = [b for b in manifest if b not in laid_out]
        extra = [b for b in laid_out if b not in manifest]
        dupes = [b for b in laid_out if laid_out.count(b) > 1]
        for b in missing:
            print(f"  MISSING from pages.py: {b}")
        for b in extra:
            print(f"  UNKNOWN block in pages.py: {b}")
        for b in sorted(set(dupes)):
            print(f"  DUPLICATED in pages.py: {b}")
        if not (missing or extra or dupes):
            n = next(i for i, (a, c) in enumerate(zip(manifest, laid_out)) if a != c)
            print(f"  ORDER differs at {n}: manifest {manifest[n]}, pages {laid_out[n]}")
        sys.exit("\n  pages.py does not lay out the book correctly.")

    unknown = [s for _p, s, _i, _sp, _t in P.PAGES if s not in P.SCENES]
    if unknown:
        sys.exit(f"  unknown scenes: {sorted(set(unknown))}")

    chunks = []
    for n, (pid, scene, ids, spread, tint) in enumerate(P.PAGES):
        viewbox, art = P.SCENES[scene]
        small = ' small' if scene == "jar_held" else ''
        active = " active" if n == 0 else ""
        chunks.append(
            f'<!-- {"═" * 18} {pid} · {scene} {"═" * 18} -->\n'
            f'<div class="page{active}" data-page="{n}" data-spread="{spread}" '
            f'data-pageid="{pid}" style="--tint:{tint}">\n'
            f'  <div class="art-pane">\n'
            f'    <svg class="art{small}" viewBox="{viewbox}" role="img" '
            f'aria-label="Illustration for {pid}">{art}\n    </svg>\n'
            f'  </div>\n'
            f'  <div class="text-pane">\n'
            + "\n".join(render_block(b, by_id[b][1], by_id[b][2], spread,
                                     verse.get(b, [])) for b in ids)
            + "\n  </div>\n</div>")

    out = TEMPLATE.read_text(encoding="utf-8").replace("<!--PAGES-->", "\n\n".join(chunks))
    OUT.write_text(out, encoding="utf-8")

    spreads = len({p[3] for p in P.PAGES})
    longest = max(len(ids) for _p, _s, ids, _sp, _t in P.PAGES)
    print(f"\n  built {len(P.PAGES)} pages across {spreads} spreads")
    print(f"  {len(manifest)} blocks laid out, longest page holds {longest}")
    print(f"  {len({s for _p, s, _i, _sp, _t in P.PAGES})} distinct scenes")
    print(f"  -> {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)\n")


if __name__ == "__main__":
    main()
