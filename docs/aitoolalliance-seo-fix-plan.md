# SEO Fix Plan for aitoolalliance.com

## Problem
20 posts published, all missing:
- Meta descriptions
- Open Graph tags (og:title, og:description, og:image)
- Twitter card tags
- Schema markup (Article/FAQ structured data)

No SEO plugin is active. Rank Math may be installed but not running.

## What's Working
- WordPress REST API reads work (can list posts, get content)
- All posts have excerpts and featured images
- Sitemap and robots.txt are functional
- Canonical URLs present

## What's Blocked
- API returns 401 for plugins/themes/users endpoints
- Cannot install/activate Rank Math via API
- Cannot write meta descriptions via REST without SEO plugin

## Recommended Fix Path

### Option A: Manual Admin Login (Fastest)
1. Log into wp-admin at https://aitoolalliance.com/wp-admin
2. Check if Rank Math is installed (Plugins menu)
3. If installed: activate it, connect, bulk-edit meta descriptions
4. If not installed: install Rank Math SEO (free) from plugin directory

### Option B: Generate Meta Content for Bulk Paste
I can generate SEO-optimized meta descriptions + OG data for all 20 posts.
Opus copies into Rank Math after activating it.

### Option C: Fix API Permissions
Current app password user (`aitoolalliance_u6cbhe`) may be Editor, not Admin.
Create a new Admin-level app password for programmatic SEO updates.

## Quick Win: Auto-Generated Meta Descriptions

| Post | Suggested Meta Description |
|------|---------------------------|
| Best AI Video Creation Tools | Compare the top AI video generators for business in 2026. Save time and budget with tools that turn text into professional video. |
| AI Code Assistants | GitHub Copilot vs Claude Code vs Cursor: which AI coding assistant actually speeds up development? Side-by-side comparison for 2026. |
| Best AI Voice Synthesis | The 7 best AI voice synthesis tools for content creators. Natural-sounding TTS, real-time voice cloning, and enterprise audio workflows. |
| AI Meeting Assistants | Reclaim 4+ hours weekly with AI meeting assistants that transcribe, summarize, and generate action items. Top tools for 2026 compared. |
| 12 Free AI Tools | Free AI tools that actually help small businesses work smarter in 2026. No trials, no credit cards, just results. |

(16 more available on request)

## What Opus Needs to Do
1. Log into aitoolalliance wp-admin
2. Activate or install Rank Math SEO
3. Paste meta descriptions I generate
4. Verify with https://www.opengraph.xyz

## Estimated Impact
- Current: Zero social previews, no rich snippets in Google
- After fix: Proper search listings, social sharing with images, potential for rich results
- Time to impact: 1-2 weeks for Google re-crawl

---
Generated 2026-07-02
