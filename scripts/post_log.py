#!/usr/bin/env python3
"""
post_log.py — Unified content tracking for all Nova crons.

Usage:
  python post_log.py log --project EveOnion --type article --title "..." --status published --url "..."
  python post_log.py log --project Kybernauts --type propaganda --title "..." --status draft --channel discord
  python post_log.py recent [--project PROJECT] [--days N] [--type TYPE]
  python post_log.py stats
  python post_log.py dedup --days N

All crons should call this AFTER publishing/drafting content.
Append-only JSONL — never deletes, just marks status changes.
"""
import json
import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "memory" / "post-log"
LOG_FILE = LOG_DIR / "posts.jsonl"

def ensure_dir():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

def log_entry(project: str, entry_type: str, title: str, status: str,
              channel: str = "", url: str = "", snippet: str = "",
              post_id: str = "", notes: str = ""):
    """Append a log entry."""
    ensure_dir()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project": project,
        "type": entry_type,
        "title": title[:200],
        "status": status,  # published, draft, blocked, failed
        "channel": channel,
        "url": url,
        "snippet": snippet[:200] if snippet else "",
        "post_id": post_id,
        "notes": notes,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"Logged: [{project}] {entry_type} — {status} — {title[:60]}")
    return entry

def recent_entries(project: str = None, days: int = 7, entry_type: str = None):
    """Show recent entries."""
    ensure_dir()
    if not LOG_FILE.exists():
        print("No posts logged yet.")
        return
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    entries = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
            except json.JSONDecodeError as e:
                logger.warning("Skipping malformed log line: %s", line[:100])
                continue
            ts = datetime.fromisoformat(entry.get("timestamp", ""))
            if ts < cutoff:
                continue
            if project and entry.get("project", "").lower() != project.lower():
                continue
            if entry_type and entry.get("type", "").lower() != entry_type.lower():
                continue
            entries.append(entry)
    
    if not entries:
        print(f"No entries found for project={project} type={entry_type} days={days}")
        return
    
    print(f"\n{len(entries)} entries found:\n")
    for e in entries:
        ts = e.get("timestamp", "")[:10]
        print(f"  [{ts}] {e['project']}/{e['type']} — {e['status']} — {e['title'][:60]}")
        if e.get("url"):
            print(f"    URL: {e['url']}")
        if e.get("channel"):
            print(f"    Channel: {e['channel']}")

def stats():
    """Show posting statistics."""
    ensure_dir()
    if not LOG_FILE.exists():
        print("No posts logged yet.")
        return
    
    counts = {}
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
            except json.JSONDecodeError as e:
                logger.warning("Skipping malformed log line in stats: %s", line[:100])
                continue
            proj = entry.get("project", "unknown")
            st = entry.get("status", "unknown")
            key = f"{proj}/{st}"
            counts[key] = counts.get(key, 0) + 1
    
    print("\nPost Statistics:\n")
    for key in sorted(counts.keys()):
        print(f"  {key}: {counts[key]}")

def dedup(days: int = 30):
    """Check for duplicate titles within date range."""
    ensure_dir()
    if not LOG_FILE.exists():
        print("No posts logged yet.")
        return
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    seen = {}
    dups = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
            except json.JSONDecodeError as e:
                logger.warning("Skipping malformed log line in dedup: %s", line[:100])
                continue
            ts = datetime.fromisoformat(entry.get("timestamp", ""))
            if ts < cutoff:
                continue
            title = entry.get("title", "").lower().strip()
            proj = entry.get("project", "")
            key = f"{proj}::{title}"
            if key in seen:
                dups.append((seen[key], entry))
            else:
                seen[key] = entry
    
    if dups:
        print(f"\n{len(dups)} potential duplicates found:\n")
        for orig, dup in dups:
            print(f"  ORIGINAL: [{orig.get('timestamp','')[:10]}] {orig.get('title','')[:60]}")
            print(f"  DUPLICATE: [{dup.get('timestamp','')[:10]}] {dup.get('title','')[:60]}")
    else:
        print("No duplicates found.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Unified post log")
    sub = parser.add_subparsers(dest="command")
    
    # log
    log_p = sub.add_parser("log", help="Log a post entry")
    log_p.add_argument("--project", required=True, help="Project name (EveOnion, Kybernauts, Anti-Yagas, ContentNova-aitoolalliance, etc.)")
    log_p.add_argument("--type", required=True, help="article, propaganda, tweet, news-scan, reddit, forum-bump, affiliate")
    log_p.add_argument("--title", required=True, help="Post title or headline")
    log_p.add_argument("--status", required=True, choices=["published", "draft", "blocked", "failed"], help="Post status")
    log_p.add_argument("--channel", default="", help="Where it was posted (discord, twitter, bluesky, web)")
    log_p.add_argument("--url", default="", help="Post URL if published")
    log_p.add_argument("--snippet", default="", help="First 200 chars of content")
    log_p.add_argument("--post-id", default="", help="WordPress post ID if applicable")
    log_p.add_argument("--notes", default="", help="Additional notes")
    
    # recent
    rec_p = sub.add_parser("recent", help="Show recent entries")
    rec_p.add_argument("--project", default=None)
    rec_p.add_argument("--days", type=int, default=7)
    rec_p.add_argument("--type", default=None)
    
    # stats
    sub.add_parser("stats", help="Show posting statistics")
    
    # dedup
    dedup_p = sub.add_parser("dedup", help="Check for duplicate titles")
    dedup_p.add_argument("--days", type=int, default=30)
    
    args = parser.parse_args()
    
    if args.command == "log":
        log_entry(args.project, args.type, args.title, args.status,
                  args.channel, args.url, args.snippet, args.post_id, args.notes)
    elif args.command == "recent":
        recent_entries(args.project, args.days, args.type)
    elif args.command == "stats":
        stats()
    elif args.command == "dedup":
        dedup(args.days)
    else:
        parser.print_help()