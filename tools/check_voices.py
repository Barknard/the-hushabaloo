"""
Verify the ElevenLabs wiring in .env before anything tries to generate audio.

Checks the API key against the live account, then resolves every voice ID in
the cast and reports its real name back from ElevenLabs -- so a pasted ID that
points at the wrong voice is caught here rather than three minutes into a batch.

    python tools/check_voices.py

Stdlib only; nothing to install. Exits 0 when the whole cast resolves, 1 otherwise.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.elevenlabs.io/v1"
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

# Display name -> .env variable. Order is the order they appear in the book.
CAST = [
    ("Narrator", "VOICE_NARRATOR"),
    ("Etta", "VOICE_ETTA"),
    ("Kip", "VOICE_KIP"),
    ("Mo", "VOICE_MO"),
    ("The Hushabaloo", "VOICE_HUSHABALOO"),
]

OK, MISSING, BAD = "[ok]", "[--]", "[!!]"


def load_env(path):
    """Minimal .env reader -- avoids a python-dotenv dependency."""
    if not path.exists():
        sys.exit(f"{BAD} No .env at {path}\n     Copy .env.example to .env and fill it in.")
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()
    return values


def get(path, api_key):
    """GET an ElevenLabs endpoint. Returns (payload, None) or (None, reason)."""
    request = urllib.request.Request(f"{API}{path}", headers={"xi-api-key": api_key})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response), None
    except urllib.error.HTTPError as exc:
        return None, f"HTTP {exc.code}"
    except Exception as exc:  # network down, DNS, timeout
        return None, str(exc)


def main():
    env = load_env(ENV_PATH)
    api_key = env.get("ELEVENLABS_API_KEY", "")

    print(f"\n  read-along -- checking {ENV_PATH.name}\n")

    if not api_key:
        sys.exit(f"  {MISSING} ELEVENLABS_API_KEY is empty. Nothing else can be checked.\n")

    # --- the key itself ---
    account, reason = get("/user/subscription", api_key)
    if account is None:
        sys.exit(f"  {BAD} API key rejected ({reason}). Check the key in .env.\n")

    used = account.get("character_count", 0)
    limit = account.get("character_limit", 0)
    print(f"  {OK} API key valid -- tier '{account.get('tier', '?')}', "
          f"{limit - used:,} of {limit:,} characters left this cycle\n")

    # --- the cast ---
    print("  Cast")
    unresolved = []
    for role, var in CAST:
        voice_id = env.get(var, "")
        if not voice_id:
            print(f"  {MISSING} {role:<16} {var} is empty")
            unresolved.append(role)
            continue

        voice, reason = get(f"/voices/{voice_id}", api_key)
        if voice is None:
            print(f"  {BAD} {role:<16} {voice_id} did not resolve ({reason})")
            unresolved.append(role)
        else:
            print(f"  {OK} {role:<16} {voice_id}  -> \"{voice.get('name', '?')}\"")

    # --- verdict ---
    if unresolved:
        print(f"\n  Still needed: {', '.join(unresolved)}")
        print("  Design prompts for each are in script/voice-casting.md\n")
        return 1

    print("\n  Whole cast resolves. Ready to generate.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
