# Nova Cron Master Scheduler

> Last updated: 2026-07-10
> Timezone: America/New_York

## Daily Schedule Visual

```
02:00 | ████ ContentNova-aitoolalliance          (qwen3.5:27b, 480s, medium)
03:00 | ████ ContentNova-aibusinessinsider        (qwen3.5:27b, 480s, medium)
03:38 | ██   Finance-NAS-Backup                  (deepseek-v4-flash, 300s, light)
04:00 | ████ ContentNova-aicofounderstack         (qwen3.5:27b, 600s, medium)
05:00 | ──── (quiet)
06:00 | ████ Weekly-SkillUpdate (Mon only)          (deepseek-v4-flash, 120s, light)
06:45 | ██   spam-pattern-discovery                (deepseek-v4-flash, 300s, light)
07:00 | ██   daily-brief-7am                      (kimi-k2.6, 300s, medium)
07:15 | ██   gmail-cleanup-daily                  (deepseek-v4-flash, 120s, light)
07:30 | ██   Iris-all-accounts-digest            (deepseek-v4-flash, 180s, medium)
08:15 | ██   EveOnion-NewsScan                   (minimax-m2.7, 480s, medium)
09:00 | ██   Nova-Ops-Assessment                   (deepseek-v4-flash, 180s, light)
09:00 | ██   TradeBot-GasCheck                    (deepseek-v4-flash, 300s, light)
09:15 | ██   TradeBot-DailyResearch              (deepseek-v4-flash, 300s, medium)
09:30 | ████ EveOnion-Article (Tue/Fri only)       (kimi-k2.6, 480s, heavy)
10:00 | ██   TradeBot-Analytics (Mon only)          (deepseek-v4-flash, 120s, light)
10:00 | ██   EveOnion-RedditTweet                 (minimax-m2.7, 480s, medium)
10:00 | ██   EveOnion-PersonaScan (every 3 days)    (deepseek-v4-flash, 300s, medium)
14:00 | ████ TradeBot-WeeklyReview (Sat only)       (deepseek-v4-flash, 300s, medium)
15:00 | ██   AntiYagas-Phase1-Daily                 (deepseek-v4-flash, 300s, medium)
18:00 | ██   AntiYagas-EveningBrief                 (deepseek-v4-flash, 120s, light)
18:00 | ██   Weekly-SkillDiscovery (Fri only)       (deepseek-v4-flash, 300s, light)
18:15 | ██   Kybernauts-Propaganda (Sun only)        (deepseek-v4-flash, 180s, medium)
18:15 | ██   Kybernauts-YouTubeLink (Wed only)       (deepseek-v4-flash, 120s, light)
20:00 | ████ NightSchool-8pm                       (deepseek-v4-flash, 600s, heavy)
20:15 | ██   NightSchool-NAS-Sync                  (deepseek-v4-flash, 60s, light)
22:00 | ██   Weekly-MemoryHygiene (Sun only)        (deepseek-v4-flash, 300s, light)
23:00 | ██   Workspace-NAS-Backup (daily)              (deepseek-v4-flash, 300s, medium)

--- Continuous ---
- TradeBot-Executor — every 10 min (deepseek-v4-flash, 300s)
- TradeBot-Research — every 2h (deepseek-v4-flash, 600s)
- spam-sweep-every-4h — every 2h (deepseek-v4-flash, 480s)
```

## Load Analysis

| Time Block | Total Jobs | Heavy | Model Load |
|------------|-----------|-------|------------|
| 2-4am | 3 | 3 (all content) | `qwen3.5:27b` ×3 |
| 7-8am | 4 | 0 | `deepseek-v4-flash` ×3 + `kimi-k2.6` ×1 |
| 9-10am | 4-5 | 1 (article) | `kimi-k2.6` + `deepseek-v4-flash` ×3 + `minimax-m2.7` |
| 2-3pm | 1 | 0 | `deepseek-v4-flash` |
| 6pm | 3-4 | 0 | `deepseek-v4-flash` ×3-4 |
| 8pm | 2 | 1 (night school) | `deepseek-v4-flash` ×2 |

## Model Breakdown (Enabled Only)

| Model | # Crons | Heavy Jobs | Notes |
|-------|---------|-----------|-------|
| kimi-k2.6 | **2** | 1 (EveOnion-Article) | Live creative + special cases only |
| deepseek-v4-flash | **20** | 1 (night school) | Ops/scans/continuous. Workhorse |
| qwen3.5:27b | **3** | 0 (content ×3) | Scheduled writing. Light GPU |
| minimax-m2.7 | **2** | 0 | EveOnion news + tweet generation |

## Total: 30 enabled + 3 disabled + 1 expired

### Disabled
- TradeBot-PortfolioOverview — "Opus audit in progress"
- TradeBot-Consolidated — replaced by split crons
- Kybernauts-ForumBump — disabled pending browser automation fix

### Expired
- P2-Integration-Reminder — one-shot at 2026-06-15, deleteAfterRun

## Cron Registry

### Content Empire (3 crons)
| Name | ID | Schedule | Model | Timeout | Notes |
|------|-----|----------|-------|---------|-------|
| ContentNova-aitoolalliance | 21260801 | 2am daily | qwen3.5:27b | 480s | Quality gate v3 |
| ContentNova-aibusinessinsider | 38c57c58 | 3am daily | qwen3.5:27b | 480s | Quality gate v3 |
| ContentNova-aicofounderstack | b44776e2 | 4am daily | qwen3.5:27b | 600s | Quality gate v3 |

### EveOnion (4 crons)
| Name | ID | Schedule | Model | Timeout |
|------|-----|----------|-------|---------|
| EveOnion-NewsScan | b9de81b3 | 8:15am daily | minimax-m2.7 | 480s |
| EveOnion-Article | 084309e2 | 9:30am Tue/Fri | kimi-k2.6 | 480s |
| EveOnion-RedditTweet | 02b8d422 | 10am daily | minimax-m2.7 | 480s |
| EveOnion-PersonaScan | 94609722 | 10am every 3 days | deepseek-v4-flash | 300s |

### TradeBot (5 crons + 2 continuous)
| Name | ID | Schedule | Model | Timeout | API Impact |
|------|-----|----------|-------|---------|------------|
| TradeBot-Research | ea26cf89 | every 2h | deepseek-v4-flash | 600s | Jupiter + Helius (heavy) |
| TradeBot-Executor | f5117dbc | every 10m | deepseek-v4-flash | 300s | Helius (light) |
| TradeBot-WeeklyReview | 2be91036 | Sat 2pm | deepseek-v4-flash | 300s | Helius (light) |
| TradeBot-Analytics | c8153b73 | Mon 10am | deepseek-v4-flash | 120s | Helius (light) |
| TradeBot-DailyResearch | 457a5ae7 | 9:15am daily | deepseek-v4-flash | 300s | Web Search (3 calls) |
| TradeBot-GasCheck | 73b00eab | 9am daily | deepseek-v4-flash | 300s | Helius (light) |
| TradeBot-PortfolioOverview | 0eb02ac4 | every 4h | **DISABLED** | — | Opus audit in progress |
| TradeBot-Consolidated | 78b66703 | every 10m | **DISABLED** | — | replaced by split |

### Kybernauts (3 crons)
| Name | ID | Schedule | Model | Timeout |
|------|-----|----------|-------|---------|
| AntiYagas-Phase1-Daily | 7d40d90f | 3pm daily | deepseek-v4-flash | 300s |
| AntiYagas-EveningBrief | 74381489 | 6pm daily | deepseek-v4-flash | 120s |
| Kybernauts-Propaganda | d27750c9 | Sun 6:15pm | deepseek-v4-flash | 180s |
| Kybernauts-YouTubeLink | 72b82016 | Wed 6:15pm | deepseek-v4-flash | 120s |
| Kybernauts-ForumBump | ac348e21 | Sun 6:30pm | **DISABLED** | 300s |

### Nova Ops (11 crons)
| Name | ID | Schedule | Model | Timeout |
|------|-----|----------|-------|---------|
| spam-sweep-every-4h | c96ff863 | every 2h | deepseek-v4-flash | 480s |
| spam-pattern-discovery | 20a09bb0 | 6:45am daily | deepseek-v4-flash | 300s |
| daily-brief-7am | 0552b684 | 7am daily | kimi-k2.6 | 300s |
| gmail-cleanup-daily | 8b079437 | 7:15am daily | deepseek-v4-flash | 120s |
| Iris-all-accounts-digest | a375126c | 7:30am daily | deepseek-v4-flash | 180s |
| Nova-Ops-Assessment | 488e0af0 | 9am daily | deepseek-v4-flash | 180s |
| NightSchool-8pm | 3071d872 | 8pm daily | deepseek-v4-flash | 600s |
| NightSchool-NAS-Sync | 845e7dac | 8:15pm daily | deepseek-v4-flash | 60s |
| Workspace-NAS-Backup | cec8b2ad | 11pm daily | deepseek-v4-flash | 300s |
| Weekly-MemoryHygiene | 10d4c1a3 | Sun 10pm | deepseek-v4-flash | 300s |
| Weekly-SkillUpdate | ac9ba7e1 | Mon 6am | deepseek-v4-flash | 120s |
| Weekly-SkillDiscovery | 0b0873dc | Fri 6pm | deepseek-v4-flash | 300s |
| Finance-NAS-Backup | 9b5aa167 | 3:38am daily | deepseek-v4-flash | 300s |

## Weekly Usage Budget (Ollama Pro)

**Problem:** kimi-k2.6 is level 4 (extra heavy). Scheduled crons burning GPU time from automated jobs.

**Fix (2026-07-10):**
- **ContentNova x3** switched from `kimi-k2.6` -> `qwen3.5:27b` (level ~2, ~5-10x lighter)
- **Remaining kimi-k2.6:** Only daily-brief-7am + EveOnion-Article (creative cases)
- **minimax-m2.7:** EveOnion news + tweet (light, not GPU-heavy)

**Expected savings:** ~60-70% reduction in scheduled GPU burn

**If still hitting cap:**
1. Switch EveOnion-Article to `qwen3.5:27b`
2. Switch daily-brief-7am to `deepseek-v4-flash`
3. Buy extra usage balance

## Ollama Model Quick Reference

| Model | Level | Use Case | Weekly Burn |
|-------|-------|----------|-------------|
| kimi-k2.6 | 4 (extra heavy) | Live creative sessions, special creative crons | HIGH — minimize |
| deepseek-v4-pro | 4 (extra heavy) | Deep debugging, complex reasoning only | HIGH — rare use |
| deepseek-v4-flash | 3 (heavy) | Ops, scans, fast structured tasks | Medium — workhorse |
| qwen3.5:27b | 2 (medium) | Scheduled writing, analytics, content | Low — preferred |
| minimax-m2.7 | 2 (medium) | Creative generation, social content | Low |
| mistral-small | 2 (medium) | Fast structured output, coding | Low |

## Rules

1. **Never schedule 2 heavy `kimi-k2.6` jobs at the same time.**
2. **Keep 15min minimum gap between any 2 jobs in same time block.**
3. **Content empire (2-4am) is sacred — don't add there.**
4. **If adding a new job, check this doc first.**
5. **Prefer `deepseek-v4-flash` for new ops/scans. Use `qwen3.5:27b` for scheduled writing. Reserve `kimi-k2.6` for live creative sessions only.**

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

## Next Review
Check this doc before adding any new cron. Update after every change.

## Last Updated
2026-07-10 — Synced with actual cron list. Removed duplicate EveOnion-NewsScan. Switched ContentNova x3 to qwen3.5:27b. Updated model counts and schedule to reality.
