#!/usr/bin/env python3
"""
Replay queued prompt-pack posts from memory/prompt-pack-aibusinessinsider-queue/.

Triggered when aibusinessinsider.org's Cloudflare 403 clears (or a proxy is
configured). Reads each meta.json sidecar, calls the WP REST API to create
+ publish the post, then deletes the WXR file on success.

Dry-run by default. Pass --execute to actually post.

Usage:
  # See what's queued
  python replay_aibusinessinsider.py

  # Dry-run one specific entry
  python replay_aibusinessinsider.py --file 2026-07-31_211000_daily-prompt-pack-marketing-operations.meta.json --dry-run

  # Push the whole queue
  python replay_aibusinessinsider.py --execute
"""

import argparse
import json
import sys
from pathlib import Path

THIS_DIR = Path(__file__).parent
sys.path.insert(0, str(THIS_DIR))

from vault_helper import get_credential
import prompt_pack_crossposter as cpc
import wxr_export
from prompt_pack_crossposter import clean_for_posting

QUEUE_DIR = Path(r"C:\Users\compj\.openclaw\workspace\memory\prompt-pack-aibusinessinsider-queue")
SITE_KEY = "aibusinessinsider.org"


def _wp_auth():
    """Pull aibusinessinsider WP creds from the vault. May 403 if CF block persists."""
    url = get_credential("wordpress", "aibusinessinsider_url")
    user = get_credential("wordpress", "aibusinessinsider_user")
    pw = get_credential("wordpress", "aibusinessinsider_pass")
    return url, user, pw


def replay_one(meta_path, dry_run=True):
    """Push one queued post via WP REST API."""
    meta = json.loads(Path(meta_path).read_text(encoding="utf-8"))
    title = clean_for_posting(meta["title"])
    content = clean_for_posting(meta["content"])
    excerpt = clean_for_posting(meta.get("excerpt", ""))

    print(f"\n--- {meta_path.name} ---")
    print(f"  title: {title[:80]}")
    print(f"  excerpt: {excerpt[:80]}")

    if dry_run:
        print(f"  DRY-RUN: would POST to {SITE_KEY}/wp-json/wp/v2/posts")
        return {"dry_run": True, "meta": str(meta_path)}

    import base64
    import requests

    url, user, pw = _wp_auth()
    auth = base64.b64encode(f"{user}:{pw}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Try draft first, then publish
    draft_resp = requests.post(
        f"{url}/wp-json/wp/v2/posts",
        headers=headers,
        json={"title": title, "content": content, "status": "draft", "excerpt": excerpt},
        timeout=60,
    )
    if draft_resp.status_code == 403:
        print(f"  403 still blocking - leaving in queue")
        return {"error": "403 still blocking", "meta": str(meta_path)}
    if draft_resp.status_code not in (200, 201):
        print(f"  draft failed: {draft_resp.status_code} {draft_resp.text[:200]}")
        return {"error": f"draft {draft_resp.status_code}", "body": draft_resp.text[:200]}

    post_id = draft_resp.json().get("id")
    pub_resp = requests.post(
        f"{url}/wp-json/wp/v2/posts/{post_id}",
        headers=headers,
        json={"status": "publish"},
        timeout=30,
    )
    if pub_resp.status_code not in (200, 201):
        print(f"  publish failed: {pub_resp.status_code}")
        return {"error": f"publish {pub_resp.status_code}", "post_id": post_id}

    post_url = pub_resp.json().get("link")
    print(f"  PUBLISHED: {post_url}")

    # Cross-post now that we have a live URL
    topic = meta.get("topic", "")
    prompts = meta.get("prompts") or [
        f"{p.get('tag','')} {p.get('body','')}".strip()
        for p in json.loads(meta.get("prompts_json", "[]"))
    ] or [content[:200], content[200:400], content[400:600]]
    if len(prompts) != 3:
        prompts = (prompts + ["", "", ""])[:3]
    cross = cpc.crosspost(SITE_KEY, topic, post_url, title, prompts)
    print(f"  cross-post: {json.dumps({k: v.get('status') for k, v in cross.items()})}")

    # Move files to done/ subfolder on success
    done_dir = QUEUE_DIR / "done"
    done_dir.mkdir(exist_ok=True)
    Path(meta_path).rename(done_dir / Path(meta_path).name)
    wxr_file = meta.get("wxr_file")
    if wxr_file and Path(wxr_file).exists():
        Path(wxr_file).rename(done_dir / Path(wxr_file).name)
    print(f"  moved to {done_dir}/")

    return {"ok": True, "post_url": post_url, "post_id": post_id, "cross": cross}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", help="Replay just this meta.json file")
    p.add_argument("--execute", action="store_true", help="Actually POST (default: dry-run)")
    p.add_argument("--dry-run", action="store_true", help="Force dry-run even with --execute")
    args = p.parse_args()

    dry_run = not args.execute or args.dry_run

    if not QUEUE_DIR.exists():
        print(f"No queue at {QUEUE_DIR}")
        return

    metas = sorted(QUEUE_DIR.glob("*.meta.json"))
    if args.file:
        target = QUEUE_DIR / args.file
        if not target.exists():
            print(f"Not found: {target}")
            sys.exit(1)
        metas = [target]

    if not metas:
        print("Queue empty")
        return

    print(f"{len(metas)} queued post(s) for {SITE_KEY}")
    print(f"Mode: {'DRY-RUN' if dry_run else 'EXECUTE'}\n")

    results = []
    for meta in metas:
        try:
            r = replay_one(meta, dry_run=dry_run)
        except Exception as e:
            print(f"  exception: {e}")
            r = {"exception": str(e), "meta": str(meta)}
        results.append(r)

    print(f"\n{'='*40}\nSummary: {json.dumps(results, indent=2)[:2000]}")


if __name__ == "__main__":
    main()
