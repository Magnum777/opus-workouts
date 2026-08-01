"""Audit recent prompt-pack posts for non-ASCII characters and emoji."""
import re
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\compj\.openclaw\workspace\scripts")
from vault_helper import get_credential
import base64
import requests

# CJK ranges (basic + extensions)
CJK_RANGES = [
    (0x4E00, 0x9FFF),       # CJK Unified Ideographs
    (0x3400, 0x4DBF),       # CJK Extension A
    (0x20000, 0x2A6DF),     # CJK Extension B
    (0xF900, 0xFAFF),       # CJK Compatibility Ideographs
    (0x2F800, 0x2FA1F),     # CJK Compatibility Supplement
]
EMOJI_RANGES = [
    (0x1F300, 0x1F9FF),     # Misc Symbols and Pictographs, Emoticons
    (0x1F600, 0x1F64F),     # Emoticons
    (0x1F680, 0x1F6FF),     # Transport and Map
    (0x2600, 0x26FF),       # Misc symbols
    (0x2700, 0x27BF),       # Dingbats
    (0x1FA70, 0x1FAFF),     # Symbols and Pictographs Extended-A
]


def classify_chars(text):
    cjk, emoji = [], []
    for ch in text:
        cp = ord(ch)
        if any(lo <= cp <= hi for lo, hi in CJK_RANGES):
            cjk.append((ch, hex(cp)))
        elif any(lo <= cp <= hi for lo, hi in EMOJI_RANGES):
            emoji.append((ch, hex(cp)))
    return cjk, emoji


def strip_html(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


for site in ["aitoolalliance.com", "aicofounderstack.com"]:
    key_prefix = site.replace(".com", "").replace(".org", "")
    url = get_credential("wordpress", f"{key_prefix}_url")
    user = get_credential("wordpress", f"{key_prefix}_user")
    pw = get_credential("wordpress", f"{key_prefix}_pass")
    auth = base64.b64encode(f"{user}:{pw}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}
    r = requests.get(f"{url}/wp-json/wp/v2/posts?per_page=5&search=prompt+pack",
                     headers=headers, timeout=30)
    print(f"\n=== {site} ===")
    if r.status_code != 200:
        print(f"  http {r.status_code}: {r.text[:200]}")
        continue
    for p in r.json()[:3]:
        content = p["content"]["rendered"]
        text = strip_html(content)
        cjk, emoji = classify_chars(text)
        print(f"  post {p['id']}: {p['title']['rendered'][:60]}")
        print(f"    non-ASCII: {sum(1 for c in text if ord(c) > 127)}")
        print(f"    CJK chars: {len(cjk)}  emoji: {len(emoji)}")
        if cjk[:5]:
            print(f"    CJK samples: {cjk[:5]}")
        if emoji[:5]:
            print(f"    emoji samples: {emoji[:5]}")
        print(f"    text: {text[:250]}")
