#!/usr/bin/env python3
"""Parse OpenClaw logs for compaction events."""
import re, sys

PATTERN = re.compile(
    r"truncating in injected context.*limit\s+(\d+).*?(\d+)\s+chars",
    re.IGNORECASE
)

def scan(path: str):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = PATTERN.search(line)
            if m:
                limit, actual = int(m.group(1)), int(m.group(2))
                print(f"Compaction: {actual} chars → {limit} chars (saved {actual-limit} chars)")

if __name__ == "__main__":
    scan(sys.argv[1] if len(sys.argv) > 1 else ".openclaw/logs/latest.log")
