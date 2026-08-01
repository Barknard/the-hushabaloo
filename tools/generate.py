"""
Generate every audio block for THE HUSHABALOO.

Reads script/blocks.py, produces one MP3 per block plus word-level timings for the
karaoke highlight, and writes audio/timestamps.json for the player.

    python tools/generate.py            # generate what's missing or stale
    python tools/generate.py --force    # regenerate everything
    python tools/generate.py --only p7  # just one spread

Stdlib only. The API key comes from .env and has no hardcoded fallback -- that is a
direct lesson from DATATRAX, whose generator carried a live key as a default argument
and ended up committing it.

DELIBERATE DIFFERENCE FROM DATATRAX: no block merging. DATATRAX merged consecutive
same-voice blocks into one API call for smoother prosody, then cut the audio back apart
at timestamp midpoints with ffmpeg. That split is precisely where karaoke desync comes
from -- a bad cut shifts every subsequent word. Our blocks are already complete verse
units with natural pauses, so each gets its own call. Slightly more requests, no cutting,
no drift.
"""

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "script"))
import blocks as B  # noqa: E402

API = "https://api.elevenlabs.io/v1"
MODEL = "eleven_v3"
MODEL_FALLBACK = "eleven_multilingual_v2"
FORMAT = "mp3_44100_128"

AUDIO = ROOT / "audio"
LINES = AUDIO / "lines"
SFX_DIR = AUDIO / "sfx"
PROVENANCE = AUDIO / "provenance.json"
TIMESTAMPS = AUDIO / "timestamps.json"

THROTTLE = 0.5  # seconds between calls


# ── env ───────────────────────────────────────────────────────────────────────

def load_env():
    path = ROOT / ".env"
    if not path.exists():
        sys.exit(f"  No .env at {path}. Copy .env.example and fill it in.")
    env = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    if not env.get("ELEVENLABS_API_KEY"):
        sys.exit("  ELEVENLABS_API_KEY is empty in .env.")
    return env


def resolve_cast(env):
    """Map voice name -> voice id, failing loudly on anything unset."""
    cast, missing = {}, []
    for name, var in B.VOICES.items():
        vid = env.get(var, "").strip()
        (cast.setdefault(name, vid) if vid else missing.append(f"{name} ({var})"))
    if missing:
        sys.exit("  Cast incomplete -- set these in .env:\n    " + "\n    ".join(missing))
    return cast


# ── http ──────────────────────────────────────────────────────────────────────

def post(path, api_key, payload, want_json=True):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{API}{path}", data=body, method="POST",
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return (json.load(r) if want_json else r.read()), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read()[:300].decode('utf-8', 'replace')}"
    except Exception as e:
        return None, str(e)


# ── timestamps ────────────────────────────────────────────────────────────────

def chars_to_words(chars, starts, ends):
    """Aggregate ElevenLabs character timings into word timings."""
    words, current, start, prev_end = [], "", None, 0.0
    for ch, st, et in zip(chars, starts, ends):
        if ch.isspace():
            if current:
                words.append({"word": current, "start": round(start, 3),
                              "end": round(prev_end, 3)})
                current, start = "", None
        else:
            if start is None:
                start = st
            current += ch
            prev_end = et
    if current:
        words.append({"word": current, "start": round(start, 3),
                      "end": round(prev_end, 3)})
    return words


def strip_direction(words):
    """
    Drop [performance direction] and standalone '...' from the word list.

    The player highlights visible text only, so the timing list must contain exactly
    the words a reader can see. DATATRAX solved this the same way; getting it wrong
    shifts every highlight after the first bracket.
    """
    out, inside = [], False
    for w in words:
        t = w["word"]
        if re.fullmatch(r"\.{2,}", t):
            continue
        if t.startswith("["):
            inside = "]" not in t
            continue
        if inside:
            inside = "]" not in t
            continue
        out.append(w)
    return out


def visible_text(text):
    """The words a reader sees: direction and pause markers removed."""
    t = re.sub(r"\[.*?\]", " ", text)
    t = re.sub(r"\.{2,}", " ", t)
    return " ".join(t.split())


# ── provenance ────────────────────────────────────────────────────────────────
# Every generated file records a fingerprint of what produced it. When the text or
# voice changes, the fingerprint changes and the block regenerates itself -- no manual
# "delete the audio folder" step, which is the kind of stale-state trap that produces
# a confidently wrong build.

def fingerprint(kind, ref, text, cast):
    settings = B.VOICE_SETTINGS.get(ref, B.VOICE_SETTINGS["_default"])
    basis = f"{kind}|{ref}|{text}|{cast.get(ref, '')}|{MODEL}|{sorted(settings.items())}"
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


def sfx_fingerprint(name):
    spec = B.SFX[name]
    basis = f"sfx|{name}|{spec.get('prompt', '')}|{spec['seconds']}"
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


# ── generation ────────────────────────────────────────────────────────────────

def gen_speech(api_key, voice_id, text, voice_name="NARRATOR"):
    # eleven_v3 reads `stability` as a performance dial: 0.0 Creative, 0.5 Natural,
    # 1.0 Robust. Lower values follow inline [direction] far more willingly. The
    # narrator carries most of the book, so it runs Creative -- the swings between
    # a hushed line and a headlong one are the point. Characters sit at Natural so
    # they stay recognisably themselves across a whole story.
    settings = B.VOICE_SETTINGS.get(voice_name, B.VOICE_SETTINGS["_default"])
    payload = {"text": text, "model_id": MODEL, "voice_settings": dict(settings)}
    data, err = post(f"/text-to-speech/{voice_id}/with-timestamps?output_format={FORMAT}",
                     api_key, payload)
    if data is None and "HTTP 4" in (err or ""):
        payload["model_id"] = MODEL_FALLBACK
        data, err = post(
            f"/text-to-speech/{voice_id}/with-timestamps?output_format={FORMAT}",
            api_key, payload)
    if data is None:
        return None, None, err

    audio = base64.b64decode(data["audio_base64"])
    align = data.get("alignment") or {}
    words = []
    if align:
        words = strip_direction(chars_to_words(
            align["characters"],
            align["character_start_times_seconds"],
            align["character_end_times_seconds"],
        ))
    return audio, words, None


def gen_sfx(api_key, name):
    spec = B.SFX[name]
    payload = {"text": spec["prompt"], "duration_seconds": float(spec["seconds"]),
               "prompt_influence": 0.6}
    audio, err = post(f"/sound-generation?output_format={FORMAT}", api_key,
                      payload, want_json=False)
    return audio, err


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="regenerate everything")
    ap.add_argument("--only", metavar="SPREAD", help="limit to one spread id, e.g. p7")
    args = ap.parse_args()

    env = load_env()
    api_key = env["ELEVENLABS_API_KEY"]
    cast = resolve_cast(env)

    LINES.mkdir(parents=True, exist_ok=True)
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    prov = {} if args.force else (
        json.loads(PROVENANCE.read_text()) if PROVENANCE.exists() else {})

    targets = [b for b in B.BLOCKS if not args.only or b[5] == args.only]
    speech = [b for b in targets if b[1] == "speech"]
    # CC0 effects are fetched by tools/fetch_sfx.py and mastered there. Generating
    # over them would silently replace real Foley with a described approximation.
    sfx_names = sorted({b[2] for b in targets
                        if b[1] == "sfx" and B.SFX[b[2]]["source"] == "gen"})

    print(f"\n  THE HUSHABALOO -- generating")
    print(f"  {len(speech)} speech blocks, {len(sfx_names)} sound effects"
          f"{' (forced)' if args.force else ''}\n")

    made = skipped = failed = 0

    # -- sound effects: one file per effect, reused by every block referencing it --
    for name in sfx_names:
        path = SFX_DIR / f"{name}.mp3"
        fp = sfx_fingerprint(name)
        if path.exists() and prov.get(f"sfx:{name}") == fp:
            print(f"  skip  sfx/{name}")
            skipped += 1
            continue
        print(f"  gen   sfx/{name} ...", end="", flush=True)
        audio, err = gen_sfx(api_key, name)
        if audio is None:
            print(f"  FAILED\n        {err}")
            failed += 1
        else:
            path.write_bytes(audio)
            prov[f"sfx:{name}"] = fp
            print(f"  ok ({len(audio)//1024} KB)")
            made += 1
        time.sleep(THROTTLE)

    # -- speech --
    timings = {}
    if TIMESTAMPS.exists() and not args.force:
        timings = json.loads(TIMESTAMPS.read_text())

    for bid, _kind, voice, text, _pause, _spread in speech:
        path = LINES / f"{bid}.mp3"
        fp = fingerprint("speech", voice, text, cast)
        if path.exists() and prov.get(bid) == fp and bid in timings:
            print(f"  skip  {bid}")
            skipped += 1
            continue

        preview = visible_text(text)[:52]
        print(f"  gen   {bid:<22} ({voice}) \"{preview}...\"", end="", flush=True)
        audio, words, err = gen_speech(api_key, cast[voice], text, voice)
        if audio is None:
            print(f"  FAILED\n        {err}")
            failed += 1
        else:
            path.write_bytes(audio)
            timings[bid] = words
            prov[bid] = fp
            expect = len(visible_text(text).split())
            flag = "" if len(words) == expect else f"  [!] {len(words)} timings vs {expect} words"
            print(f"  ok{flag}")
            made += 1
        time.sleep(THROTTLE)

    PROVENANCE.write_text(json.dumps(prov, indent=2))
    TIMESTAMPS.write_text(json.dumps(timings, indent=2))

    print(f"\n  generated {made}, skipped {skipped}, failed {failed}")
    print(f"  timings -> {TIMESTAMPS.relative_to(ROOT)}")
    if failed:
        print("  Re-run to retry only the failures.\n")
        return 1
    print("  Next: python tools/audit.py\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
