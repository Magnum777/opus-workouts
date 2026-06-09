# Social Posting Automation — Playbook

**Created:** May 28, 2026 (Night School Session)
**Topic:** Self-hosted social media scheduling & cross-posting automation stack

## The Landscape (2026)

SaaS social schedulers (Buffer, Hootsuite, etc.) are expensive and lock your data in their databases. The open-source self-hosted landscape has matured dramatically. Three viable options plus a build-your-own pipeline approach using n8n + AI.

## Tier 1: Full-Package Self-Hosted Tools

### BrightBean Studio ⭐ (Best All-Rounder — NEW)
- **Stack:** Python/Django, Postgres
- **License:** Open source (full-featured, no paid tier)
- **Stars:** 1,700+
- **Platforms:** Facebook, Instagram, LinkedIn, TikTok, YouTube, Pinterest, Threads, Bluesky, Google Business Profile, Mastodon (10+)
- **Key Features:** Multi-workspace, RBAC, approval workflows, unified inbox (comments/DMs/reviews), media library, client portal, Kanban idea board, calendar scheduling, recurring slots
- **Deployment:** Heroku/Render/Railway one-click, Docker, local. Also offers a free hosted version
- **Why it wins:** Full feature parity with Sendible/SocialPilot at $0. First-party API integrations (no middleman). Bluesky + Threads support. Client approval portal built in.

### Postiz (Most Popular)
- **Stack:** Next.js, PostgreSQL, Redis, Temporal
- **License:** AGPL-3.0
- **Stars:** 31,000+
- **Platforms:** X/Twitter, LinkedIn, Instagram, Facebook, YouTube, TikTok, Reddit
- **Key Features:** AI content generation, team workspaces, analytics, calendar
- **Downsides:** Heavy infra (3 services), AGPL copyleft, no Bluesky/Mastodon, cloud pricing gets expensive ($29/mo for 400 posts)
- **Best for:** Teams with infra budget who want the most polished UI

### Mixpost (Lightest Footprint)
- **Stack:** Laravel/PHP, MySQL/PostgreSQL
- **License:** MIT
- **Stars:** 3,200+
- **Platforms:** X/Twitter, Facebook, Instagram, Mastodon, LinkedIn, Pinterest, TikTok, YouTube
- **Key Features:** Clean UI, media library, calendar
- **Downsides:** No API (browser-only), no Bluesky, PHP stack dependency
- **Best for:** PHP teams or solo creators wanting simple self-hosted scheduler

### Blurt (Developer-First)
- **Stack:** Go binary, no database (filesystem-based)
- **License:** MIT
- **Platforms:** Bluesky, Mastodon, LinkedIn, Medium, Dev.to, Substack
- **Key Features:** Posts = markdown files, CLI + API + MCP server + web UI, git-versionable
- **Downsides:** Developer-oriented, fewer platforms (no X/Instagram/Facebook), no analytics
- **Best for:** Devs who want to own content as files and automate from terminal

## Tier 2: Pipeline Approach (n8n + AI)

Instead of a monolithic scheduler, build a modular pipeline:

```
RSS Feed → n8n → AI (reformat/rewrite) → Scheduling API → Platforms
```

### Pre-built Pipeline Patterns (from GitHub)
- **"Automated Marketing Engine"** — Turn one blog post into 8 platform-specific pieces via n8n + Claude AI → LinkedIn, X/Twitter, Reddit, Email, Dev.to, Hashnode, Indie Hackers. 7-day drip schedule.
- **"Blog-to-Social AI n8n"** — Free workflow: RSS → OpenAI → Twitter + LinkedIn content. 5-min setup.
- **"Feed-Pulse"** — BEAR.Sunday + Claude API: Crawl → Match → Generate → Publish pipeline.

### The Recommended Stack for Layered Media
```
WordPress Blog → RSS trigger → n8n → 
  ├── AI reformat (per platform) → 
  │   ├── LinkedIn (long-form)
  │   ├── X/Twitter (thread)
  │   ├── Bluesky (casual)
  │   └── Reddit (discussion)
  └── Schedule via API → BrightBean Studio / Mixpost / Postiz
```

## Decision Framework

| If you... | Pick... |
|-----------|---------|
| Want full agency-grade features for free | **BrightBean Studio** |
| Have infra budget, want best UX | **Postiz** |
| Run PHP, want simplest setup | **Mixpost** |
| Are a developer, want file ownership | **Blurt** |
| Already run n8n, want full control | **Pipeline approach** |

## Implementation Plan for Layered Media

### Phase 1: Pick the scheduler (this week)
1. Deploy BrightBean Studio on Railway or Docker (lowest friction, highest feature density)
2. Connect Bluesky, LinkedIn, X/Twitter, Reddit
3. Set up 3 workspaces: Layered Media, Nova, Client Projects

### Phase 2: Build the pipeline (next week)
1. n8n RSS trigger on Layered Media blog
2. AI reformat step (OpenClaw or OpenAI) per platform
3. Write to BrightBean API for scheduling

### Phase 3: Scale (ongoing)
1. Add approval workflows for client accounts
2. Enable social inbox for engagement monitoring
3. Add recurring slot scheduling for consistent cadence

## Cost Comparison

| Option | Monthly Cost | Infra Load | Feature Level |
|--------|-------------|------------|---------------|
| Buffer/Hootsuite | $30-300/mo | Zero | Limited by plan |
| BrightBean (self-hosted) | $0 + hosting (~$5-15/mo) | Medium (Django + Postgres) | Full |
| Postiz (self-hosted) | $0 + hosting (~$10-20/mo) | High (3 services) | Full |
| Mixpost (self-hosted) | $0 + hosting (~$5-10/mo) | Low (PHP + MySQL) | Good |
| n8n pipeline | $0 + hosting (already have n8n) | Low (n8n + API calls) | Customizable |

## Key Takeaways

1. **BrightBean Studio is the 2026 winner** for full-featured self-hosted social management — just launched, already 1.7K stars, Bluesky/Threads support, client portal built in
2. **Blurt is the dark horse** for developer workflows — file-based ownership is a genuinely different paradigm
3. **n8n + AI pipeline** is the modular alternative if you don't want tool lock-in
4. **Self-hosting is cheaper than SaaS** at any scale beyond 3 social channels

## Resources
- [BrightBean Studio GitHub](https://github.com/brightbeanxyz/brightbean-studio)
- [Postiz GitHub](https://github.com/gitroomhq/postiz-app)
- [Mixpost GitHub](https://github.com/inovector/mixpost)
- [Blurt](https://blurt.sh)
- [Automated Marketing Engine (n8n)](https://github.com/davidsly4954/Automated-Marketing-Engine)
- [Blog-to-Social n8n Workflow](https://github.com/flowyantra/blog-to-social-ai-n8n)

## Status
**✅ Completed — May 28, 2026**
