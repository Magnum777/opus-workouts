#!/usr/bin/env python3
"""
Prompt Pack Orchestrator — runs from the daily cron agent turn.

Flow per site:
  1. prompt_pack_gen.pick_topic(site) — topic with 30-day no-repeat
  2. Agent turn fills the JSON body (title, excerpt, prompts, intro_html, footer_html)
  3. publisher_v3.create_post(site, ...) -> draft first, then publish
  4. prompt_pack_crossposter.crosspost(site, topic, post_url, title, prompts)

The cron agent turn wraps this orchestrator.  We accept the filled JSON as a
single --content-json argument so the agent can paste in the model output.

Enforces Opus's no-emoji / no-em-dash / no-CJK rules on every text field
before publishing. Prompts get the same clean pass since Opus doesn't want
those chars in any cron output (the accuracy rule applies to the words,
not to forbidden characters).

403 fallback: if WP REST API returns 403 (Cloudflare bot challenge, common
on aibusinessinsider.org), queue the post as a WXR export to
memory/prompt-pack-aibusinessinsider-queue/ for later replay. The cron
never dies silently.

Usage:
  python prompt_pack_orchestrator.py \
      --site aitoolalliance.com \
      --content-json '{"title":"...", "excerpt":"...", "prompts":[...], "intro_html":"...", "footer_html":"..."}'
  python prompt_pack_orchestrator.py \
      --site aitoolalliance.com \
      --content-json-file /path/to/content.json
"""

import argparse
import json
import sys
from pathlib import Path

THIS_DIR = Path(__file__).parent
sys.path.insert(0, str(THIS_DIR))
from publisher_v3 import create_post, SITES, update_post
import prompt_pack_gen
import prompt_pack_crossposter
import wxr_export
from prompt_pack_crossposter import clean_for_posting, humanize


def render_post_html(content_json, humanize_wrapper=True):
    """Combine intro + prompts + footer into WordPress HTML.

    Per Opus: the 3 prompts are the product and must stay verbatim in their
    WORDS (100% accurate). The intro_html, footer_html, title, and excerpt
    get humanized AND cleaned (CJK/emoji/em-dash/curly quotes stripped per
    Opus's hard rules). Prompt bodies also get the char-clean pass since
    the accuracy rule applies to words, not forbidden characters.
    """
    intro = content_json["intro_html"]
    footer = content_json.get("footer_html", "")
    if humanize_wrapper:
        intro = humanize(intro)
        footer = humanize(footer)
    intro = clean_for_posting(intro)
    footer = clean_for_posting(footer)

    parts = [intro]
    for p in content_json["prompts"]:
        tag = p.get("tag", "").strip()
        body = p.get("body", "").strip()
        # Clean tag + body of forbidden chars but keep the words intact
        tag = clean_for_posting(tag)
        body = clean_for_posting(body)
        parts.append(f'<h3>{tag}</h3>')
        parts.append(f'<p>{body}</p>')
    parts.append(footer)
    return "\n".join(parts)


def run(site_key, content_json, dry_run=False):
    """Publish to WP then cross-post to X/Bluesky/Pinterest."""
    # Clean wrapper text fields before they touch anything
    title = clean_for_posting(content_json["title"])
    excerpt = clean_for_posting(content_json.get("excerpt", ""))
    html = render_post_html(content_json)
    topic = prompt_pack_gen._load_state()["sites"].get(site_key, {}).get("history", [{}])[-1].get("topic", "")
    if not topic:
        topic = prompt_pack_gen.pick_topic(site_key) or "AI"
    topic = clean_for_posting(topic)

    summary = {"site": site_key, "title": title, "topic": topic}

    if dry_run:
        summary["dry_run"] = True
        summary["html_preview"] = html[:600]
        return summary

    # 1. Publish draft first (so we have a URL even if social fails)
    draft = create_post(site_key, title=title, content=html, status="draft", excerpt=excerpt)
    summary["draft"] = draft

    # 403 fallback: Cloudflare bot challenge blocking the WP REST API.
    # Queue as WXR so the post isn't lost; replay later when the block
    # clears or you set up a proxy. Common on aibusinessinsider.org.
    if not draft.get("ok"):
        err_text = json.dumps(draft)
        if "403" in err_text or "forbidden" in err_text.lower() or "cloudflare" in err_text.lower():
            print(f"[orchestrator] {site_key} WP 403 - queuing as WXR fallback")
            wxr_path, meta_path = wxr_export.queue_post(
                site_key, title, html, excerpt=excerpt, author="admin"
            )
            summary["wxr_fallback"] = {"wxr": wxr_path, "meta": meta_path, "reason": "WP REST 403"}
            summary["post_url"] = None
            # Skip cross-post: we have no live URL yet. The replay
            # script will pick up the WXR queue and post later.
            return summary
        summary["error"] = "draft creation failed"
        return summary

    # 2. Flip to publish
    pub = update_post(site_key, draft["id"], status="publish")
    summary["published"] = pub
    if not pub.get("ok"):
        summary["error"] = "publish failed"
        return summary

    post_url = pub.get("link") or draft.get("link")
    summary["post_url"] = post_url

    # 3. Cross-post
    prompts = [f"{p.get('tag','')} {p.get('body','')}".strip() for p in content_json["prompts"]]
    cross = prompt_pack_crossposter.crosspost(site_key, topic, post_url, title, prompts)
    summary["crosspost"] = cross

    return summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--site", required=True, choices=list(SITES.keys()))
    p.add_argument("--content-json",
                   help="JSON string with title, excerpt, prompts, intro_html, footer_html")
    p.add_argument("--content-json-file", dest="content_json_file",
                   help="Path to JSON file containing the content (alternative to --content-json)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if args.content_json_file:
        content = json.load(open(args.content_json_file, "r", encoding="utf-8"))
    elif args.content_json:
        content = json.loads(args.content_json)
    else:
        p.error("One of --content-json or --content-json-file is required")
    out = run(args.site, content, dry_run=args.dry_run)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
