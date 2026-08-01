"""
One-shot: replace long descriptive stage directions with short canonical audio tags.

eleven_v3 recognises a fixed vocabulary of short tags ([whispers], [excited], ...).
Anything else is a coin flip: ElevenLabs documents that v3 "sometimes reads your
tags out loud instead of applying them," and a tag that matches nothing recognised
is overwhelmingly likely to be read. That is exactly what happened to the
Hushabaloo on spread 7 -- 2.5 seconds of him reading his own stage direction.

So: only vetted tags, at most two per block, and never a sentence inside brackets.
Expressiveness comes mainly from stability 0.0 plus the punctuation of the verse;
tags are a nudge, not the mechanism.

    python tools/_normalize_tags.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "script"))
import blocks as B  # noqa: E402

# The only tags allowed anywhere in the book. Short, canonical, documented.
VETTED = ["whispers", "excited", "curious", "sad", "warmly",
          "shouts", "sighs", "laughs", "nervously", "mischievously"]

# Longest phrases first so "very quiet" wins over "quiet".
KEYWORDS = [
    (["barely a whisper", "almost inaudible", "very quiet", "hushed", "whisper",
      "very small", "very softly", "barely breathing", "softly", "quiet", "small",
      "empty", "flat", "hollow"], "whispers"),
    (["exhilarated", "headlong", "unstoppable", "exultant", "triumphant", "soaring",
      "delighted", "joyful", "joyously", "gleeful", "excited", "thrilled", "big",
      "building", "quickening", "urgent", "fast", "breathless", "pure joy",
      "everything at once", "brightening", "spark"], "excited"),
    (["puzzled", "curious", "wondering", "awe", "marvelling", "interested",
      "craning", "bolt upright", "round and wide", "secretive", "conspiratorial",
      "leaning in", "matter-of-fact", "dry", "reveal", "watchful"], "curious"),
    (["heartbroken", "deflating", "mournful", "sad", "grief", "pitying",
      "stunned", "troubled", "dreadful", "wary", "alarmed", "worst"], "sad"),
    (["tender", "gentle", "fond", "proud", "contented", "warm", "amused",
      "relieved", "sincere", "playful", "inviting", "smile", "grin", "lilting",
      "bright", "kind"], "warmly"),
    (["scared", "frightened", "afraid", "uneasy"], "nervously"),
]


def canonical(direction):
    """Map one long direction to a single vetted tag, or None."""
    low = direction.lower()
    for words, tag in KEYWORDS:
        if any(w in low for w in words):
            return tag
    return None


def convert(text):
    """Rewrite every [direction] in a block; keep at most two, drop duplicates."""
    kept = []

    def sub(m):
        tag = canonical(m.group(1))
        if tag is None or tag in kept or len(kept) >= 2:
            return " "
        kept.append(tag)
        return f"[{tag}] "

    out = re.sub(r"\[(.*?)\]", sub, text)
    return " ".join(out.split())


def visible(t):
    t = re.sub(r"\[.*?\]", " ", t)
    t = re.sub(r"\.{2,}", " ", t)
    return " ".join(t.split())


def main():
    src_path = ROOT / "script" / "blocks.py"
    src = src_path.read_text(encoding="utf-8")
    changed = 0

    for bid, kind, voice, text, _p, _s in B.BLOCKS:
        if kind != "speech" or "[" not in text:
            continue
        new = convert(text)
        if new == text:
            continue
        if visible(new) != visible(text):
            sys.exit(f"WORD DRIFT in {bid}\n  was: {visible(text)[:90]}\n  now: {visible(new)[:90]}")

        pat = re.compile(
            r'(\("' + re.escape(bid) + r'", "speech", "' + voice + r'",\s*)(".*?")'
            r'(,\s*(?:LINE|BEAT|SECTION|PAGE|0\.0), ")', re.S)
        m = pat.search(src)
        if not m:
            sys.exit(f"could not locate {bid}")
        src = src[:m.start(2)] + '"' + new.replace('"', '\\"') + '"' + src[m.end(2):]
        changed += 1

    src_path.write_text(src, encoding="utf-8")
    print(f"normalised {changed} blocks to canonical tags")

    # Report what survived, so the vocabulary in use is visible at a glance.
    import importlib
    importlib.reload(B)
    used = {}
    for b in B.BLOCKS:
        for t in re.findall(r"\[(.*?)\]", b[3]):
            used[t] = used.get(t, 0) + 1
    print("\n  tags now in use:")
    for t, n in sorted(used.items(), key=lambda x: -x[1]):
        mark = "ok " if t in VETTED else "!! "
        print(f"    {mark}[{t}] x{n}")
    stray = [t for t in used if t not in VETTED]
    if stray:
        sys.exit(f"\n  non-vetted tags survived: {stray}")


if __name__ == "__main__":
    main()
