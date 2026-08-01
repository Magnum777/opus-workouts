#!/usr/bin/env python3
"""
WXR Export — WordPress eXtended RSS file format.

Used to queue posts for sites whose WP REST API is unreachable (Cloudflare
bot challenge 403). The WXR file can be imported later via
WP Admin -> Tools -> Import -> WordPress, or replayed via a working REST
API endpoint once the blocker clears.

Reference: https://wordpress.org/documentation/article/tools-import-screen/

Usage:
  python wxr_export.py \
      --site aibusinessinsider.org \
      --title "Daily Prompt Pack: marketing operations" \
      --content "<p>...</p>" \
      --excerpt "Three copy-paste prompts..." \
      --author admin
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

QUEUE_DIR = Path(r"C:\Users\compj\.openclaw\workspace\memory\prompt-pack-aibusinessinsider-queue")
QUEUE_DIR.mkdir(parents=True, exist_ok=True)


def _slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:80] or "post"


def _escape_cdata(text):
    """Escape CDATA content. WP WXR allows raw HTML inside CDATA blocks."""
    return text.replace("]]>", "]]]]><![CDATA[>")


def build_wxr(site_key, title, content, excerpt="", author="admin"):
    """Build a minimal valid WXR document for one post.

    Includes the standard WXR header, channel metadata, and a single <item>
    of post type. Ready for WP Admin import or programmatic replay.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pub_date = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    slug = _slugify(title)
    post_id = int(datetime.now().timestamp())
    site_url = f"https://{site_key}"

    wxr = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0"
  xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
  xmlns:wfw="http://wellformedweb.org/CommentAPI/"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:wp="http://wordpress.org/export/1.2/">
<channel>
  <title>{site_key}</title>
  <link>{site_url}</link>
  <description>Queued post for {site_key} (Cloudflare 403 workaround)</description>
  <pubDate>{pub_date}</pubDate>
  <language>en-US</language>
  <wp:wxr_version>1.2</wp:wxr_version>
  <generator>prompt_pack_orchestrator.py / WXR fallback</generator>
  <item>
    <title>{_xml_escape(title)}</title>
    <link>{site_url}/?p={post_id}</link>
    <pubDate>{pub_date}</pubDate>
    <dc:creator><![CDATA[{author}]]></dc:creator>
    <guid isPermaLink="false">{site_url}/?p={post_id}</guid>
    <description></description>
    <content:encoded><![CDATA[{_escape_cdata(content)}]]></content:encoded>
    <excerpt:encoded><![CDATA[{_escape_cdata(excerpt)}]]></excerpt:encoded>
    <wp:post_id>{post_id}</wp:post_id>
    <wp:post_date>{now}</wp:post_date>
    <wp:post_date_gmt>{now}</wp:post_date_gmt>
    <wp:post_name>{slug}</wp:post_name>
    <wp:status>publish</wp:status>
    <wp:post_type>post</wp:post_type>
  </item>
</channel>
</rss>"""
    return wxr


def _xml_escape(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def queue_post(site_key, title, content, excerpt="", author="admin"):
    """Write a WXR file to the queue. Returns the file path."""
    wxr = build_wxr(site_key, title, content, excerpt=excerpt, author=author)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    fname = QUEUE_DIR / f"{timestamp}_{_slugify(title)}.wxr.xml"
    fname.write_text(wxr, encoding="utf-8")
    # Also write a sidecar JSON with the parsed fields for replay tooling
    sidecar = QUEUE_DIR / f"{timestamp}_{_slugify(title)}.meta.json"
    sidecar.write_text(
        json.dumps(
            {
                "site": site_key,
                "title": title,
                "excerpt": excerpt,
                "content": content,
                "author": author,
                "queued_at": datetime.now().isoformat(),
                "wxr_file": str(fname),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return str(fname), str(sidecar)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--site", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--content-file", help="Read content from file")
    p.add_argument("--excerpt", default="")
    p.add_argument("--author", default="admin")
    p.add_argument("--out", help="Output WXR path (default: queue dir)")
    args = p.parse_args()

    if args.content_file:
        content = Path(args.content_file).read_text(encoding="utf-8")
    else:
        content = args.content

    wxr_path, meta_path = queue_post(
        args.site, args.title, content, excerpt=args.excerpt, author=args.author
    )
    print(f"WXR: {wxr_path}")
    print(f"Meta: {meta_path}")


if __name__ == "__main__":
    main()
