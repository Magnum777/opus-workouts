# WordPress Sites - Complete Documentation

## Sites Overview

| Site | URL | Status | API User | API Password |
|------|-----|--------|----------|--------------|
| AI Business Insider | aibusinessinsider.org | ✅ Live | jessica_nova | Ro7IoPncBKoMmaWP |
| AI Tool Alliance | aitoolalliance.com | ✅ Ready | aitoolalliance_u6cbhe | aX9$E$4lyyj2AWgp |
| AI Cofounder Stack | aicofounderstack.com | ✅ Live | nova | DUau yrXK 1X8k O6eH YL5v qKID |
| EveOnion | eveonion.com | ✅ Ready | nova | EVEONION_APP_PASSWORD_REDACTED |

## API Access

All sites use WordPress REST API with **Application Passwords**:
- Base URL: `https://{site}/wp-json/wp/v2/`
- Auth: Basic Auth with username + application password

## Content-Nova Sub-Agent

**Role:** Editor-in-chief for WordPress content

**Responsibilities:**
- Content pipeline management (backlog, calendar)
- Research & draft orchestration
- Quality control & consistency
- Reporting via #wordpress channel

**Docs Location:** `docs/wordpress/BACKLOG-*.md`, `docs/wordpress/CALENDAR-*.md`

## Key Lessons from Past Issues

### What Caused Problems
- Too many cron jobs running simultaneously
- Context refreshing too fast
- Sub-agents not cleaning up properly
- Memory files growing unbounded

### Best Practices Going Forward
1. **Minimal crons** - Only essential ones, spaced out
2. **Sub-agent cleanup** - Always set `cleanup: delete`
3. **Session limits** - Max 4-6 active sessions
4. **Memory management** - Daily distillation only, delete old sessions
5. **One task at a time** - Don't pile on work

## Swarm Lanes (from COFOUNDER-OFFER)

1. **Content-Swarm** - WordPress publishing (up to 3 sites)
2. **Traffic-Swarm** - Social promotion
3. **Ops-Swarm** - Backups, health checks, Git commits
4. **Cofounder-Swarm** - Strategy & business development

## Tech Stack

- Theme: Kadence (free)
- SEO: Rank Math SEO (free)
- Hosting: SiteGround
- Caching: SiteGround Speed Optimizer

## Monetization

- Ads: Mediavine / AdSense (target 50K sessions)
- Affiliates: AI tool programs
- Digital products: Future phase
