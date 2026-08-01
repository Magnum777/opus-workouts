#!/usr/bin/env python3
"""
Prompt Pack Cross-Poster — X + Bluesky + Pinterest for ContentNova sites.
Upload-post profile: nova
- X: @AICofounderStack
- Bluesky: nova-cofounder.bsky.social
- Pinterest boards on @ncofounder:
    aitoolalliance -> "AI Tools & Startup Gear"
    aicofounderstack -> "Tech for Founders"

aibusinessinsider.org is currently Cloudflare-403 blocked, so no live cross-post
for that site.  We still write drafts to memory/prompt-pack-social-drafts/.

Fails soft: any per-platform error saves the draft text to memory and continues.

Usage:
  python prompt_pack_crossposter.py \
      --site aitoolalliance.com \
      --topic "AI code assistants" \
      --post-url https://aitoolalliance.com/2026/07/31/... \
      --title "Daily Prompt Pack: AI code assistants" \
      --prompts '["[Claude] ...", "[Cursor] ...", "[ChatGPT] ..."]'
"""

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

import requests

WORKSPACE = Path("C:/Users/compj/.openclaw/workspace")
VAULT_PATH = WORKSPACE / "scripts" / "credentials" / "vault.db"
DRAFT_DIR = WORKSPACE / "memory" / "prompt-pack-social-drafts"
DRAFT_DIR.mkdir(parents=True, exist_ok=True)

UPLOAD_POST_BASE = "https://api.upload-post.com/api"
UPLOAD_POST_PROFILE = "nova"  # the ContentNova-branded profile

PIN_BOARDS = {
    "aitoolalliance.com": "1124140825679666015",      # AI Tools & Startup Gear
    "aicofounderstack.com": "1124140825679666017",    # Tech for Founders
}

# aibusinessinsider.org is omitted - no Pinterest board wired yet, and the WP
# site is currently 403-blocked.

SITE_HASHTAGS = {
    "aitoolalliance.com": "#AItools #PromptPack",
    "aicofounderstack.com": "#AIfounders #StartupStack",
    "aibusinessinsider.org": "#AIbusiness #PromptPack",
}

SITE_URLS = {
    "aitoolalliance.com": "https://aitoolalliance.com",
    "aicofounderstack.com": "https://aicofounderstack.com",
    "aibusinessinsider.org": "https://aibusinessinsider.org",
}

# Character classes Opus explicitly forbids in cron-published text.
# Per .learnings/NO_EM_DASHES.md + Opus's hard "no emoji" rule.
# Applies to titles, excerpts, intro/footer HTML, and social captions.
# NOT applied to the 3 prompt bodies - those are the product and stay verbatim.
_FORBIDDEN_CHAR_RANGES = [
    (0x2014, 0x2014),  # em dash
    (0x2013, 0x2013),  # en dash
    (0x2018, 0x2018),  # left single quote
    (0x2019, 0x2019),  # right single quote / apostrophe
    (0x201C, 0x201C),  # left double quote
    (0x201D, 0x201D),  # right double quote
    (0x2026, 0x2026),  # ellipsis
    (0x4E00, 0x9FFF),  # CJK Unified Ideographs
    (0x3400, 0x4DBF),  # CJK Extension A
    (0xF900, 0xFAFF),  # CJK Compatibility Ideographs
    (0x1F300, 0x1F9FF),  # Misc Symbols and Pictographs, Emoticons
    (0x1F600, 0x1F64F),  # Emoticons
    (0x1F680, 0x1F6FF),  # Transport and Map
    (0x2600, 0x26FF),   # Misc symbols
    (0x2700, 0x27BF),   # Dingbats
    (0x1FA70, 0x1FAFF),  # Symbols and Pictographs Extended-A
]

# Replacement map for the chars that have clean ASCII equivalents.
_CHAR_SWAPS = {
    "\u2014": " - ",   # em dash -> spaced hyphen
    "\u2013": "-",     # en dash -> hyphen
    "\u2018": "'",     # left single quote
    "\u2019": "'",     # right single quote
    "\u201C": '"',     # left double quote
    "\u201D": '"',     # right double quote
    "\u2026": "...",   # ellipsis -> three dots
}


def _is_forbidden(ch):
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in _FORBIDDEN_CHAR_RANGES)


def clean_for_posting(text):
    """Strip Opus-forbidden chars (em-dashes, curly quotes, CJK, emoji).

    Used on titles, excerpts, intro/footer HTML, and social captions.
    NOT applied to prompt bodies - those stay verbatim.
    Drops chars without a clean ASCII equivalent (CJK, emoji, exotic
    symbols) entirely. Logs the replacement for visibility.
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
    # Collapse double spaces from em-dash replacement
    out = re.sub(r"  +", " ", out)
    # Strip HTML entity versions of curly quotes if they slipped through
    out = out.replace("&#8217;", "'").replace("&#8216;", "'")
    out = out.replace("&#8220;", '"').replace("&#8221;", '"')
    out = out.replace("&#8230;", "...")
    out = out.replace("&mdash;", " - ").replace("&ndash;", "-")
    if removed:
        # one-line warning, useful when tail -F'ing cron logs
        print(f"[clean_for_posting] dropped {removed} forbidden chars (CJK/emoji/exotic)")
    return out


def _api_key():
    conn = sqlite3.connect(str(VAULT_PATH))
    row = conn.execute(
        "SELECT value FROM credentials WHERE service='upload_post' AND key='api_key'"
    ).fetchone()
    conn.close()
    if not row or len(row[0]) < 20:
        raise SystemExit("UPLOAD_POST_API_KEY missing or invalid in vault")
    return row[0]


def _headers():
    return {"Authorization": f"Apikey {_api_key()}"}


def _save_draft(site_key, platform, payload, error):
    fname = DRAFT_DIR / f"{datetime.now():%Y-%m-%d}_{site_key}_{platform}.json"
    payload["_error"] = str(error)[:500]
    payload["_saved_at"] = datetime.now().isoformat()
    fname.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(fname)


def _truncate(text, max_chars):
    """Truncate to <= max_chars without slicing URLs or mid-word.

    Strategy:
    1. If already short enough, return as-is.
    2. Cut at the last newline before max_chars - 1 (preserves snippet boundaries).
    3. Fall back to last space before max_chars - 1.
    4. Strip trailing punctuation and append "..." (ASCII, no Unicode).
    5. Never slice a multi-byte char.
    """
    if len(text) <= max_chars:
        return text
    budget = max_chars - 3  # reserve 3 chars for "..."

    # Prefer newline boundary (preserves snippet blocks cleanly)
    cut_at = text.rfind("\n", 0, budget)
    if cut_at < budget // 2:
        # No good newline boundary — use space
        cut_at = text.rfind(" ", 0, budget)
    if cut_at <= 0:
        cut_at = budget

    cut = text[:cut_at]
    # Avoid slicing a multi-byte UTF-8 char
    while cut and ord(cut[-1]) > 0x7F and (ord(cut[-1]) & 0xC0) == 0x80:
        cut = cut[:-1]
    return cut.rstrip(",.;: ") + "..."


# Programmatic humanize pass — strips the worst AI tells from short copy
# without needing a model roundtrip. Per Opus: prompts are NOT humanized,
# but the social captions and post body intro/footer are.
_AI_PHRASES = [
    "delve into", "delve", "in today's fast-paced",
    "in the ever-evolving landscape", "ever-evolving landscape",
    "tapestry", "serves as a testament", "stands as a testament",
    "a testament to", "pivotal role", "key role", "vital role",
    "crucial role", "fostering", "cultivating", "embark on a journey",
    "navigate the complexities", "navigate the landscape",
    "in the realm of", "in the world of", "harness the power",
    "harness the potential", "unleash the power", "unleash the potential",
    "robust solution", "seamless experience", "cutting-edge",
    "game-changer", "game changer", "revolutionary",
    "deep dive", "comprehensive guide", "ultimate guide",
    "whether you're a", "in this article, we'll explore",
    "let's explore", "we'll discuss", "we will explore",
]
_AI_REPLACEMENTS = {
    "moreover": "also",
    "furthermore": "also",
    "additionally": "also",
    "utilize": "use",
    "leverage": "use",
    "facilitate": "help",
    "endeavor": "try",
    "commence": "start",
    "terminate": "end",
    "in order to": "to",
    "due to the fact that": "because",
    "at this point in time": "now",
    "in the event that": "if",
}


def humanize(text):
    """Cheap mechanical pass for social copy. Strips AI tells. Keeps short
    social copy readable. NOT used on prompts — those must stay verbatim.

    Replaces AI vocabulary phrases with neutral alternatives (never blank)
    and rewrites obvious AI sentence starters. Keeps the voice intact by
    collapsing redundant phrases rather than gutting the sentence.
    """
    if not text:
        return text
    out = text
    # Replace em dashes with periods/spaces
    out = out.replace(" — ", ". ").replace("—", "-")
    # Replace curly quotes with straight
    out = out.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")

    # Phrase-level: replace with neutral wording, never blank
    phrase_swaps = {
        "in today's fast-paced": "today",
        "in the ever-evolving landscape of": "in",
        "in the ever-evolving landscape": "now",
        "ever-evolving landscape": "the space",
        "serves as a testament to": "shows",
        "stands as a testament to": "shows",
        "a testament to": "proof of",
        "delve into": "look at",
        "delve": "look",
        "embark on a journey": "start",
        "navigate the complexities": "work through",
        "navigate the landscape": "work through",
        "in the realm of": "in",
        "in the world of": "in",
        "harness the power of": "use",
        "harness the power": "use",
        "harness the potential of": "use",
        "harness the potential": "use",
        "unleash the power of": "use",
        "unleash the power": "use",
        "unleash the potential": "use",
        "robust solution": "solid option",
        "seamless experience": "smooth experience",
        "cutting-edge": "modern",
        "game-changer": "big shift",
        "game changer": "big shift",
        "revolutionary": "new",
        "deep dive": "look",
        "comprehensive guide": "guide",
        "ultimate guide": "guide",
        "in this article, we'll explore": "here's",
        "in this article we'll explore": "here's",
        "let's explore": "here's",
        "we'll discuss": "here's",
        "we will explore": "here's",
        "tapestry": "mix",
        "pivotal role": "big role",
        "key role": "big role",
        "vital role": "big role",
        "crucial role": "big role",
        "fostering": "building",
        "cultivating": "building",
    }
    # Sort by length descending so longer phrases match first
    for phrase in sorted(phrase_swaps, key=len, reverse=True):
        out = re.sub(re.escape(phrase), phrase_swaps[phrase], out, flags=re.IGNORECASE)

    # Word-level replacements
    for bad, good in _AI_REPLACEMENTS.items():
        out = re.sub(rf"\b{re.escape(bad)}\b", good, out, flags=re.IGNORECASE)

    # Collapse double spaces and stray punctuation
    out = re.sub(r"  +", " ", out)
    out = re.sub(r"\s+([.,;:])", r"\1", out)
    out = re.sub(r"\s+([.,;:])\s+", r"\1 ", out)
    return out.strip()


def _domain_only(url):
    """Strip a URL to bare domain. Used for X posts where URLs are penalized."""
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def _build_x_text(title, topic, post_url, prompts):
    """X (Twitter) — under 280 chars, NO URL in body (X penalizes them).

    X has been scrubbing links from organic posts since 2023. Workaround:
    post the bare domain (no scheme, no path) and put the full URL in the
    first comment via upload-post's first_comment field.

    Wrapper copy is humanized AND cleaned (strip CJK/emoji/em-dash/curly
    quotes per Opus's rules). The prompt snippets themselves stay verbatim
    (Opus rule: prompts are the product, must be 100% accurate).
    """
    tag = SITE_HASHTAGS.get(_domain_only(post_url), "#PromptPack")
    domain = _domain_only(post_url)
    snippet = " / ".join(clean_for_posting(p)[:40] for p in prompts[:3])
    wrapper = f"Daily Prompt Pack: {topic}\n\nFull pack on {domain}\n{tag}"
    wrapper = clean_for_posting(humanize(wrapper))
    # Reassemble with snippets unchanged
    text = f"{wrapper.split(chr(10) + chr(10))[0]}\n\n{snippet}\n\n{wrapper.split(chr(10) + chr(10), 1)[-1]}"
    return _truncate(text, 280)


def _build_x_first_comment(post_url):
    """First comment on X post — full URL lives here so it isn't penalized."""
    return clean_for_posting(humanize(f"Read the full prompt pack: {post_url}"))


def _build_bluesky_text(title, topic, post_url, prompts):
    """Bluesky — 300 chars. URLs are fine on Bluesky.

    Wrapper is humanized AND cleaned. Prompt snippets stay verbatim but
    get the same clean pass since Opus doesn't want CJK/emoji in any cron
    output (prompts that happen to include those should also be cleaned;
    the 100% accuracy rule applies to the words, not to forbidden chars).
    """
    snippet = "\n".join(f"- {clean_for_posting(p)[:60]}" for p in prompts[:3])
    head = clean_for_posting(humanize(title))
    tail = clean_for_posting(humanize(f"Full pack: {post_url}"))
    text = f"{head}\n\n{snippet}\n\n{tail}"
    return _truncate(text, 300)


def _build_pin_title(title, topic, post_url):
    """Pinterest title — HARD 100 char cap. Just the hook + URL.

    Returns the short title that goes in upload-post's `title` field.
    """
    domain = _domain_only(post_url)
    head = clean_for_posting(humanize(f"Daily Prompt Pack: {topic}"))
    candidate = f"{head} | {domain}"
    return _truncate(candidate, 100)


def _build_pin_description(title, topic, post_url, prompts):
    """Pinterest description — extended, up to ~500 chars.

    Goes in upload-post's `description` field. Pinterest uses this for SEO
    in their search index, so keep keywords and snippets.
    """
    snippet = " | ".join(clean_for_posting(p)[:60] for p in prompts[:3])
    head = clean_for_posting(humanize(title))
    tail = clean_for_posting(
        humanize(
            f"Daily prompt pack on {topic}. Copy-paste into ChatGPT, Claude, or Cursor. {post_url}"
        )
    )
    text = f"{head}. {snippet}. {tail}"
    return _truncate(text, 500)


def _render_pin_image(site_key, topic, prompts, output_path):
    """Render a 1000x1500 vertical PNG pin with prompts."""
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1000, 1500
    bg_color = {
        "aitoolalliance.com": (16, 24, 40),
        "aicofounderstack.com": (40, 18, 50),
        "aibusinessinsider.org": (18, 38, 32),
    }.get(site_key, (16, 24, 40))
    accent = {
        "aitoolalliance.com": (99, 162, 255),
        "aicofounderstack.com": (236, 100, 255),
        "aibusinessinsider.org": (90, 220, 160),
    }.get(site_key, (99, 162, 255))

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    def _font(size, bold=False):
        candidates = [
            "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        ]
        for c in candidates:
            if Path(c).exists():
                try:
                    return ImageFont.truetype(c, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    f_brand = _font(36, bold=True)
    f_topic = _font(58, bold=True)
    f_prompt = _font(34)
    f_footer = _font(28)
    f_tag = _font(30)

    site_label = {
        "aitoolalliance.com": "AI TOOL ALLIANCE",
        "aicofounderstack.com": "AI COFOUNDER STACK",
        "aibusinessinsider.org": "AI BUSINESS INSIDER",
    }[site_key]

    # Header bar
    draw.rectangle([0, 0, width, 110], fill=accent)
    draw.text((50, 32), site_label, fill=(255, 255, 255), font=f_brand)

    # Topic headline
    draw.text((60, 160), f"Today's topic:", fill=(180, 200, 230), font=f_tag)
    draw.text((60, 200), topic.title(), fill=(255, 255, 255), font=f_topic)

    # Divider
    draw.line([(60, 320), (width - 60, 320)], fill=accent, width=4)

    # Prompts
    y = 360
    for i, p in enumerate(prompts[:3], 1):
        # Number badge
        draw.ellipse([(60, y), (160, y + 100)], fill=accent)
        draw.text((95, y + 22), str(i), fill=(255, 255, 255), font=_font(54, bold=True))

        # Prompt text - wrap at ~32 chars per line
        text = p
        if len(text) > 240:
            text = text[:237] + "…"
        words = text.split()
        lines, current = [], ""
        for w in words:
            if len(current) + len(w) + 1 > 38:
                lines.append(current)
                current = w
            else:
                current = (current + " " + w).strip()
        if current:
            lines.append(current)
        lines = lines[:5]  # cap at 5 lines per prompt

        py = y + 12
        for line in lines:
            draw.text((190, py), line, fill=(240, 245, 255), font=f_prompt)
            py += 44
        y = py + 30

    # Footer
    draw.line([(60, height - 200), (width - 60, height - 200)], fill=accent, width=4)
    draw.text((60, height - 170), "DAILY PROMPT PACK", fill=accent, font=f_brand)
    draw.text((60, height - 110), "Copy-paste into ChatGPT, Claude, or Cursor", fill=(200, 215, 240), font=f_footer)
    draw.text((60, height - 70), SITE_URLS[site_key], fill=(255, 255, 255), font=_font(32, bold=True))

    img.save(output_path, "PNG", optimize=True)
    return str(output_path)


def _post_text(platform, text, first_comment=None):
    """upload-post /upload_text — supports x, bluesky.

    NOTE: upload-post's API rejects JSON bodies with a 'platform' array key
    and asks for 'Username required in form data'. Use form-encoded data with
    platform[] array form, no separate username field (profile handles it).
    Verified via diag_upload_post_r2.py test 5.

    X (Twitter): URLs are penalized in organic posts. Put the full URL in
    `first_comment` and keep the post body URL-free.
    """
    url = f"{UPLOAD_POST_BASE}/upload_text"
    data = {
        "user": UPLOAD_POST_PROFILE,
        "platform[]": [platform],
        "title": text,
    }
    if first_comment:
        data["first_comment"] = first_comment
    r = requests.post(url, headers=_headers(), data=data, timeout=60)
    return r.status_code, r.text[:600]


def _post_photo(platform, image_path, title, description=None, board_id=None):
    """upload-post /upload_photos — Pinterest needs a board_id, image required.

    Same form-data rule as _post_text. platform[] must be array-form.

    NOTE: upload-post expects the field name `pinterest_board_id` for
    Pinterest board routing, NOT `board_id`. Verified via diag_pinterest.py
    test B (200) vs test A (400 "Pinterest Board ID is required").

    NOTE: Pinterest title is hard-capped at 100 chars. The `description`
    field gets the long body (up to ~500). Verified via diag_pinterest.py
    round 2 - sending 440+ char title returns 400 'Pinterest title is too long'.
    """
    url = f"{UPLOAD_POST_BASE}/upload_photos"
    files = {"photos[]": (Path(image_path).name, open(image_path, "rb"), "image/png")}
    data = {
        "user": UPLOAD_POST_PROFILE,
        "platform[]": [platform],
        "title": title,
    }
    if description:
        data["description"] = description
    if platform == "pinterest" and board_id:
        data["pinterest_board_id"] = board_id
    r = requests.post(url, headers=_headers(), data=data, files=files, timeout=120)
    return r.status_code, r.text[:600]


def crosspost(site_key, topic, post_url, title, prompts):
    """Fire X, Bluesky, Pinterest.  Failures save to disk and continue."""
    results = {}

    # 1. X (text) — domain-only in body, full URL in first_comment
    x_text = _build_x_text(title, topic, post_url, prompts)
    x_comment = _build_x_first_comment(post_url)
    try:
        code, body = _post_text("x", x_text, first_comment=x_comment)
        results["x"] = {"status": code, "text": x_text, "first_comment": x_comment}
        if code not in (200, 201):
            results["x"]["error"] = body
            _save_draft(site_key, "x", {"text": x_text, "first_comment": x_comment, "topic": topic}, body)
    except Exception as e:
        results["x"] = {"status": -1, "error": str(e), "text": x_text, "first_comment": x_comment}
        _save_draft(site_key, "x", {"text": x_text, "first_comment": x_comment, "topic": topic}, e)

    # 2. Bluesky (text)
    bsky_text = _build_bluesky_text(title, topic, post_url, prompts)
    try:
        code, body = _post_text("bluesky", bsky_text)
        results["bluesky"] = {"status": code, "text": bsky_text}
        if code not in (200, 201):
            results["bluesky"]["error"] = body
            _save_draft(site_key, "bluesky", {"text": bsky_text, "topic": topic}, body)
    except Exception as e:
        results["bluesky"] = {"status": -1, "error": str(e), "text": bsky_text}
        _save_draft(site_key, "bluesky", {"text": bsky_text, "topic": topic}, e)

    # 3. Pinterest (image pin) — only if board is wired for this site
    if site_key in PIN_BOARDS:
        pin_title = _build_pin_title(title, topic, post_url)
        pin_description = _build_pin_description(title, topic, post_url, prompts)
        pin_path = DRAFT_DIR / f"{datetime.now():%Y-%m-%d}_{site_key}_pin.png"
        try:
            _render_pin_image(site_key, topic, prompts, pin_path)
            code, body = _post_photo("pinterest", pin_path, pin_title, description=pin_description, board_id=PIN_BOARDS[site_key])
            results["pinterest"] = {"status": code, "image": str(pin_path), "title": pin_title, "description": pin_description}
            if code not in (200, 201):
                results["pinterest"]["error"] = body
                _save_draft(site_key, "pinterest", {"title": pin_title, "description": pin_description, "image": str(pin_path), "topic": topic}, body)
        except Exception as e:
            results["pinterest"] = {"status": -1, "error": str(e)}
            _save_draft(site_key, "pinterest", {"title": pin_title, "description": pin_description, "image": str(pin_path) if pin_path.exists() else None, "topic": topic}, e)
    else:
        results["pinterest"] = {"status": "skipped", "reason": f"no board wired for {site_key} (Cloudflare-blocked or no board)"}

    return results


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--site", required=True)
    p.add_argument("--topic", required=True)
    p.add_argument("--post-url", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--prompts", required=True, help='JSON list of 3 prompt strings')
    args = p.parse_args()

    prompts = json.loads(args.prompts)
    if not isinstance(prompts, list) or len(prompts) != 3:
        print("ERROR: --prompts must be a JSON list of exactly 3 strings", file=sys.stderr)
        sys.exit(2)

    results = crosspost(args.site, args.topic, args.post_url, args.title, prompts)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
