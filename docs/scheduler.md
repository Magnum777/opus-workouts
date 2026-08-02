# Nova Cron Master Scheduler

> Last updated: 2026-08-02
> Timezone: America/New_York

## Daily Schedule Visual

```
02:00 | ██   ContentNova-aitoolalliance          (minimax-m3, 480s)
03:00 | ██   ContentNova-aibusinessinsider        (minimax-m3, 600s)
03:38 | ░░   Finance-NAS-Backup                   (deepseek-v4-flash, 300s)
04:00 | ██   ContentNova-aicofounderstack          (minimax-m3, 600s)
06:30 | ░░   TD-Scanner                            (deepseek-v4-flash, 300s)
06:45 | ░░   Daily-MemorySweep + spam-pattern-discovery (deepseek-v4-flash ×2, 300s each)
07:00 | ██   daily-brief-7am                      (kimi-k2.6, 300s)
07:15 | ░░   gmail-cleanup-daily                   (deepseek-v4-flash, 120s)
07:30 | ██   Iris-all-accounts-digest             (deepseek-v4-flash, 900s)
07:30 | ░░   DS-Seed-Enforcer                      (deepseek-v4-flash, 300s)
08:15 | ██   EveOnion-NewsScan                     (minimax-m3, 480s)
09:00 | ░░   Nova-Ops-Assessment                   (deepseek-v4-flash, 180s)
09:30 | ██   EveOnion-Article (Tue/Fri only)       (kimi-k2.6, 480s)
10:00 | ██   EveOnion-RedditTweet                  (minimax-m3, 480s)
10:00 | ░░   EveOnion-PersonaScan (every 3 days)   (deepseek-v4-flash, 300s)
10:15 | ██   Amazon-Affiliate-Publish (Tue/Fri)      (minimax-m3, 480s)
11:00 | ░░   Amazon-Affiliate-Injector              (deepseek-v4-flash, 180s)
14:00 | ░░   Yagas-Intel-Collect                   (minimax-m3, 120s)
17:00 | ░░   Yagas-Propaganda-Post                 (minimax-m3, 180s)
18:15 | ██   Kybernauts-Propaganda (Sun only)       (minimax-m3, 180s)
20:00 | ████ NightSchool-8pm                       (deepseek-v4-flash, 3600s)
20:15 | ░░   NightSchool-NAS-Sync                  (deepseek-v4-flash, 60s)
22:00 | ░░   Weekly-MemoryHygiene (Sun only)        (deepseek-v4-flash, 300s)
23:00 | ██   Workspace-NAS-Backup (daily)            (deepseek-v4-flash, 1800s)
--- Continuous ---
- spam-sweep-every-4h - every 2h (deepseek-v4-flash, 600s)
--- Weekly Only ---
- Mon 06:00 | Weekly-SkillUpdate (deepseek-v4-flash, 120s)
- Mon 12:00 | Amazon-Tracker-Weekly (deepseek-v4-flash, 120s)
- Fri 18:00 | Weekly-SkillDiscovery (deepseek-v4-flash, 300s)
```

## Load Analysis

| Time Block | Total Jobs | Heavy | Model Load |
|------------|-----------|-------|------------|
| 2-4am | 3 | 0 | minimax-m3 x3 |
| 6-8am | 4 | 0 | deepseek-v4-flash x3 + kimi-k2.6 x1 |
| 8-10am | 4 | 1 (article) | kimi-k2.6 x1 + deepseek-v4-flash x1 + minimax-m3 x2 |
| 10am-noon | 3 | 0 | deepseek-v4-flash x3 |
| 2-5pm | 2 | 0 | minimax-m3 x2 |
| 6pm | 1 | 0 | minimax-m3 x1 |
| 8pm | 2 | 1 (night school) | deepseek-v4-flash x2 |
| 10-11pm | 1-2 | 0 | deepseek-v4-flash x1-2 |

## Model Breakdown (Enabled Only)

| Model | # Crons | Heavy Jobs | Notes |
|-------|---------|-----------|-------|
| kimi-k2.6 | **2** | 1 (EveOnion-Article) | Live creative + daily brief |
| deepseek-v4-flash | **16** | 1 (night school) | Ops/scans/continuous. Workhorse |
| minimax-m3 | **6** | 0 | EveOnion (2) + ContentNova (3) + Kybernauts/Yagas (3) |

## Total: 29 enabled + 6 disabled

### Disabled Crons (TradeBot — all stale, broken paths)

| Name | ID | Reason |
|------|-----|--------|
| TradeBot-GasCheck | 2e7adb67 | Disabled, exec path broken |
| TradeBot-Research | 40dacb34 | Disabled, exec path broken |
| TradeBot-DailyResearch | 457a5ae7 | Disabled, exec path broken |
| TradeBot-Analytics | c8153b73 | Disabled since Jul 7 |
| TradeBot-Executor | cc311165 | Disabled, delivery mode "none" |
| TradeBot-WeeklyReview | e618fccf | Disabled, never ran |

## Cron Registry

### Content Empire (3 crons)
| Name | ID | Schedule | Model | Timeout | Notes |
|------|-----|----------|-------|---------|-------|
| ContentNova-aitoolalliance | 21260801 | 2am daily | minimax-m3 | 480s | Quality gate v3 |
| ContentNova-aibusinessinsider | 38c57c58 | 3am daily | minimax-m3 | 600s | Quality gate v3 |
| ContentNova-aicofounderstack | b44776e2 | 4am daily | minimax-m3 | 600s | Quality gate v3 |

### Amazon Affiliate (3 crons)
| Name | ID | Schedule | Model | Timeout | Notes |
|------|-----|----------|-------|---------|-------|
| Amazon-Affiliate-Publish | 5aec02c7 | 10:15am Tue/Fri | minimax-m3 | 480s | Dynamic queue: generates topics, researches, writes, publishes |
| Amazon-Affiliate-Injector | 895f97ba | 11am daily | deepseek-v4-flash | 180s | Injects links + replenishes topic queue if low |
| Amazon-Tracker-Weekly | 53f0d707 | Mon 12pm | deepseek-v4-flash | 120s | Weekly dashboard check, post log enabled |

### EveOnion (4 crons)
| Name | ID | Schedule | Model | Timeout |
|------|-----|----------|-------|---------|
| EveOnion-NewsScan | d5dcb6b3 | 8:15am daily | minimax-m3 | 480s |
| EveOnion-Article | 412e27fd | 9:30am Tue/Fri | kimi-k2.6 | 480s |
| EveOnion-RedditTweet | 870c934f | 10am daily | minimax-m3 | 480s |
| EveOnion-PersonaScan | c2df9331 | 10am every 3 days | deepseek-v4-flash | 300s |

### Kybernauts (1 cron)
| Name | ID | Schedule | Model | Timeout |
|------|-----|----------|-------|---------|
| Kybernauts-Propaganda | 788bb86f | Sun 6:15pm | minimax-m3 | 180s |

### Yagas / Anti-Yagas (2 crons)
| Name | ID | Schedule | Model | Timeout | Notes |
|------|-----|----------|-------|---------|-------|
| Yagas-Intel-Collect | f146de70 | 2pm daily | minimax-m3 | 120s | Discord-only, post log enabled |
| Yagas-Propaganda-Post | f52721ee | 5pm daily | minimax-m3 | 180s | Discord-only, Phase 4, post log enabled |

### Nova Ops (15 crons)
| Name | ID | Schedule | Model | Timeout |
|------|-----|----------|-------|---------|
| spam-sweep-every-4h | c96ff863 | every 2h | deepseek-v4-flash | 600s |
| spam-pattern-discovery | 20a09bb0 | 6:45am daily | deepseek-v4-flash | 300s |
| TD-Scanner | 69b64d1d | 6:30am daily | deepseek-v4-flash | 300s |
| DS-Seed-Enforcer | 41b865e3 | 7:30am daily | deepseek-v4-flash | 300s |
| daily-brief-7am | 0552b684 | 7am daily | kimi-k2.6 | 300s |
| gmail-cleanup-daily | 8b079437 | 7:15am daily | deepseek-v4-flash | 120s |
| Iris-all-accounts-digest | a375126c | 7:30am daily | deepseek-v4-flash | 900s |
| Nova-Ops-Assessment | 488e0af0 | 9am daily | deepseek-v4-flash | 180s |
| Finance-NAS-Backup | 9b5aa167 | 3:38am daily | deepseek-v4-flash | 300s | **Fixed from minimax-m3** |
| NightSchool-8pm | 3071d872 | 8pm daily | deepseek-v4-flash | 3600s |
| NightSchool-NAS-Sync | 845e7dac | 8:15pm daily | deepseek-v4-flash | 300s |
| Workspace-NAS-Backup | cec8b2ad | 11pm daily | deepseek-v4-flash | 1800s |
| Daily-MemorySweep | 80014d37 | 6:45am daily | deepseek-v4-flash | 300s | Light sweep — yesterday's daily, new facts only |
| Daily-MemorySweep | 80014d37 | 6:45am daily | deepseek-v4-flash | 300s | Light sweep: yesterday's daily, new facts only |
| Weekly-MemoryHygiene | 10d4c1a3 | Sun 10pm | kimi-k2.6 | 900s | Deep clean: archive, dedup, full rewrite |
| Weekly-SkillUpdate | ac9ba7e1 | Mon 6am | deepseek-v4-flash | 120s |
| Weekly-SkillDiscovery | 0b0873dc | Fri 6pm | deepseek-v4-flash | 300s |

### TradeBot (6 crons — ALL DISABLED)
| Name | ID | Schedule | Status |
|------|-----|----------|--------|
| TradeBot-GasCheck | 2e7adb67 | 9am daily | ❌ Disabled |
| TradeBot-Research | 40dacb34 | every 2h | ❌ Disabled |
| TradeBot-DailyResearch | 457a5ae7 | 9:15am daily | ❌ Disabled |
| TradeBot-Analytics | c8153b73 | Mon 10am | ❌ Disabled |
| TradeBot-Executor | cc531165 | every 10m | ❌ Disabled |
| TradeBot-WeeklyReview | e618fccf | Sat 2pm | ❌ Disabled |

## Weekly Usage Budget (Ollama Pro)

**Model cost tiers:**
- `kimi-k2.6` — level 4 (extra heavy). 2 crons: daily-brief + EveOnion-Article
- `minimax-m3` — level 2 (medium). 6 crons: EveOnion (2) + ContentNova (3) + Kybernauts propaganda
- `deepseek-v4-flash` — level 3 (heavy). 12 crons, workhorse. Finance-NAS-Backup moved here from minimax-m3

## Ollama Model Quick Reference

| Model | Level | Use Case | Weekly Burn |
|-------|-------|----------|-------------|
| kimi-k3 | 4 (extra heavy) | Flagship chat/creative, vision | HIGH — primary chat model |
| kimi-k2.6 | 4 (extra heavy) | Live creative fallback, special crons | HIGH — minimize |
| deepseek-v4-pro | 4 (extra heavy) | Deep debugging only | HIGH — rare |
| minimax-m3 | 2 (medium) | Creative generation, agentic, social | Medium |
| deepseek-v4-flash | 3 (heavy) | Ops, scans, fast structured tasks | Medium — workhorse (12 crons) |
| glm-5.2 | 2 (medium) | Code tasks, 976K ctx | Low |
| kimi-k2.7-code | 2 (medium) | Dedicated coding, 262K ctx | Low — NEW |
| qwen3.5:397b | 2 (medium) | Reasoning + vision, 262K ctx | Low — NEW |
| nemotron-3-ultra | 2 (medium) | Agentic reasoning, 262K ctx | Low — NEW |
| mimo-v2.5-pro | 2 (medium) | Agentic coding, tool use | Low |

## Rules

1. **Never schedule 2 heavy `kimi-k2.6` jobs at the same time.**
2. **Keep 15min minimum gap between any 2 jobs in same time block.**
3. **Content empire (2-4am) is sacred — don't add there.**
4. **If adding a new job, check this doc first.**
5. **Prefer `deepseek-v4-flash` for new ops/scans. Reserve `kimi-k2.6` for live creative. Use `minimax-m3` for creative/agent tasks.**

## Adding a Cron

Checklist:
- [ ] What model? (prefer `deepseek-v4-flash` for ops, `minimax-m3` for creative, `kimi-k2.6` for live)
- [ ] What time? (check load chart, avoid conflicts)
- [ ] Timeout? (default 180s, heavy jobs 300-600s)
- [ ] Does it overlap with existing heavy jobs?
- [ ] Update this doc after adding

## Channel Map

| Channel ID | Name |
|------------|------|
| 1470836415523983630 | #nova |
| 1471281549646364805 | #wordpress |
| 1470957359248576699 | #tradebot |
| 1479156871641436265 | #kybernauts |
| 1484624659633934587 | #eveonion |
| 1524864332478021802 | #finance |

## Changelog

### 2026-08-02 — Amazon Affiliate Dynamic Queue
- **Added:** amazon_topic_generator.py v2 - topic generation with site-specific templates, 6 categories, dedup
- **Added:** amazon_publish_from_queue.py - queue-based publisher (replaces hardcoded list)
- **Queue:** 15 topics seeded across 3 sites, auto-replenishes when low
- **Upgraded:** Amazon-Affiliate-Publish cron - now generates topics, researches products via web_search, writes HTML articles, publishes from queue. Model deepseek-v4-flash -> minimax-m3, timeout 180s -> 480s
- **Upgraded:** Amazon-Affiliate-Injector cron - now also checks queue and replenishes if <5 topics
- **Old scripts:** amazon_content_pipeline.py still exists for manual use, queue system replaces it for automated publishing

### 2026-08-02 — Post Log, Missing Crons, Ops Health Check
- **Added:** Unified post log system (scripts/post_log.py + memory/post-log/posts.jsonl)
- **All content crons now log** to post_log.py after publishing/drafting (7 crons updated)
- **Recreated:** Yagas-Intel-Collect (2pm daily, minimax-m3, #kybernauts)
- **Recreated:** Yagas-Propaganda-Post (5pm daily, minimax-m3, #kybernauts, Discord-only)
- **Recreated:** Amazon-Affiliate-Publish (10:15am Tue/Fri, deepseek-v4-flash, #wordpress)
- **Recreated:** Amazon-Affiliate-Injector (11am daily, deepseek-v4-flash, #wordpress)
- **Recreated:** Amazon-Tracker-Weekly (Mon noon, deepseek-v4-flash, #finance)
- **Upgraded:** Nova-Ops-Assessment now includes content pipeline health check
  - Checks post log for missing cron entries (blocked/failed flags)
  - Runs dedup on titles
  - Flags content crons that didn't log in 48h
- **Added:** Content type to ontology schema
- **Added:** docs/infrastructure.md — full system architecture, cron registry, known issues, processes
- **Total enabled crons:** 29 (was 23, added 5 recreated + 1 Daily-MemorySweep)
- **Upgraded model:** deepseek-v4-flash → kimi-k2.6 (flash kept using Edit despite explicit instructions)
- **Increased timeout:** 600s → 900s (reading 7+ daily files + rewriting MEMORY.md)
- **Rewrote prompt:** 9 explicit numbered steps, CRITICAL: WRITE only, no Edit/apply_patch
- **Removed apply_patch from toolsAllow:** Prompt forbids it, model should comply
- **Added verification step:** Step 7 reads back first 5 lines to confirm save
- **Added memory_search steps:** Steps 1 and 5 use semantic search to catch facts daily files miss
- **Pulled nomic-embed-text:** Memory search was broken for weeks — model wasn't installed
- **Added Context Compaction Discipline to AGENTS.md:** 6 rules for context hygiene
- **Added Search Before Answering rule:** Always memory_search before answering about prior work

### 2026-07-31 — Model Refresh & Audit
- **Added models:** kimi-k3:cloud (1M ctx, vision, tools), glm-5.2:cloud (976K ctx, tools), kimi-k2.7-code:cloud (262K, vision+tools), qwen3.5:397b (262K, vision+tools), nemotron-3-ultra (262K, tools), minimax-m3 (updated to 512K ctx, video+vision+tools)
- **Upgraded:** Primary chat model kimi-k2.6 → kimi-k3 (1M ctx, vision)
- **Upgraded:** Code alias glm-5.1 → glm-5.2 (976K ctx)
- **Fixed:** Finance-NAS-Backup model minimax-m3 → deepseek-v4-flash (backup script doesn't need creative model)
- **Updated:** Model reference table, alias table, cron counts
- **Updated:** TOOLS.md model table, MEMORY.md model section

### 2026-07-26 — Cron Hardening Audit
- **Fixed:** TD-Scanner delivery: bare `discord:1470836415523983630` → `channel:1470836415523983630`. Trimmed toolsAllow from kitchen-sink to minimum. Added timeout + failure alerts.
- **Fixed:** DS Seed Enforcer delivery: missing `to` field → `channel:1470836415523983630`. Trimmed toolsAllow. Added timeout + failure alerts.
- **Fixed:** Daily Brief delivery: `not-delivered` every day → added `to: channel:1470836415523983630`. Removed dormant TradeBot check from prompt. Trimmed toolsAllow.
- **Fixed:** Memory Hygiene: `edit` tool failing on MEMORY.md → switched to `write` (full file overwrite). Added `apply_patch`. Increased timeout 300s→600s.
- **Fixed:** Workspace-NAS-Backup: gateway restart interrupt. Fixed prompt path. Added failure alerts.
- **Fixed:** Finance-NAS-Backup: trimmed toolsAllow from kitchen-sink to minimum. Added failure alerts.
- **Fixed:** EveOnion-PersonaScan: trimmed toolsAllow. Added failure alerts.
- **Fixed:** Nova-Ops-Assessment: added `read` to toolsAllow. Added `to` on delivery. Added failure alerts.
- **Fixed:** NightSchool-NAS-Sync: changed delivery from `none` to `announce` (was silently failing). Added model + timeout + toolsAllow. Added failure alerts.
- **Fixed:** Weekly-SkillUpdate: added `to` on delivery. Trimmed toolsAllow to `exec,read`. Added failure alerts.
- **Fixed:** Weekly-SkillDiscovery: added `to` on delivery. Added toolsAllow (`exec,read,write,web_search`). Added failure alerts.
- **Added:** Failure alerts (after 2 consecutive errors, 1h cooldown) to ALL 23 enabled crons
- **Added:** TD-Scanner and DS Seed Enforcer to registry
- **Documented:** NightSchool-NAS-Sync timeout 60s→300s

### 2026-07-25 — Model Audit & Fix
- **Fixed:** Agent models.json (tradebot, wordpress) stale baseUrl `192.168.68.50` → `127.0.0.1`
- **Fixed:** Duplicate crons removed (5 old agent versions: EveOnion-NewsScan, EveOnion-RedditTweet, EveOnion-Article, EveOnion-PersonaScan, Kybernauts-Propaganda)
- **Fixed:** Amazon-Affiliate-Publish model `deepseek-v4-flash` → `deepseek-v4-flash:cloud` (missing `:cloud` suffix)
- **Fixed:** Amazon-Tracker-Weekly model `deepseek-v4-flash` → `deepseek-v4-flash:cloud`
- **Updated:** Agent models: eveonion m2.7→m3, wordpress kimi→m3, creative alias m2.7→m3
- **Updated:** Yagas crons: deepseek-v4-flash → minimax-m3 (creative/agentic work)
- **Updated:** Kybernauts-Propaganda: deepseek-v4-flash → minimax-m3
- **Added:** mimo-v2.5-pro:cloud model to config (alias: agent)
- **Added:** Yagas section (2 crons, previously undocumented)
- **Added:** Amazon-Tracker-Weekly to registry
- **Upgraded:** minimax-m3 context window 128K → 1M (native), added multimodal + tool support

### 2026-07-24 — Full Audit Cleanup
- **Deleted:** AntiYagas-Phase1-Daily (91a1a64d), AntiYagas-EveningBrief (a3b459c0), Kybernauts-YouTubeLink (5d1291cb)
- **Removed from doc:** Social-Share-Auto (never existed as live cron), Amazon crons (3 — never existed)
- **Documented:** 6 disabled TradeBot crons (stale/broken) for cleanup decision
- **Rewrote:** Full scheduler doc to match live cron state (23 enabled + 6 disabled)