# Kybernauts — Documentation

> Current as of 2026-05-08

## Overview

Kybernauts is an EVE Online corp (Clade) focused on Pochven territory, small/mid-sized fleet PvP, and Black Ops. The Discord agent handles recruitment, propaganda posting, and forum monitoring.

## Accounts & Links

| Service | Details |
|---------|---------|
| Website | join.kybernauts.today |
| Twitter/X | @KybernautClade via Upload-Post API, profile "Kybernauts" |
| EVE Forum Thread | forums.eveonline.com/t/507971 |
| Discord | #kybernauts (1479156871641436265) |
| EVE Forum Login | opusmagnum (SSO — needs re-auth for auto-bumping) |

## Upload-Post API (Twitter/X)

Same as EveOnion — use **form-data**, profile "Kybernauts":
```bash
curl -X POST "https://api.upload-post.com/api/upload_text" \
  -H "Authorization: Apikey <KEY>" \
  -F "user=Kybernauts" \
  -F "platform[]=x" \
  -F "title=<tweet text>"

# With poster image:
curl -X POST "https://api.upload-post.com/api/upload_photos" \
  -H "Authorization: Apikey <KEY>" \
  -F "user=Kybernauts" \
  -F "platform[]=x" \
  -F "photos[]=@poster.png" \
  -F "title=<tweet text>"
```

API key in `credentials/uploadpost.env`.

## EVE Forum (Discourse API)

Read-only access via JSON endpoint (no auth needed):
```
https://forums.eveonline.com/t/507971.json
```
Returns: title, views, reply_count, last_posted_at, posts with content.

**Posting requires EVE SSO auth** — the old Playwright scripts have expired sessions. For now, the ForumBump cron just monitors and reminds Opus to bump manually.

## Taglines

- POCHVEN OR BUST
- UNDOCK OR DIE
- TRIANGLE DEFENDERS
- HUNT OR BE HUNTED
- FORWARD TO POCHVEN

## Visual Identity

- **Colors**: Dark purple (#1a0a2e), Bio-luminescent teal (#00d4aa), Void black (#0d0208)
- **Symbols**: Triglavian triple-triangle
- **Style**: Dark, geometric, ominous

## Propaganda Posters

Available in `media/kybernauts/`:
| File | Description |
|------|-------------|
| `propaganda_20260425_183647.png` | "Pochven Awaits" — Triglavian triangles, best for recruitment |
| `propaganda-2026-05-05.png` | "Singularity is a Lie. Clade is Truth." — ideological |
| `kybernauts_poster.png` | "Faith and Fury" — minimalist |
| `kybernauts-poster-v1.webp` | AI-generated (has errors, avoid for public posts) |
| `nova-kybernauts-flux.webp` | Nova+Kybernauts mascot (no CTA, not standalone) |

## Cron Jobs

| Job | Schedule | Purpose |
|-----|----------|---------|
| Kybernauts-Propaganda | Every 2 days 6pm ET | Recruitment tweet + poster via Upload-Post |
| Kybernauts-ForumBump | Sunday 6pm ET | Check thread status, post reminder |

Both use `ollama/deepseek-v4-flash:cloud`, deliver to `#kybernauts`.

## Key Files

- `memory/subminds/kybernauts-knowledge.md` — Lore, taglines, visual identity
- `scripts/kybernauts/` — Bump scripts, poster generator, health check
- `docs/kybernauts-monroe-doctrine.md` — Lore document
- `docs/kybernauts-recruitment.md` — Recruitment copy
- `docs/kybernauts-sdc-formation.md` — SDC formation doc
- `docs/kybernauts-skill-plan.md` — Skill plan

## EVE Forum Bump Scripts (Legacy)

Four Playwright scripts exist in `scripts/kybernauts/`:
- `bump_kybernauts.js` — Basic bump
- `bump_kybernauts_v2.js` — Improved bump
- `bump_kybernauts_interactive.js` — Interactive mode
- `bump_kybernauts_stealth.js` — Stealth mode

All require fresh EVE SSO auth. Currently non-functional until Opus re-auths the browser session.