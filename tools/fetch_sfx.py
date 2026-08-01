"""
Fetch open-source (CC0) sound effects and master them for the book.

    python tools/fetch_sfx.py            # fetch what's missing
    python tools/fetch_sfx.py --force    # re-fetch everything
    python tools/fetch_sfx.py --list rain   # show candidates in a collection

Source: The Designer's Choice UCS Collection on archive.org -- a genuine CC0
public-domain Foley library, ~80 categorised sets. Wikimedia Commons was tried
first and has essentially no everyday-object Foley; Freesound has the best library
but needs an API token, so this needs no credentials at all.

Every fetched file is put through the same mastering chain, which is where the
startle spec from research/03-audio-sfx-and-elevenlabs.md finally gets enforced
rather than merely written down:

  * silence trimmed off both ends, so a "1 second" effect is one second of sound
  * a >=30 ms fade-in -- no instant transient, which is what actually startles
  * a fade-out, so nothing ends on a cliff
  * loudnorm to the per-effect target in blocks.py, so no effect can jump more
    than +6 dB over the narration
  * 44.1 kHz mono-safe MP3, matching the narration
"""

import argparse
import json
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "script"))
import blocks as B  # noqa: E402

SFX_DIR = ROOT / "audio" / "sfx"
CREDITS = SFX_DIR / "CREDITS.md"
PROVENANCE = ROOT / "audio" / "sfx_provenance.json"
META = "https://archive.org/metadata/"
UA = "the-hushabaloo/1.0 (children's book project)"

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG = "ffmpeg"

# ── What to fetch ─────────────────────────────────────────────────────────────
# `want` words must all appear in the path; `avoid` disqualifies. `prefer` pushes
# a match up the ranking. Sizes are used as a tiebreak -- for spot effects the
# shortest clip is nearly always the cleanest one.
LIBRARY = {
    "click": dict(
        collection="Doors", want=["door"], prefer=["latch", "close", "cabinet", "wood"],
        avoid=["car", "fridge", "metal", "garage", "squeak", "creak"], lufs=-20, seconds=1.4),
    "raspberry_big": dict(
        collection="Farts", want=["fart"], prefer=["short", "buzz"],
        avoid=[], lufs=-17, seconds=2.2),
    "raspberry_small": dict(
        collection="Farts", want=["fart"], prefer=["short"],
        avoid=["big"], lufs=-22, seconds=1.4),
    "pop": dict(
        collection="Ceramics", want=[], prefer=["clink", "tap", "light", "set"],
        avoid=["break", "smash", "shatter", "destroy"], lufs=-19, seconds=2.2),
    "creak": dict(
        collection="Doors", want=["door"], prefer=["creak", "squeak", "wood"],
        avoid=["car", "metal", "close", "slam"], lufs=-21, seconds=2.5),
    "rain": dict(
        collection="Rain", want=[], prefer=["light", "window", "gentle", "medium"],
        avoid=["thunder", "storm", "heavy"], lufs=-24, seconds=6.0),
    "room_tone": dict(
        collection="Ambiences", want=[], prefer=["room", "interior", "quiet", "house"],
        avoid=["city", "traffic", "crowd", "street"], lufs=-30, seconds=8.0),
    # -- ambient beds: long, quiet, looped under the narration --
    "amb_house": dict(
        collection="Ambiences", want=[], prefer=["room", "tone", "fan"],
        avoid=["city", "crowd", "street", "carnival", "parade", "grocery", "restaurant"],
        lufs=-30, seconds=24.0),
    "amb_attic": dict(
        collection="Ambiences", want=[], prefer=["attic", "weird", "misc"],
        avoid=["suburban", "rain", "crowd", "city"], lufs=-29, seconds=24.0),
    "amb_night": dict(
        collection="Ambiences", want=[], prefer=["nighttime", "quiet", "air"],
        avoid=["crickets", "cicada", "city", "crowd"], lufs=-31, seconds=24.0),
    "amb_drips": dict(
        collection="Ambiences", want=[], prefer=["after rain", "drips", "suburban"],
        avoid=["crowd", "city", "weedwhacker"], lufs=-30, seconds=24.0),
    "bell": dict(
        collection="Bells", want=[], prefer=["small", "light", "ding", "hand"],
        avoid=["church", "alarm", "large"], lufs=-22, seconds=2.5),
}


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def collection_files(name):
    d = get_json(f"{META}Designers-Choice-Collection-{name}")
    base = f"https://{d['server']}{d['dir']}/"
    files = [f for f in d.get("files", []) if f["name"].lower().endswith(".mp3")]
    return base, files


def pick(files, spec):
    """Rank candidates: all `want` present, no `avoid`, most `prefer` hits, shortest."""
    scored = []
    for f in files:
        low = f["name"].lower()
        if any(w not in low for w in spec["want"]):
            continue
        if any(a in low for a in spec["avoid"]):
            continue
        score = sum(1 for p in spec["prefer"] if p in low)
        scored.append((-score, int(f.get("size", 1 << 30)), f["name"]))
    if not scored:
        return None
    scored.sort()
    return scored[0][2]


def master(raw, out, lufs, seconds):
    """Trim, fade in past the startle threshold, fade out, normalise, encode."""
    fade = 0.05                       # 50 ms -- comfortably above the 30 ms floor
    filters = (
        "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02,"
        "areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02,areverse,"
        f"atrim=0:{seconds},"
        f"afade=t=in:st=0:d={fade},"
        f"afade=t=out:st={max(seconds - 0.25, 0.15)}:d=0.25,"
        f"loudnorm=I={lufs}:TP=-3:LRA=7"
    )
    r = subprocess.run(
        [FFMPEG, "-y", "-i", str(raw), "-af", filters,
         "-ar", "44100", "-b:a", "128k", str(out)],
        capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or "")[-300:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--list", metavar="COLLECTION", help="show candidates and exit")
    args = ap.parse_args()

    if args.list:
        base, files = collection_files(args.list)
        print(f"\n  {len(files)} mp3s in {args.list}\n")
        for f in files[:60]:
            print("   ", f["name"][:96])
        return 0

    SFX_DIR.mkdir(parents=True, exist_ok=True)
    tmp = ROOT / "audio" / "_raw"
    tmp.mkdir(exist_ok=True)
    prov = {} if args.force else (
        json.loads(PROVENANCE.read_text()) if PROVENANCE.exists() else {})

    print("\n  Fetching CC0 sound effects -- The Designer's Choice UCS Collection\n")
    credits, made, skipped, failed = [], 0, 0, 0
    cache = {}

    for name, spec in LIBRARY.items():
        out = SFX_DIR / f"{name}.mp3"
        if out.exists() and prov.get(name) and not args.force:
            print(f"  skip  {name}")
            credits.append((name, prov[name]["source"], spec["collection"]))
            skipped += 1
            continue

        coll = spec["collection"]
        try:
            if coll not in cache:
                cache[coll] = collection_files(coll)
            base, files = cache[coll]
        except Exception as e:
            print(f"  FAIL  {name}: could not read {coll} ({e})")
            failed += 1
            continue

        chosen = pick(files, spec)
        if not chosen:
            print(f"  FAIL  {name}: nothing in {coll} matched {spec['want']}/{spec['prefer']}")
            failed += 1
            continue

        short = chosen.split("/")[-1][:56]
        print(f"  get   {name:<16} {coll}/{short} ...", end="", flush=True)
        raw = tmp / f"{name}.src.mp3"
        try:
            url = base + urllib.parse.quote(chosen)
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                raw.write_bytes(r.read())
        except Exception as e:
            print(f"  download failed ({e})")
            failed += 1
            continue

        ok, err = master(raw, out, spec["lufs"], spec["seconds"])
        if not ok:
            print(f"  master failed\n        {err}")
            failed += 1
            continue

        prov[name] = {"source": chosen, "collection": coll,
                      "lufs": spec["lufs"], "seconds": spec["seconds"]}
        credits.append((name, chosen, coll))
        print(f"  ok ({out.stat().st_size // 1024} KB)")
        made += 1

    PROVENANCE.write_text(json.dumps(prov, indent=2))

    CREDITS.write_text(
        "# Sound effect credits\n\n"
        "Effects marked below come from **The Designer's Choice UCS Collection**, "
        "released into the public domain under "
        "[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) and mirrored on "
        "[archive.org](https://archive.org/details/Designers-Choice-Collection-Doors).\n\n"
        "CC0 imposes no attribution requirement. They are credited anyway.\n\n"
        "Every file was trimmed, fade-shaped and loudness-normalised by "
        "`tools/fetch_sfx.py` before use.\n\n"
        "| Effect | Collection | Source file |\n| --- | --- | --- |\n"
        + "".join(f"| `{n}` | {c} | `{s.split('/')[-1]}` |\n" for n, s, c in sorted(credits))
        + "\nRemaining effects are generated with ElevenLabs from the prompts in "
          "`script/blocks.py`.\n",
        encoding="utf-8")

    for f in tmp.glob("*"):
        f.unlink()
    tmp.rmdir()

    print(f"\n  fetched {made}, skipped {skipped}, failed {failed}")
    print(f"  credits -> {CREDITS.relative_to(ROOT)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
