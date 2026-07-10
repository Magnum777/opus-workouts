#!/usr/bin/env python3
"""Prune memory files older than N days. Run weekly."""
import os, glob, time, argparse

MEMORY_DIR = "memory"
ARCHIVE_DIR = "memory/archive"
RETENTION_DAYS = 30

def prune(path: str, days: int, dry_run: bool):
    cutoff = time.time() - (days * 86400)
    removed = 0
    for f in glob.glob(os.path.join(path, "*.md")):
        if os.path.getmtime(f) < cutoff:
            print(f"[PRUNE] {f}")
            if not dry_run:
                os.remove(f)
            removed += 1
    print(f"Pruned {removed} file(s) older than {days} days.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--days", type=int, default=RETENTION_DAYS)
    args = parser.parse_args()
    prune(ARCHIVE_DIR, args.days, args.dry_run)
