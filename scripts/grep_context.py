#!/usr/bin/env python3
"""
Lightweight file search utility for context-efficient file inspection.
Usage: python scripts/grep_context.py <pattern> <path> [options]

Designed to replace full file reads when you only need specific lines.
Returns compact results with line numbers, not entire file contents.

Examples:
  python scripts/grep_context.py "password" scripts/
  python scripts/grep_context.py "def main" scripts/td_manager.py
  python scripts/grep_context.py "hardcoded|D0nga" scripts/ --ext .py,.ps1
"""
import re
import sys
import os
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        print("Usage: python grep_context.py <pattern> <path> [--ext .py,.ps1] [--max 20] [--context 0]")
        sys.exit(1)

    pattern = sys.argv[1]
    search_path = sys.argv[2]
    ext_filter = None
    max_lines = 20
    context_lines = 0

    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == "--ext" and i + 1 < len(sys.argv):
            ext_filter = [e.strip() for e in sys.argv[i + 1].split(",")]
            i += 2
        elif sys.argv[i] == "--max" and i + 1 < len(sys.argv):
            max_lines = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--context" and i + 1 < len(sys.argv):
            context_lines = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1

    regex = re.compile(pattern, re.IGNORECASE)
    total_matches = 0
    files_searched = 0

    search = Path(search_path)
    if search.is_file():
        files = [search]
    else:
        files = sorted(search.rglob("*"))

    for fpath in files:
        if fpath.is_dir():
            continue
        if ext_filter and fpath.suffix not in ext_filter:
            continue
        # Skip binary-ish and large files
        if fpath.stat().st_size > 500_000:
            continue
        if fpath.suffix in ('.zip', '.7z', '.exe', '.dll', '.pyc', '.db'):
            continue

        files_searched += 1
        try:
            lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue

        matches_in_file = []
        for i, line in enumerate(lines):
            if regex.search(line):
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                for j in range(start, end):
                    matches_in_file.append((j + 1, lines[j]))
                matches_in_file.append(("", ""))  # separator

        if matches_in_file:
            rel = fpath.relative_to(Path.cwd()) if fpath.is_relative_to(Path.cwd()) else fpath
            print(f"\n=== {rel} ({len([m for m in matches_in_file if m[0]])} matches) ===")
            shown = 0
            for line_no, line_text in matches_in_file:
                if line_no == "":
                    print()
                    continue
                if shown >= max_lines:
                    print(f"  ... ({len(matches_in_file)} total, showing first {max_lines})")
                    break
                print(f"  {line_no}: {line_text.rstrip()}")
                shown += 1
            total_matches += len([m for m in matches_in_file if m[0]])

    print(f"\n--- {total_matches} matches in {files_searched} files ---")

if __name__ == "__main__":
    main()