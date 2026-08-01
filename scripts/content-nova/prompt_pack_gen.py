#!/usr/bin/env python3
"""
Prompt Pack Generator — daily 3 prompts per ContentNova site.
Topic-rotation state at scripts/content-nova/prompt-pack-state.json
Outputs JSON the cron turn consumes for WP publish + cross-post.

Usage:
  python prompt_pack_gen.py --site aitoolalliance.com
  python prompt_pack_gen.py --site aicofounderstack.com
"""

import json
from datetime import date
from pathlib import Path

THIS_DIR = Path(__file__).parent
STATE_FILE = THIS_DIR / "prompt-pack-state.json"

# Per-site topic pool.  Each site rotates with 30-day no-repeat guard.
TOPIC_POOLS = {
    "aitoolalliance.com": [
        "writing assistants", "image generation", "video generation",
        "code assistants", "voice and audio", "AI agents",
        "research and search", "automation workflows", "browser tools",
        "design tools", "data analysis", "presentation tools",
        "transcription tools", "AI for spreadsheets", "AI for email",
        "meeting assistants", "task management", "note-taking AI",
        "AI for marketing", "AI for SEO", "AI for sales",
        "AI for HR", "AI for legal", "AI for finance",
        "AI for designers", "AI for developers", "AI for writers",
        "AI for video editors", "AI for podcasters", "AI for students",
    ],
    "aicofounderstack.com": [
        "ideation and validation", "customer discovery", "MVP scoping",
        "go-to-market planning", "pricing strategy", "fundraising pitches",
        "investor updates", "hiring first 3", "founder productivity",
        "weekly founder review", "churn rescue", "expense discipline",
        "positioning and messaging", "landing page copy", "competitor teardown",
        "growth experiments", "content engine setup", "email outreach",
        "cold email sequences", "demo call prep", "objection handling",
        "board updates", "advisor management", "cofounder dynamics",
        "remote operations", "vendor evaluation", "tool stack audit",
        "burn rate planning", "revenue forecasting", "metric dashboards",
        "user onboarding",
    ],
    "aibusinessinsider.org": [
        "marketing operations", "sales operations", "customer support",
        "HR and people ops", "finance and accounting", "legal and compliance",
        "weekly status updates", "monthly business review", "vendor RFPs",
        "team productivity", "hiring pipeline", "performance reviews",
        "compensation planning", "strategic planning", "competitive intel",
        "market research", "brand voice and messaging", "content strategy",
        "lead scoring", "pipeline reviews", "renewal forecasting",
        "customer success", "implementation playbooks", "data dashboards",
        "BI reporting", "AI policy and governance", "AI risk assessment",
        "budget planning", "OKR setting", "quarterly planning",
        "executive communication",
    ],
}

SITE_META = {
    "aitoolalliance.com": {
        "name": "AI Tool Alliance",
        "tag": "aitoolalliance",
        "url": "https://aitoolalliance.com",
    },
    "aicofounderstack.com": {
        "name": "AI Cofounder Stack",
        "tag": "aicofounderstack",
        "url": "https://aicofounderstack.com",
    },
    "aibusinessinsider.org": {
        "name": "AI Business Insider",
        "tag": "aibusinessinsider",
        "url": "https://aibusinessinsider.org",
    },
}


def _load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"sites": {}}
    return {"sites": {}}


def _save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def pick_topic(site_key, no_repeat_days=30):
    """Pick a topic the site hasn't used in the last `no_repeat_days` days.

    Falls back to oldest-used or round-robin if all topics exhausted.
    """
    pool = TOPIC_POOLS.get(site_key)
    if not pool:
        return None

    state = _load_state()
    site_state = state["sites"].setdefault(site_key, {"history": [], "pointer": 0})
    today = date.today().isoformat()
    cutoff_days = no_repeat_days

    recent = []
    for entry in site_state["history"]:
        try:
            d = date.fromisoformat(entry["date"])
            if (date.today() - d).days < cutoff_days:
                recent.append(entry["topic"])
        except Exception:
            pass

    available = [t for t in pool if t not in recent]

    if not available:
        # all topics used in window — fall back to least-recent
        if site_state["history"]:
            oldest = sorted(site_state["history"], key=lambda e: e["date"])
            return oldest[0]["topic"]
        return pool[site_state["pointer"] % len(pool)]

    chosen = available[site_state["pointer"] % len(available)]
    site_state["pointer"] = (site_state["pointer"] + 1) % max(len(pool), 1)
    site_state["history"].append({"date": today, "topic": chosen})

    # keep history bounded
    if len(site_state["history"]) > 90:
        site_state["history"] = site_state["history"][-90:]

    _save_state(state)
    return chosen


def build_prompt_instructions(site_key, topic):
    """Instructions for the agent turn that fills in the actual prompts."""
    meta = SITE_META[site_key]
    return {
        "site_key": site_key,
        "site_name": meta["name"],
        "site_url": meta["url"],
        "topic": topic,
        "instructions": (
            f"You are writing the daily prompt pack for {meta['name']} ({meta['url']}).\n"
            f"Today's topic: **{topic}**.\n\n"
            "Write exactly 3 highly refined AI prompts on this topic. Each prompt must:\n"
            "- Be copy-pasteable into ChatGPT, Claude, or Cursor\n"
            "- Be tagged with which tool it targets in brackets, e.g. [Claude], [ChatGPT], [Cursor]\n"
            "- Force specificity — no 'help me with X', always 'given Y, do Z, output as W'\n"
            "- Be under 80 words including the tool tag\n"
            "- Deliver one tangible artifact (refactor, table, list, audit, plan)\n\n"
            "Output JSON with this exact shape:\n"
            "{\n"
            '  "title": "Daily Prompt Pack: <topic> — <one-line value prop>",\n'
            '  "excerpt": "<one-sentence hook, <160 chars>",\n'
            '  "intro_html": "<p>1-2 sentence intro with a hook and the topic line.</p>",\n'
            '  "prompts": [\n'
            '    {"tag": "[Claude]", "body": "<prompt 1>"},\n'
            '    {"tag": "[ChatGPT]", "body": "<prompt 2>"},\n'
            '    {"tag": "[Cursor]", "body": "<prompt 3>"}\n'
            "  ],\n"
            '  "footer_html": "<p>Full archive at <a href=\\"SITE_URL/tag/prompt-pack\\">SITE_URL/tag/prompt-pack</a>.</p>"\n'
            "}\n"
        ),
    }


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--site", required=True, choices=list(TOPIC_POOLS.keys()))
    p.add_argument("--show-state", action="store_true",
                   help="Print state file path and exit")
    args = p.parse_args()

    if args.show_state:
        print(str(STATE_FILE))
        return

    topic = pick_topic(args.site)
    out = build_prompt_instructions(args.site, topic)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
