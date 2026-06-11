# Nova Cron Master Scheduler

> Last updated: 2026-06-04
> Timezone: America/New_York

## Daily Schedule Visual

```
02:00 | ████ ContentNova-aitoolalliance          (kimi-k2.6, 300s, heavy)
03:00 | ████ ContentNova-aibusinessinsider        (kimi-k2.6, 300s, heavy)
04:00 | ████ ContentNova-aicofounderstack         (kimi-k2.6, 600s, heavy)
05:00 | ──── (quiet)
06:00 | ████ Weekly-SkillUpdate (Mon only)          (deepseek-v4-flash, fast)
06:45 | ██   spam-pattern-discovery                (deepseek-v4-flash, 300s, light)
07:00 | ██   daily-brief-7am                      (deepseek-v4-flash, 180s, light)
07:15 | ██   spam-sweep-every-4h                   (deepseek-v4-flash, 480s, medium)
07:30 | ██   Iris-all-accounts-digest            (deepseek-v4-flash, 180s, medium)
08:00 | ██   EveOnion-NewsScan                   (deepseek-v4-flash, 300s, medium)
09:00 | ██   Nova-Ops-Assessment                   (deepseek-v4-flash, 180s, light)
09:30 | ████ EveOnion-Article (Tue/Fri only)       (kimi-k2.6, 300s, heavy)
10:00 | ██   TradeBot-Analytics (Mon only)          (kimi-k2.6, 180s, light)
10:00 | ██   EveOnion-PersonaScan (every 3 days)    (deepseek-v4-flash, 300s, medium)
14:00 | ████ TradeBot-WeeklyReview (Sat only)       (deepseek-v4-flash, 600s, medium)
14:30 | ████ EveOnion-DailyTweet                   (deepseek-v4-flash, 180s, light)
15:00 | ██   AntiYagas-Phase1-Daily                 (kimi-k2.6, 300s, medium)
18:00 | ██   AntiYagas-EveningBrief                 (kimi-k2.6, 300s, medium)
18:00 | ██   Weekly-SkillDiscovery (Fri only)       (deepseek-v4-flash, 180s, light)
18:15 | ██   Kybernauts-Propaganda (every 2 days)    (kimi-k2.6, 300s, medium)
18:30 | ████ Kybernauts-ForumBump (Sun only)          (kimi-k2.6, 600s, heavy)
20:00 | ████ NightSchool-8pm                       (deepseek-v4-flash, 600s, heavy)
20:15 | ██   NightSchool-NAS-Sync                  (deepseek-v4-flash, 60s, light)
22:00 | ██   Weekly-MemoryHygiene (Sun only)          (deepseek-v4-flash, 180s, light)

--- Continuous ---
- TradeBot-Consolidated — every 5 min (deepseek-v4-flash, 600s)
- TradeBot-PortfolioOverview — every 4h (deepseek-v4-flash, 180s)
```

## Load Analysis

| Time Block | Total Jobs | Heavy | Model Load |
|------------|-----------|-------|------------|
| 2-4am | 3 | 3 (all content) | `kimi-k2.6` ×3 |
| 7-8am | 3 | 0 | `deepseek-v4-flash` ×3 |
| 9-10am | 2-3 | 1 (article) | `kimi-k2.6` + `deepseek-v4-flash` |
| 2-3pm | 2 | 1 (review) | `deepseek-v4-flash` + `kimi-k2.6` |
| 6pm | 3-4 | 1 (forum bump Sun) | `kimi-k2.6` ×2-3 + `deepseek-v4-flash` |
| 8pm | 1 | 1 (night school) | `deepseek-v4-flash` |

## Model Breakdown

| Model | # Crons | Heavy Jobs | Notes |
|-------|---------|-----------|-------|
| kimi-k2.6 | **7** | 4 (content ×3 + article) | Main creative engine. 2-4am block is peak load |
| deepseek-v4-flash | **15** | 2 (night school, forum bump) | Ops/scans. Distributed well |
| minimax-m2.7 | 0 | — | Retired, no active crons |

## Conflict History

- **June 4**: ContentNova-aicofounderstack + daily-spam-sweep both hit 300s timeout. Fixed: bumped to 600s/480s.
- **June 3**: EveOnion-PersonaScan previously ran minimax-m2.7 which was slow. Fixed: switched to deepseek-v4-flash.
- **May 28-31**: EveOnion-NewsScan had 4 consecutive timeouts. Fixed: switched from minimax-m2.7 to deepseek-v4-flash.

## Rules

1. **Never schedule 2 heavy `kimi-k2.6` jobs at the same time.**
2. **Keep 15min minimum gap between any 2 jobs in same time block.**
3. **Content empire (2-4am) is sacred — don't add there.**
4. **If adding a new job, check this doc first.**
5. **Prefer `deepseek-v4-flash` for new ops/scans. Reserve `kimi-k2.6` for writing.**

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
| 1471135533777424587 | #eveonion (alt) |

## Cron Registry (by Project)

### TradeBot (4 crons)
| Name | ID | Schedule | Model | Timeout |
|------|-----|----------|-------|---------|
| TradeBot-Consolidated | 78b66703 | every 5m | deepseek-v4-flash | 600s |
| TradeBot-PortfolioOverview | 0eb02ac4 | every 4h | deepseek-v4-flash | 180s |
| TradeBot-WeeklyReview | 2be91036 | Sat 2pm | deepseek-v4-flash | 600s |
| TradeBot-Analytics | c8153b73 | Mon 10am | kimi-k2.6 | 180s |

### Content Empire (3 crons)
| Name | ID | Schedule | Model | Timeout |
|------|-----|----------|-------|---------|
| ContentNova-aitoolalliance | 21260801 | 2am daily | kimi-k2.6 | 300s |
| ContentNova-aibusinessinsider | 38c57c58 | 3am daily | kimi-k2.6 | 300s |
| ContentNova-aicofounderstack | b44776e2 | 4am daily | kimi-k2.6 | 600s |

### EveOnion (5 crons)
| Name | ID | Schedule | Model | Timeout |
|------|-----|----------|-------|---------|
| EveOnion-NewsScan | d4bb7a00 | 8am daily | deepseek-v4-flash | 300s |
| EveOnion-Article | f4567195 | 9:30am Tue/Fri | kimi-k2.6 | 300s |
| EveOnion-DailyTweet | 005d8eba | 2:30pm daily | deepseek-v4-flash | 180s |
| EveOnion-PersonaScan-Reddit | 94609722 | 10am every 3 days | deepseek-v4-flash | 300s |

### Kybernauts (4 crons)
| Name | ID | Schedule | Model | Timeout |
|------|-----|----------|-------|---------|
| AntiYagas-Phase1-Daily | 7d40d90f | 3pm daily | kimi-k2.6 | 300s |
| AntiYagas-EveningBrief | 74381489 | 6pm daily | kimi-k2.6 | 300s |
| Kybernauts-Propaganda | d27750c9 | 6:15pm every 2 days | kimi-k2.6 | 300s |
| Kybernauts-ForumBump | ac348e21 | 6:30pm Sun | kimi-k2.6 | 600s |

### Nova Ops (8 crons)
| Name | ID | Schedule | Model | Timeout |
|------|-----|----------|-------|---------|
| daily-brief-7am | 0552b684 | 7am daily | deepseek-v4-flash | 180s |
| spam-sweep-every-4h | c96ff863 | every 4h | deepseek-v4-flash | 480s |
| spam-pattern-discovery | 20a09bb0 | 6:45am daily | deepseek-v4-flash | 300s |
| Iris-all-accounts-digest | a375126c | 7:30am daily | deepseek-v4-flash | 180s |
| Nova-Ops-Assessment | 488e0af0 | 9am daily | deepseek-v4-flash | 180s |
| NightSchool-8pm | 3071d872 | 8pm daily | deepseek-v4-flash | 600s |
| Weekly-MemoryHygiene | 10d4c1a3 | 10pm Sun | deepseek-v4-flash | 180s |
| Weekly-SkillUpdate | ac9ba7e1 | 6am Mon | deepseek-v4-flash | 180s |
| Weekly-SkillDiscovery | 0b0873dc | 6pm Fri | deepseek-v4-flash | 180s |

## Total: 24 crons
- `kimi-k2.6`: **7** crons (creative/writing heavy)
- `deepseek-v4-flash`: **16** crons (ops/scans/fast)
- Continuous jobs: 2 (every 5m, every 4h)

## Next Review
Check this doc before adding any new cron. Update after every change.

## Last Updated
2026-06-07 — added spam-pattern-discovery (6:45am daily), changed spam-sweep to every 4h.
