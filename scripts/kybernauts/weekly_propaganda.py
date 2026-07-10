#!/usr/bin/env python3
"""
Kybernauts Weekly Propaganda Rotation
Posts ONE image tweet per week + ONE YouTube link tweet per week.
Cycles through 6 images and rotates text/captions.
"""
import json
import os
import sys
import random
from datetime import datetime

# Config
API_KEY = "UPLOADPOST_API_KEY_REDACTED"
PROFILE = "Kybernauts"
STATE_FILE = "data/kybernauts/propaganda_rotation.json"

# Image inventory (6 images) — clean versions without URL text overlay
# URL goes in tweet text (clickable via t.co shortener) NOT burned into image
IMAGES = [
    ("data/kybernauts/propaganda/01_liberate.png", [
        "The stars belong to the Clade. Join the transformation. http://join.kybernauts.today #EVEOnline #Pochven",
        "Liberation is not given. It is taken. Join the Clade. http://join.kybernauts.today #EVEOnline #Pochven",
        "Break free from the Singularity's chains. http://join.kybernauts.today #EVEOnline #Pochven",
    ]),
    ("data/kybernauts/propaganda/02_p92.png", [
        "The Clade does not ask. It beckons. Answer the call. http://join.kybernauts.today #EVEOnline #Pochven",
        "P-92: Proof that the worthy still rise. Are you among them? http://join.kybernauts.today #EVEOnline #Pochven",
        "Only the bold answer the beacon. http://join.kybernauts.today #EVEOnline #Pochven",
    ]),
    ("data/kybernauts/propaganda/03_kkp07.png", [
        "Only the worthy ascend. Are you ready to prove yourself? http://join.kybernauts.today #EVEOnline #Pochven",
        "KKP-07: The Proving Grounds await. Will you answer? http://join.kybernauts.today #EVEOnline #Pochven",
        "Ascension demands sacrifice. The Clade demands you. http://join.kybernauts.today #EVEOnline #Pochven",
    ]),
    ("data/kybernauts/propaganda/04_chatgpt.png", [
        "The fire of the Clade burns eternal. http://join.kybernauts.today #EVEOnline #Pochven",
        "From the ashes of the Singularity, the Clade rises. http://join.kybernauts.today #EVEOnline #Pochven",
        "The forge is hot. The worthy are few. http://join.kybernauts.today #EVEOnline #Pochven",
    ]),
    ("data/kybernauts/propaganda/05_p09.png", [
        "Pochven awaits those bold enough to answer. Will you? http://join.kybernauts.today #EVEOnline #Pochven",
        "P-09: The frontier calls. Not all who hear it answer. http://join.kybernauts.today #EVEOnline #Pochven",
        "The red forest whispers. Will you listen? http://join.kybernauts.today #EVEOnline #Pochven",
    ]),
    ("data/kybernauts/propaganda/06_p93.png", [
        "The Singularity is a lie. The Clade is truth. Join us. http://join.kybernauts.today #EVEOnline #Pochven",
        "P-93: Proof that truth endures beyond the false dawn. http://join.kybernauts.today #EVEOnline #Pochven",
        "Reject the Singularity. Embrace the Clade. http://join.kybernauts.today #EVEOnline #Pochven",
    ]),
]

# YouTube video link tweets (rotating text)
YOUTUBE_URL = "https://www.youtube.com/watch?v=qTWUFguQWhc"
YOUTUBE_TEXTS = [
    "See the fire that drives us.\n\n{url}\n\nhttp://join.kybernauts.today\n#EVEOnline #Pochven",
    "The Clade does not hide. See for yourself.\n\n{url}\n\nhttp://join.kybernauts.today\n#EVEOnline #Pochven",
    "Before you join, understand what awaits.\n\n{url}\n\nhttp://join.kybernauts.today\n#EVEOnline #Pochven",
    "This is what Pochven looks like from the inside.\n\n{url}\n\nhttp://join.kybernauts.today\n#EVEOnline #Pochven",
]


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_image_idx": -1, "last_youtube_idx": -1, "weeks": []}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def post_to_x(image_path, text, dry_run=False):
    """Post image + text to X and Bluesky via Upload-Post API."""
    import subprocess

    if dry_run:
        print(f"[DRY RUN] Would post:")
        print(f"  Image: {image_path}")
        print(f"  Text:  {text}")
        return {"success": True, "dry_run": True}

    abs_path = os.path.abspath(image_path)
    if not os.path.exists(abs_path):
        return {"success": False, "error": f"Image not found: {abs_path}"}

    cmd = [
        "curl", "-s", "-X", "POST",
        "https://api.upload-post.com/api/upload_photos",
        "-H", f"Authorization: Apikey {API_KEY}",
        "-F", f"user={PROFILE}",
        "-F", "platform[]=x",
        "-F", "platform[]=bluesky",
        "-F", f"photos[]=@C:\\Users\\compj\\.openclaw\\workspace\\{image_path}",
        "-F", f"title={text}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"success": False, "error": result.stdout or result.stderr}


def post_youtube_text(text, dry_run=False):
    """Post text-only tweet with YouTube link to X and Bluesky."""
    import subprocess

    if dry_run:
        print(f"[DRY RUN] Would post YouTube tweet:")
        print(f"  Text: {text}")
        return {"success": True, "dry_run": True}

    cmd = [
        "curl", "-s", "-X", "POST",
        "https://api.upload-post.com/api/upload_text",
        "-H", f"Authorization: Apikey {API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "user": PROFILE,
            "platform": ["x", "bluesky"],
            "title": text,
        }),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"success": False, "error": result.stdout or result.stderr}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["image", "youtube", "both"], default="both",
                        help="What to post this run")
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting")
    args = parser.parse_args()

    state = load_state()

    results = []

    if args.mode in ("image", "both"):
        # Rotate to next image
        idx = (state["last_image_idx"] + 1) % len(IMAGES)
        image_path, captions = IMAGES[idx]
        caption = random.choice(captions)

        if args.dry_run:
            result = post_to_x(image_path, caption, dry_run=True)
            results.append({"type": "image", "idx": idx, "result": result})
            # DO NOT advance state on dry run
        else:
            result = post_to_x(image_path, caption, dry_run=False)
            results.append({"type": "image", "idx": idx, "result": result})
            state["last_image_idx"] = idx

    if args.mode in ("youtube", "both"):
        # Rotate to next YouTube text
        yt_idx = (state.get("last_youtube_idx", -1) + 1) % len(YOUTUBE_TEXTS)
        text = YOUTUBE_TEXTS[yt_idx].format(url=YOUTUBE_URL)

        if args.dry_run:
            result = post_youtube_text(text, dry_run=True)
            results.append({"type": "youtube", "idx": yt_idx, "result": result})
            # DO NOT advance state on dry run
        else:
            result = post_youtube_text(text, dry_run=False)
            results.append({"type": "youtube", "idx": yt_idx, "result": result})
            state["last_youtube_idx"] = yt_idx

    # Record this run
    state["weeks"].append({
        "date": datetime.now().isoformat(),
        "mode": args.mode,
        "dry_run": args.dry_run,
        "results": results,
    })

    save_state(state)

    # Report
    for r in results:
        if r["result"].get("success"):
            x_url = r["result"].get("results", {}).get("x", {}).get("url", "N/A")
            bsky_url = r["result"].get("results", {}).get("bluesky", {}).get("url", "N/A")
            if r["type"] == "image":
                print(f"IMAGE - X: {x_url}")
                print(f"IMAGE - Bluesky: {bsky_url}")
            else:
                print(f"YOUTUBE - X: {x_url}")
                print(f"YOUTUBE - Bluesky: {bsky_url}")
        else:
            print(f"FAILED ({r['type']}): {r['result'].get('error', 'unknown')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
