"""Replay Pinterest pin posts from saved drafts.

Used when X/Bluesky went through but Pinterest failed (board_id field name
was wrong, or title was too long). Reads the saved draft + PNG from
memory/prompt-pack-social-drafts/ and re-posts to Pinterest only.
"""
import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

import requests

DRAFT_DIR = Path(r"C:\Users\compj\.openclaw\workspace\memory\prompt-pack-social-drafts")
VAULT_PATH = Path(r"C:\Users\compj\.openclaw\workspace\scripts\credentials\vault.db")

PIN_BOARDS = {
    "aitoolalliance.com": "1124140825679666015",
    "aicofounderstack.com": "1124140825679666017",
}


def api_key():
    conn = sqlite3.connect(str(VAULT_PATH))
    row = conn.execute(
        "SELECT value FROM credentials WHERE service='upload_post' AND key='api_key'"
    ).fetchone()
    conn.close()
    return row[0] if row else None


def replay_pinterest(site_key):
    key = api_key()
    if not key:
        print("no api key")
        return False
    if site_key not in PIN_BOARDS:
        print(f"no board for {site_key}")
        return False

    today = datetime.now().strftime("%Y-%m-%d")
    drafts = sorted(DRAFT_DIR.glob(f"{today}_{site_key}_pinterest.json"))
    if not drafts:
        drafts = sorted(DRAFT_DIR.glob(f"*_{site_key}_pinterest.json"))
    if not drafts:
        print(f"no Pinterest drafts for {site_key}")
        return False
    draft_path = drafts[-1]
    draft = json.loads(draft_path.read_text(encoding="utf-8"))

    image_field = draft.get("image", "")
    if not image_field:
        print(f"draft {draft_path} has no image field")
        return False
    image_path = Path(image_field)
    if not image_path.exists():
        print(f"image missing: {image_path}")
        return False

    # New drafts save title + description separately. Old ones had only 'text'.
    pin_title = draft.get("title", "")
    pin_description = draft.get("description", "")
    if not pin_title:
        # Fallback: rebuild from saved caption (old shape) or use first 100 chars
        pin_title = (draft.get("text") or "")[:100]
        pin_description = draft.get("text", "")

    print(f"replaying: {draft_path}")
    print(f"image: {image_path}")
    print(f"title ({len(pin_title)} chars): {pin_title}")
    print(f"description ({len(pin_description)} chars): {pin_description[:120]}...")

    url_api = "https://api.upload-post.com/api/upload_photos"
    files = {"photos[]": (image_path.name, open(image_path, "rb"), "image/png")}
    data = {
        "user": "nova",
        "platform[]": ["pinterest"],
        "title": pin_title,
        "description": pin_description,
        "pinterest_board_id": PIN_BOARDS[site_key],
    }
    r = requests.post(
        url_api,
        headers={"Authorization": f"Apikey {key}"},
        data=data,
        files=files,
        timeout=60,
    )
    print(f"status: {r.status_code}")
    print(r.text[:500])
    return r.status_code in (200, 201)


if __name__ == "__main__":
    sites = sys.argv[1:] if len(sys.argv) > 1 else ["aitoolalliance.com", "aicofounderstack.com"]
    for s in sites:
        print(f"\n=== {s} ===")
        replay_pinterest(s)
