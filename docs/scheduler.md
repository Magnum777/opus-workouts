# Nova Cron Master Scheduler

> Last updated: 2026-07-19
> Timezone: America/New_York

## Daily Schedule Visual

```
02:00 | ████ ContentNova-aitoolalliance          (deepseek-v4-flash, 480s, medium)
03:00 | ████ ContentNova-aibusinessinsider        (deepseek-v4-flash, 600s, medium)
03:38 | ██   Finance-NAS-Backup                  (deepseek-v4-flash, 300s, light)
04:00 | ████ ContentNova-aicofounderstack         (deepseek-v4-flash, 600s, medium)
06:00 | ██   Weekly-SkillUpdate (Mon only)        (deepseek-v4-flash, 120s, light)
06:45 | ██   spam-pattern-discovery                (deepseek-v4-flash, 300s, light)
07:00 | ██   daily-brief-7am                      (kimi-k2.6, 300s, medium)
07:15 | ██   gmail-cleanup-daily                  (deepseek-v4-flash, 120s, light)
07:30 | ██   Iris-all-accounts-digest             (deepseek-v4-flash, 900s, medium)
08:15 | ██   EveOnion-NewsScan                    (minimax-m2.7, 480s, medium)
09:00 | ██   Nova-Ops-Assessment                  (deepseek-v4-flash, 180s, light)
09:00 | ██   TradeBot-GasCheck                    (deepseek-v4-flash, 300s, light)
09:15 | ██   TradeBot-DailyResearch              (deepseek-v4-flash, 300s, medium)
09:30 | ████ EveOnion-Article (Tue/Fri only)       (kimi-k2.6, 480s, heavy)
10:00 | ██   TradeBot-Analytics (Mon only)          (deepseek-v4-flash, 600s, medium)
10:00 | ██   EveOnion-RedditTweet                 (minimax-m2.7, 480s, medium)
10:00 | ██   EveOnion-PersonaScan (every 3 days)    (deepseek-v4-flash, 300s, medium)
14:00 | ████ TradeBot-WeeklyReview (Sat only)       (deepseek-v4-flash, 300s, medium)
15:00 | ██   AntiYagas-Phase1-Daily                (deepseek-v4-flash, 300s, medium)
18:00 | ██   AntiYagas-EveningBrief                (deepseek-v4-flash, 120s, light)
18:00 | ██   Weekly-SkillDiscovery (Fri only)       (deepseek-v4-flash, 300s, light)
18:15 | ██   Kybernauts-Propaganda (Sun only)        (deepseek-v4-flash, 180s, medium)
18:15 | ██   Kybernauts-YouTubeLink (Wed only)       (deepseek-v4-flash, 120s, light)
20:00 | ████ NightSchool-8pm                       (deepseek-v4-flash, 3600s, heavy)
20:15 | ██   NightSchool-NAS-Sync                  (deepseek-v4-flash, 60s, light)
22:00 | ██   Weekly-MemoryHygiene (Sun only)        (deepseek-v4-flash, 300s, light)
23:00 | ██   Workspace-NAS-Backup (daily)              (deepseek-v4-flash, 1800s, medium)

--- Continuous ---
- TradeBot-Executor — every 10 min (deepseek-v4-flash, 300s)
- TradeBot-Research — every 2h (deepseek-v4-flash, 600s)
- spam-sweep-every-4h — every 2h (deepseek-v4-flash, 600s)
```

## Load Analysis

| Time Block | Total Jobs | Heavy | Model Load |
|------------|-----------|-------|------------|
| 2-4am | 3 | 0 | `deepseek-v4-flash` ×3 |
| 6-8am | 4 | 0 | `deepseek-v4-flash` ×3 + `kimi-k2.6` ×1 |
| 8-10am | 6 | 1 (article) | `kimi-k2.6` ×1 + `deepseek-v4-flash` ×3 + `minimax-m2.7` ×2 |
| 10am | 2-3 | 0 | `deepseek-v4-flash` + `minimax-m2.7` |
| 12pm | 2 | 0 | `deepseek-v4-flash` ×2 |
| 2-3pm | 1 | 0 | `deepseek-v4-flash` |
| 6pm | 2-3 | 0 | `deepseek-v4-flash` ×2-3 |
| 8pm | 2 | 1 (night school) | `deepseek-v4-flash` ×2 |

## Model Breakdown (Enabled Only)

| Model | # Crons | Heavy Jobs | Notes |
|-------|---------|-----------|-------|
| kimi-k2.6 | **2** | 1 (EveOnion-Article) | Live creative + daily brief only |
| deepseek-v4-flash | **24** | 1 (night school) | Ops/scans/continuous. Workhorse |
| minimax-m2.7 | **2** | 0 | EveOnion news + tweet |

## Total: 32 enabled + 0 disabled

### Removed (2026-07-19)
- P2-Integration-Reminder — expired one-shot, deleted
- TradeBot-PortfolioOverview — previously disabled, never recreated (Opus audit)
- TradeBot-Consolidated — previously disabled, replaced by split crons
- Kybernauts-ForumBump — previously disabled, browser automation issue

## Cron Registry

### Content Empire (3 crons)
| Name | ID | Schedule | Model | Timeout | Notes |
|------|-----|----------|-------|---------|-------|
| ContentNova-aitoolalliance | 21260801 | 2am daily | deepseek-v4-flash | 480s | Quality gate v3 |
| ContentNova-aibusinessinsider | 38c57c58 | 3am daily | deepseek-v4-flash | 600s | Quality gate v3 |
| ContentNova-aicofounderstack | b44776e2 | 4am daily | deepseek-v4-flash | 600s | Quality gate v3 |

### EveOnion (4 crons)
| Name | ID | Schedule | Model | Timeout |
|------|-----|----------|-------|---------|
| EveOnion-NewsScan | d5dcb6b3 | 8:15am daily | minimax-m2.7 | 480s |
| EveOnion-Article | 412e27fd | 9:30am Tue/Fri | kimi-k2.6 | 480s |
| EveOnion-RedditTweet | 870c934f | 10am daily | minimax-m2.7 | 480s |
| EveOnion-PersonaScan | c2df9331 | 10am every 3 days | deepseek-v4-flash | 300s |

### TradeBot (6 crons + 2 continuous)
| Name | ID | Schedule | Model | Timeout | API Impact |
|------|-----|----------|-------|---------|------------|
| TradeBot-DailyResearch | 457a5ae7 | 9:15am daily | deepseek-v4-flash | 300s | Web Search (3 calls) |
| TradeBot-Analytics | c8153b73 | Mon 10am | deepseek-v4-flash | 600s | Helius (light) |
| TradeBot-GasCheck | 2e7adb67 | 9am daily | deepseek-v4-flash | 300s | Helius (light) |
| TradeBot-WeeklyReview | e618fccf | Sat 2pm | deepseek-v4-flash | 300s | Helius (light) |
| TradeBot-Research | 40dacb34 | every 2h | deepseek-v4-flash | 600s | Jupiter + Helius (heavy) |
| TradeBot-Executor | cc531165 | every 10m | deepseek-v4-flash | 300s | Helius (light) |

### Kybernauts (4 crons)
| Name | ID | Schedule | Model | Timeout |
|------|-----|----------|-------|---------|
| AntiYagas-Phase1-Daily | 7d40d90f | 3pm daily | deepseek-v4-flash | 600s | Phase 2 content + Full YAGAS/INIT intel suite (every 4 days): zKill scan, auto-dossier builder, associates report |
| AntiYagas-EveningBrief | 74381489 | 6pm daily | deepseek-v4-flash | 120s |
| Kybernauts-Propaganda | 788bb86f | Sun 6:15pm | deepseek-v4-flash | 180s |
| Kybernauts-YouTubeLink | 5d1291cb | Wed 6:15pm | deepseek-v4-flash | 120s |

### Social Media (1 cron)
| Name | ID | Schedule | Model | Timeout | Notes |
|------|-----|----------|-------|---------|-------|
| Social-Share-Auto | *new* | Every 30 min | deepseek-v4-flash | 60s | Auto-shares new WordPress posts to X, Bluesky, Pinterest via upload-post |

### Amazon Affiliate (2 crons)
| Name | ID | Schedule | Model | Timeout | Notes |
|------|-----|----------|-------|---------|-------|
| Amazon-Tracker-Weekly | cf11c261 | Mon 12pm | deepseek-v4-flash | 120s | Reports sales progress to #wordpress |
| Amazon-Tracker-Urgent | 614da3c4 | Daily 12pm | deepseek-v4-flash | 120s | Silent unless <=30 days remaining |

### Nova Ops (11 crons)
| Name | ID | Schedule | Model | Timeout |
|------|-----|----------|-------|---------|
| spam-sweep-every-4h | c96ff863 | every 2h | deepseek-v4-flash | 600s |
| spam-pattern-discovery | 20a09bb0 | 6:45am daily | deepseek-v4-flash | 300s |
| daily-brief-7am | 0552b684 | 7am daily | kimi-k2.6 | 300s |
| gmail-cleanup-daily | 8b079437 | 7:15am daily | deepseek-v4-flash | 120s |
| Iris-all-accounts-digest | a375126c | 7:30am daily | deepseek-v4-flash | 900s |
| Nova-Ops-Assessment | 488e0af0 | 9am daily | deepseek-v4-flash | 180s |
| NightSchool-8pm | 3071d872 | 8pm daily | deepseek-v4-flash | 3600s |
| NightSchool-NAS-Sync | 845e7dac | 8:15pm daily | deepseek-v4-flash | 60s |
| Workspace-NAS-Backup | cec8b2ad | 11pm daily | deepseek-v4-flash | 1800s |
| Weekly-MemoryHygiene | 10d4c1a3 | Sun 10pm | deepseek-v4-flash | 300s |
| Weekly-SkillUpdate | ac9ba7e1 | Mon 6am | deepseek-v4-flash | 120s |
| Weekly-SkillDiscovery | 0b0873dc | Fri 6pm | deepseek-v4-flash | 300s |
| Finance-NAS-Backup | 9b5aa167 | 3:38am daily | deepseek-v4-flash | 300s |

## Weekly Usage Budget (Ollama Pro)

**Model cost tiers:**
- `kimi-k2.6` — level 4 (extra heavy). Only 2 scheduled crons: daily-brief + EveOnion-Article
- `deepseek-v4-flash` — level 3 (heavy). 24 crons, workhorse for all ops/scans
- `minimax-m2.7` — level 2 (medium). 2 crons for EveOnion creative

**ContentNova decision (2026-07-19):** Confirmed deepseek-v4-flash for all 3 content crons. Switched from planned qwen3.5:27b back to deepseek-v4-flash per Opus's preference.

## Ollama Model Quick Reference

| Model | Level | Use Case | Weekly Burn |
|-------|-------|----------|-------------|
| kimi-k2.6 | 4 (extra heavy) | Live creative sessions, special creative crons | HIGH — minimize |
| deepseek-v4-pro | 4 (extra heavy) | Deep debugging, complex reasoning only | HIGH — rare use |
| deepseek-v4-flash | 3 (heavy) | Ops, scans, fast structured tasks, content | Medium — workhorse |
| qwen3.5:27b | 2 (medium) | Available for switch if GPU budget tight | Low — on standby |
| minimax-m2.7 | 2 (medium) | Creative generation, social content | Low |

## Rules

1. **Never schedule 2 heavy `kimi-k2.6` jobs at the same time.**
2. **Keep 15min minimum gap between any 2 jobs in same time block.**
3. **Content empire (2-4am) is sacred — don't add there.**
4. **If adding a new job, check this doc first.**
5. **Prefer `deepseek-v4-flash` for new ops/scans. Reserve `kimi-k2.6` for live creative sessions only.**

## Adding a Cron

Checklist:
- [ ] What model? (prefer `deepseek-v4-flash` for non-writing)
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

## Fixes Applied (2026-07-19)

- **Deleted:** P2-Integration-Reminder (expired one-shot, was errored)
- **Fixed:** Nova-Ops-Assessment — replaced deprecated `wmic` with `Get-PSDrive`
- **Fixed:** daily-brief-7am — added gog calendar fallback (skip instead of crash)
- **Fixed:** Iris-all-accounts-digest — replaced `~` path with full absolute path
- **Fixed:** Finance-NAS-Backup — corrected NAS IP from 192.168.68.51 to 192.168.68.91
- **Recreated:** 12 missing crons lost after May 6 gateway reinstall (4 EveOnion, 4 Kybernauts, 4 TradeBot)
- **Confirmed:** ContentNova x3 stays on deepseek-v4-flash (not qwen3.5:27b)

## Next Review
Check this doc before adding any new cron. Update after every change.