"""
Lift the children's voices into a child register, without breaking the karaoke.

    python tools/master_voices.py            # pitch anything freshly generated
    python tools/master_voices.py --force    # re-pitch everything

Run this after tools/generate.py. It is idempotent: each pitched file's hash is
recorded, so re-running never double-pitches. A file whose hash no longer matches
the record has been regenerated and gets pitched again.

WHY POST-PROCESS AND NOT A CHILD VOICE
ElevenLabs' Voice Library prohibits child and child-like voices, and Voice Design
rejected the descriptions outright. So the children are adult character voices
lifted into a child register -- which is exactly how animation has always cast
children, and it sounds far better than synthesised real-toddler timbre.

WHY DURATION IS PRESERVED EXACTLY
Word timings are absolute offsets into the file. Any filter that changed duration
would desync every highlight. `asetrate` shifts pitch and speed together by r;
`atempo=1/r` puts the speed back. The two are exact inverses, so pitch moves and
duration does not. This script asserts that afterwards rather than trusting it --
a drift over 60 ms fails the file.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "script"))
import blocks as B  # noqa: E402

LINES = ROOT / "audio" / "lines"
STATE = ROOT / "audio" / "pitch_state.json"
TOL = 0.06  # seconds of duration drift tolerated

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
    FFPROBE = None
except ImportError:
    FFMPEG = "ffmpeg"
    FFPROBE = "ffprobe"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def duration(path):
    """Read duration via ffmpeg itself -- ffprobe is not always bundled."""
    r = subprocess.run([FFMPEG, "-i", str(path), "-f", "null", "-"],
                       capture_output=True, text=True)
    for line in reversed((r.stderr or "").splitlines()):
        if "time=" in line:
            stamp = line.split("time=")[1].split()[0]
            try:
                h, m, s = stamp.split(":")
                return int(h) * 3600 + int(m) * 60 + float(s)
            except ValueError:
                continue
    return None


def shift(path, semitones):
    """Pitch up by `semitones`, holding duration constant."""
    r = 2 ** (semitones / 12.0)
    tmp = path.with_suffix(".pitched.mp3")
    before = duration(path)
    filters = f"asetrate=44100*{r:.6f},aresample=44100,atempo={1 / r:.6f}"
    proc = subprocess.run(
        [FFMPEG, "-y", "-i", str(path), "-af", filters,
         "-ar", "44100", "-b:a", "128k", str(tmp)],
        capture_output=True, text=True)
    if proc.returncode != 0:
        tmp.unlink(missing_ok=True)
        return None, (proc.stderr or "")[-200:]

    after = duration(tmp)
    if before and after and abs(before - after) > TOL:
        tmp.unlink(missing_ok=True)
        return None, f"duration drifted {before:.2f}s -> {after:.2f}s (karaoke would desync)"

    tmp.replace(path)
    return digest(path), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    state = {} if args.force else (json.loads(STATE.read_text()) if STATE.exists() else {})
    targets = [(b[0], b[2]) for b in B.BLOCKS
               if b[1] == "speech" and b[2] in B.PITCH_SEMITONES]

    print(f"\n  Lifting {len(targets)} child-voice blocks into register")
    print("  " + ", ".join(f"{v} +{s}st" for v, s in B.PITCH_SEMITONES.items()) + "\n")

    done = skipped = failed = 0
    for bid, voice in targets:
        path = LINES / f"{bid}.mp3"
        if not path.exists():
            print(f"  MISS  {bid} -- not generated yet")
            failed += 1
            continue
        if state.get(bid) == digest(path) and not args.force:
            skipped += 1
            continue

        st = B.PITCH_SEMITONES[voice]
        print(f"  lift  {bid:<20} {voice:<5} +{st}st ...", end="", flush=True)
        h, err = shift(path, st)
        if h is None:
            print(f"  FAILED\n        {err}")
            failed += 1
        else:
            state[bid] = h
            print("  ok")
            done += 1

    STATE.write_text(json.dumps(state, indent=2))
    print(f"\n  lifted {done}, already done {skipped}, failed {failed}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
