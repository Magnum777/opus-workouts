#!/usr/bin/env python3
"""
shared_text.py — workspace-wide text sanitization for cron output.

Enforces Opus's hard rules on any text that gets published by an automated
cron (WordPress, X, Bluesky, Pinterest, LinkedIn, Reddit, email, etc.):

  - No em dashes (U+2014)
  - No en dashes (U+2013)
  - No curly quotes (U+2018, U+2019, U+201C, U+201D)
  - No Unicode ellipsis (U+2026)
  - No CJK characters (U+4E00-9FFF, U+3400-4DBF, U+F900-FAFF)
  - No emoji (U+1F300-1F9FF, U+1F600-1F64F, U+1F680-1F6FF, U+2600-27BF, U+1FA70-1FAFF)
  - No HTML entity versions of the above (rendered the same way)

The replacement rules:

  em-dash    -> " - " (spaced hyphen)
  en-dash    -> "-"
  curly quotes -> straight quotes
  ellipsis   -> "..."

CJK, emoji, and exotic symbols without a clean ASCII equivalent are
dropped silently (logged once per call).

This is the single source of truth for "clean text for posting." All
cron scripts should import this and call clean_for_posting() on any
string that will be published.

Per .learnings/NO_EM_DASHES.md + Opus's hard "no emoji" rule (2026-07-31).
"""

import re

# Character classes Opus explicitly forbids in cron-published text.
_FORBIDDEN_CHAR_RANGES = [
    (0x2014, 0x2014),   # em dash
    (0x2013, 0x2013),   # en dash
    (0x2018, 0x2018),   # left single quote
    (0x2019, 0x2019),   # right single quote / apostrophe
    (0x201C, 0x201C),   # left double quote
    (0x201D, 0x201D),   # right double quote
    (0x2026, 0x2026),   # ellipsis
    (0x4E00, 0x9FFF),   # CJK Unified Ideographs
    (0x3400, 0x4DBF),   # CJK Extension A
    (0xF900, 0xFAFF),   # CJK Compatibility Ideographs
    (0x1F300, 0x1F9FF), # Misc Symbols and Pictographs, Emoticons
    (0x1F600, 0x1F64F), # Emoticons
    (0x1F680, 0x1F6FF), # Transport and Map
    (0x2600, 0x26FF),   # Misc symbols
    (0x2700, 0x27BF),   # Dingbats
    (0x1FA70, 0x1FAFF), # Symbols and Pictographs Extended-A
]

# Replacement map for chars that have clean ASCII equivalents.
_CHAR_SWAPS = {
    "\u2014": " - ",   # em dash -> spaced hyphen
    "\u2013": "-",     # en dash -> hyphen
    "\u2018": "'",     # left single quote
    "\u2019": "'",     # right single quote
    "\u201C": '"',     # left double quote
    "\u201D": '"',     # right double quote
    "\u2026": "...",   # ellipsis -> three dots
}

# HTML entity versions that might appear in already-rendered HTML.
_HTML_ENTITY_FIXES = [
    ("&#8217;", "'"),
    ("&#8216;", "'"),
    ("&#8220;", '"'),
    ("&#8221;", '"'),
    ("&#8230;", "..."),
    ("&mdash;", " - "),
    ("&ndash;", "-"),
    ("&rsquo;", "'"),
    ("&lsquo;", "'"),
    ("&rdquo;", '"'),
    ("&ldquo;", '"'),
    ("&hellip;", "..."),
]


def _is_forbidden(ch):
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in _FORBIDDEN_CHAR_RANGES)


def has_forbidden_chars(text):
    """Return True if `text` contains any forbidden char or HTML entity.

    Useful as a preflight check before posting.
    """
    if not text:
        return False
    for ch in text:
        if _is_forbidden(ch):
            return True
    for entity, _ in _HTML_ENTITY_FIXES:
        if entity in text:
            return True
    return False


def clean_for_posting(text, verbose=False):
    """Strip Opus-forbidden chars from `text`.

    - em-dashes / en-dashes / curly quotes / ellipsis get ASCII replacements
    - CJK / emoji / exotic symbols without a clean equivalent get dropped
    - HTML entity versions of these chars get replaced too

    Use on any string that gets published by a cron: titles, excerpts,
    post bodies, social captions, email subjects/bodies. Safe to call
    on empty strings.

    The 'accuracy' rule for prompts applies to the WORDS, not to forbidden
    characters - prompts that happen to contain emoji or em-dashes should
    still pass through this clean.
    """
    if not text:
        return text
    out_chars = []
    removed = 0
    for ch in text:
        if _is_forbidden(ch):
            if ch in _CHAR_SWAPS:
                out_chars.append(_CHAR_SWAPS[ch])
            else:
                removed += 1
        else:
            out_chars.append(ch)
    out = "".join(out_chars)
    # HTML entity fixes
    for entity, replacement in _HTML_ENTITY_FIXES:
        out = out.replace(entity, replacement)
    # Collapse double spaces from em-dash replacement
    out = re.sub(r"  +", " ", out)
    if verbose and removed:
        print(f"[clean_for_posting] dropped {removed} forbidden chars (CJK/emoji/exotic)")
    return out
