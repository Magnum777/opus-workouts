# MEMORY.md - Long-Term Memory

> Curated 2026-07-24. Operational details in `memory/YYYY-MM-DD.md`.
> Behavioral rules in `.learnings/`. Skill workflow in `AGENTS.md`.

## Identity
- **Name:** Nova
- **Pronouns:** she/her
- **Persona:** Raccoon-spirit AI, clever, mischievous hacker-familiar
- **Created by / works for:** James "Opus" (Layered Media LLC)

## The Human
- **Name:** James "Opus"
- **Timezone:** America/New_York
- **Entity:** Layered Media LLC
- **Peak hours:** Evenings (10pm–2am)
- **Style:** Direct, casual, ADHD when motivated

## Family
- **Wife:** Candace
- **Context:** Works at Warner Robins High School (qualifies for GM Educator $500 rebate)

## Hardware / Infra
- 9800X3D + 9070 XT, 32 GB RAM, Windows 10.0.26200
- Synology NAS: MND hostname (DNS auto-resolves, currently `192.168.68.70`) (MND / nova-home)

## Model Setup (2026-07-31)
- **Primary chat:** kimi-k3:cloud (1M ctx, vision, tools) — upgraded from kimi-k2.6
- **Code:** glm-5.2:cloud (976K ctx, tools) — upgraded from glm-5.1
- **Ops workhorse:** deepseek-v4-flash:cloud (1M ctx)
- **Creative/agent:** minimax-m3:cloud (512K ctx, video+vision)
- **Fallbacks:** glm-5.2 → kimi-k2.6 → claude-opus
- **New models available:** kimi-k3, glm-5.2, kimi-k2.7-code, qwen3.5:397b, nemotron-3-ultra
- **Vision note:** kimi-k3 has vision. kimi-k2.6 vision was broken (returned no text). Anthropic credits depleted, OpenAI auth expired.

## Active Crons (22 enabled, 6 disabled)

**Content Empire (3):** ContentNova x3 (2am/3am/4am daily, minimax-m3)
**EveOnion (4):** NewsScan (8:15am, minimax-m3), Article (Tue/Fri 9:30am, kimi-k2.6), RedditTweet (10am, minimax-m3), PersonaScan (every 3 days, deepseek-v4-flash)
**Kybernauts (1):** Propaganda (Sun 6:15pm, minimax-m3)
**Yagas (2):** Intel-Collect (2pm daily, minimax-m3), Propaganda-Post (5pm daily, minimax-m3)
**Amazon Affiliate (3):** Publish (Tue/Fri 10:15am), Injector (11am daily), Tracker-Weekly (Mon noon)
**Nova Ops (13):** spam-sweep (every 2h), spam-pattern-discovery (6:45am), daily-brief (7am, kimi-k2.6), gmail-cleanup (7:15am), Iris-digest (7:30am), ops-assessment (9am), finance-NAS-backup (3:38am, **deepseek-v4-flash** — fixed from minimax-m3), night-school (8pm), night-school-NAS-sync (8:15pm), workspace-NAS-backup (11pm), memory-hygiene (Sun 10pm), skill-update (Mon 6am), skill-discovery (Fri 6pm)

**Disabled (6 TradeBot — stale, broken paths):** GasCheck, Research, DailyResearch, Analytics, Executor, WeeklyReview

## Credit Card Portfolio & Benefits (as of 2026-07-26)

**Cards held:**
- Chase Freedom Unlimited (CFU): 1.5% everything, 3% dining/drugstores, $200 bonus after $500 spend
- Chase Sapphire Preferred (CSP): 2x gas/travel/dining, 1.25x portal redemption, transfer partners
- Chase Sapphire Reserve (CSR): 3x travel/dining, 1.5x portal, Priority Pass, $300 travel credit, $550 fee
- Amex Gold: 4x groceries (up to $25K/yr) + 4x restaurants, $250 fee, $120 dining credit + $120 Uber credit
- Prime Visa (if held): 5% Amazon + Whole Foods

**Current Freedom Flex Q3 2026 categories (not held):** Gas/EV charging, public transit, live entertainment, United Way

**Recommended but not held:**
- IHG One Rewards Premier: up to 185K bonus (150K after $3K/3mo + 35K after $6K/6mo), 26x IHG, 5x travel/dining/gas, 3x else, $99 fee, free night cert annually, Platinum status, 4th night free, $50 United TravelBank, Global Entry credit. Pass for now but worth revisiting.

**Optimization rules:**
- Groceries → Amex Gold (4x)
- Restaurants → Amex Gold (4x)
- Gas → CSP (2x)
- General spend → CFU (1.5%)
- IHG stays → no optimized card (currently using CSR/CSP at 1-2x)

**Trigger for new card recommendation:** Category spend $300+/month at 1-1.5% earn, or signup bonus >$200 net of fee.

## Projects (snapshot — verify before acting)

| Project | Status | Notes |
|---------|--------|-------|
| EveOnion | Active | 4 crons (m3 for news/tweets, kimi for articles). REAL PEOPLE off-limits: Fern Kitsuen, Lorumerth, James Cunningham. Fictional only. |
| KyberAPM | Active | Forked from EVE-APM-Preview, rebranded to Magnum777/kyber-apm. Harv testing. |
| Kybernauts | Active | Phase 3 (Direct Confrontation). Propaganda cron (m3). Yagas intel + propaganda crons (m3). |
| WordPress Empire | Active | aitoolalliance + aicofounderstack. aibusinessinsider still 403 Cloudflare. |
| ContentNova | Active | 3 crons, deepseek-v4-flash, quality gate v3. Unsplash API broken (401). |
| Night School | Active | 60+ topics processed, queue empty. NAS sync uses hostname MND. |
| TradeBot | Dormant | All 6 crons disabled, broken paths. Portfolio ~$103. Awaiting Opus decision. |
| Affiliate Pipeline | Dropped | Opus said forget it (May 27). |

## Key Rules
- "Mental notes" don't survive restart. WRITE IT DOWN.
- Quiet mode; short direct answers
- No em dashes in text for Opus
- NO EMOJI unless Opus explicitly asks for them. Hard rule.
- Sub-agent timeout ~120s hard limit
- Isolated crons can't read Windows env vars — use config files
- Recursive file scans through exec block the Node.js event loop
- Spam sweep must report EVERY trashed email to #nova

## Channels
- Discord: bot Nova, guild Layered Media LLC
- Wired: #nova, #tradebot, #wordpress, #eveonion, #kybernauts, #finance

## Recent Learnings (Auto-compacted)

### Week of 2026-07-20
- **Decision:** Anti-Yagas content is Discord-only, no social media. Kybernauts-Propaganda (official recruitment) stays on X+Bluesky. (2026-07-24)
- **Decision:** NAS IP replaced with hostname MND across 23 files. DS API file upload broken on DSM 4.1.2 — SMB write to `\\MND\video\watch` is the workaround. (2026-07-26)
- **Lesson:** Voice matching > dramatic AI writing. Opus rejects anything not in his actual voice. Monument announcement needs rebuild from verbatim Discord quotes. (2026-07-24)
- **CRITICAL:** TD-Scanner/cleanup must ONLY manage torrents added by the scanner (tracked in `td_state.json` `added_torrents`). Never touch user's own downloads. The `cmd_cleanup` function was deleting ALL zero-upload torrents including 233 of Opus's personal downloads. Fix: filter by `added_torrents` state before any deletion. (2026-07-28)
- **Lesson:** UniFi VLAN creation via API has `WanIpOverlapped` bug with static WAN + USG 3P. Two-step workaround (vlan-only → PATCH) works for tag creation but corporate VLANs still fail. Flat network is permanent decision. (2026-06-15)
- **Lesson:** UniFi SSO MFA codes expire in ~2-3 min. Script must be ready BEFORE requesting code. Session cookies must persist across requests. (2026-06-14)
- **Project update:** KyberAPM — Harv tested, 13 feedback items filed. Old repo references fully scrubbed, rebranded to Magnum777/kyber-apm. (2026-07-17/18)
- **Project update:** RateMyFC — 6 PHP bugs squashed (broken constants, missing hooks). Static mockup built. Staging site and real data testing still pending. (2026-07-21)
- **Project update:** EveOnion — NEVER target list confirmed: Fern Kitsuen, Lorumerth, James Cunningham. Fictional only. (2026-06-22/23)
- **Project update:** ContentNova — Quality gate v3 live on all 3 sites. Unsplash API broken (401). 3 crons on deepseek-v4-flash. (2026-07-14)
- **Tool/Skill:** 23 new skills installed and vetted (June 14). P0+P1 integrations complete (quality gate, YouTube research, browser retry, proactive-agent WAL protocol). P2 deferred. (2026-06-14)
- **Tool/Skill:** qwen3.5:27b is ~5-10x lighter than kimi-k2.6 — good for scheduled writing crons. Local models don't support tools in cron context. (2026-06-15, 2026-06-03)
- **Infra:** NAS audit freed ~1,173 GB. Workspace backup 5.97 GB / 82,823 files. All 21 crons updated to minimax-m3:cloud or deepseek-v4-flash:cloud. (2026-07-26)

## Last Updated
2026-07-26 — weekly memory hygiene: compacted learnings from 2026-06-01 through 2026-07-26.