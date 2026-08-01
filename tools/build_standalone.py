"""
Build a single self-contained HTML file: every MP3 and all word timings inlined.

    python tools/build_standalone.py       ->  dist/the-hushabaloo.html

The result needs no server and no network. Drop it on a tablet, open it on a plane,
email it to a grandparent -- it plays.

It injects one global, `window.__HUSHABALOO_INLINE__`, ahead of the player's own
script. The player reads that seam if present and falls back to fetching files if not.

DATATRAX's builder instead string-matched fragments of its own player source and
rewrote them. That works exactly until someone edits the player, at which point the
replacements silently no-op and the "standalone" file quietly goes back to requesting
audio that isn't there. This build fails loudly instead: if the seam is gone, it stops.
"""

import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAYER = ROOT / "player" / "index.html"
AUDIO = ROOT / "audio"
OUT = ROOT / "dist" / "the-hushabaloo.html"

SEAM = "window.__HUSHABALOO_INLINE__"
ANCHOR = "<script>"


def main():
    html = PLAYER.read_text(encoding="utf-8")

    if SEAM not in html:
        sys.exit(f"  Player has no {SEAM} seam -- refusing to build a file that would\n"
                 f"  silently fall back to fetching audio. Restore the seam first.")

    timestamps_path = AUDIO / "timestamps.json"
    if not timestamps_path.exists():
        sys.exit("  audio/timestamps.json not found -- run tools/generate.py first.")
    timestamps = json.loads(timestamps_path.read_text())

    audio, total = {}, 0
    for folder in ("lines", "sfx"):
        for mp3 in sorted((AUDIO / folder).glob("*.mp3")):
            data = mp3.read_bytes()
            audio[f"{folder}/{mp3.stem}"] = (
                "data:audio/mpeg;base64," + base64.b64encode(data).decode("ascii"))
            total += len(data)

    if not audio:
        sys.exit("  No audio found -- run tools/generate.py first.")

    payload = json.dumps({"timestamps": timestamps, "audio": audio}, separators=(",", ":"))
    inject = f"<script>{SEAM} = {payload};</script>\n{ANCHOR}"

    # Inject before the player's own <script>, so the global exists when it runs.
    at = html.rindex(ANCHOR)
    built = html[:at] + inject + html[at + len(ANCHOR):]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(built, encoding="utf-8")

    print(f"\n  inlined {len(audio)} audio files ({total / 1024 / 1024:.1f} MB raw)")
    print(f"  timings for {len(timestamps)} blocks")
    print(f"  -> {OUT.relative_to(ROOT)}  ({OUT.stat().st_size / 1024 / 1024:.1f} MB)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
