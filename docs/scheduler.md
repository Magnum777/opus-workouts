# Nova Cron Master Scheduler

> Last updated: 2026-06-04
> Timezone: America/New_York

## Daily Schedule Visual

```
02:00 | ████ ContentNova-aitoolalliance          (qwen3.5:27b, 480s, medium)
03:00 | ████ ContentNova-aibusinessinsider        (qwen3.5:27b, 480s, medium)
04:00 | ████ ContentNova-aicofounderstack         (qwen3.5:27b, 600s, medium)
05:00 | ──── (quiet)
06:00 | ████ Weekly-SkillUpdate (Mon only)          (deepseek-v4-flash, fast)
06:45 | ██   spam-pattern-discovery                (deepseek-v4-flash, 300s, light)
07:00 | ██   daily-brief-7am                      (deepseek-v4-flash, 180s, light)
07:15 | ██   spam-sweep-every-4h                   (deepseek-v4-flash, 480s, medium)
07:30 | ██   Iris-all-accounts-digest            (deepseek-v4-flash, 180s, medium)
08:00 | ██   EveOnion-NewsScan                   (deepseek-v4-flash, 300s, medium)
09:00 | ██   Nova-Ops-Assessment                   (deepseek-v4-flash, 180s, light)
09:15 | ██   TradeBot-DailyResearch              (deepseek-v4-flash, 300s, medium)  [NEW - szzg007 research pipeline]
09:30 | ████ EveOnion-Article (Tue/Fri only)       (kimi-k2.6, 300s, heavy)
10:00 | ██   TradeBot-Analytics (Mon only)          (qwen3.5:27b, 180s, light)
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
- TradeBot-Research — every 2h (deepseek-v4-flash, 180s)
- TradeBot-Executor — every 10 min (deepseek-v4-flash, 300s)
- TradeBot-PortfolioOverview — every 4h (deepseek-v4-flash, 180s)

--- Retired (Jun 14) ---
- TradeBot-Consolidated — disabled. Split into Research + Executor.
```

## Load Analysis

| Time Block | Total Jobs | Heavy | Model Load |
|------------|-----------|-------|------------|
| 2-4am | 3 | 3 (all content) | `qwen3.5:27b` ×3 |
| 7-8am | 3 | 0 | `deepseek-v4-flash` ×3 |
| 9-10am | 2-3 | 1 (article) | `kimi-k2.6` + `deepseek-v4-flash` |
| 2-3pm | 2 | 1 (review) | `deepseek-v4-flash` + `qwen3.5:27b` |
| 6pm | 3-4 | 1 (forum bump Sun) | `kimi-k2.6` ×2-3 + `deepseek-v4-flash` |
| 8pm | 1 | 1 (night school) | `deepseek-v4-flash` |

## Model Breakdown

| Model | # Crons | Heavy Jobs | Notes |
|-------|---------|-----------|-------|
| kimi-k2.6 | **7** | 4 (content ×3 + article) | Main creative engine. 2-4am block is peak load |
| deepseek-v4-flash | **15** | 2 (night school, forum bump) | Ops/scans. Distributed well |
| qwen3.5:27b | **4** | 0 (content x3 + analytics) | NEW - replaces kimi-k2.6 for scheduled writing. ~5-10x lighter usage |
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
| 1471135533777424587 | #eveonion (alt) |

## Cron Registry (by Project)

### TradeBot (5 crons)
| Name | ID | Schedule | Model | Timeout | API Impact |
|------|-----|----------|-------|---------|------------|
| TradeBot-Consolidated | 78b66703 | every 5m | deepseek-v4-flash | 600s | Jupiter + Helius (heavy) |
| TradeBot-PortfolioOverview | 0eb02ac4 | every 4h | deepseek-v4-flash | 180s | Helius (light) |
| TradeBot-WeeklyReview | 2be91036 | Sat 2pm | deepseek-v4-flash | 600s | Helius (light) |
| TradeBot-Analytics | c8153b73 | Mon 10am | **qwen3.5:27b** | 180s | Helius (light) |
| TradeBot-DailyResearch | 457a5ae7 | 9:15am daily | deepseek-v4-flash | 300s | Web Search (3 calls)

### Content Empire (3 crons)
| Name | ID | Schedule | Model | Timeout | Notes |
|------|-----|----------|-------|---------|-------|
| ContentNova-aitoolalliance | 21260801 | 2am daily | **qwen3.5:27b** | 480s | Quality gate v3 |
| ContentNova-aibusinessinsider | 38c57c58 | 3am daily | **qwen3.5:27b** | 480s | Quality gate v3 |
| ContentNova-aicofounderstack | b44776e2 | 4am daily | **qwen3.5:27b** | 600s | Quality gate v3 |

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

## Total: 26 crons
- `kimi-k2.6`: **3** crons (live session overflow - EveOnion-Article + Kybernauts heavy items)
- `deepseek-v4-flash`: **18** crons (ops/scans/fast)
- `qwen3.5:27b`: **4** crons (scheduled writing + light analytics)
- Continuous jobs: 2 (every 5m, every 4h)

## Weekly Usage Budget (Ollama Pro)

**Problem:** Kimi-k2.6 is level 4 (extra heavy). 7 crons burning ~20-30 min GPU time each = **~3.5-5 hours/week of GPU time** from scheduled jobs alone. Ad-hoc work pushes over the weekly cap.

**Fix (2026-06-15):**
- **ContentNova x3** switched from `kimi-k2.6` -> `qwen3.5:27b` (level ~2, ~5-10x lighter)
- **TradeBot-Analytics** switched from `kimi-k2.6` -> `qwen3.5:27b`
- **Remaining kimi-k2.6:** Only EveOnion-Article + Kybernauts-Propaganda/ForumBump (special creative cases)
- **Expected savings:** ~50-70% reduction in scheduled GPU burn for content block

**If still hitting cap:**
1. Switch EveOnion-Article to `qwen3.5:27b`
2. Switch Kybernauts items to `qwen3.5:27b`
3. Move remaining heavy live sessions to `mistral-small` or buy extra usage balance

## Ollama Model Quick Reference

| Model | Level | Use Case | Weekly Burn |
|-------|-------|----------|-------------|
| kimi-k2.6 | 4 (extra heavy) | Live creative sessions, special creative crons | HIGH - minimize |
| deepseek-v4-pro | 4 (extra heavy) | Deep debugging, complex reasoning only | HIGH - rare use |
| deepseek-v4-flash | 3 (heavy) | Ops, scans, fast structured tasks | Medium |
| qwen3.5:27b | 2 (medium) | Scheduled writing, analytics, content | Low - preferred |
| mistral-small | 2 (medium) | Fast structured output, coding | Low |
| qwen3:30b | 2 (medium) | Fallback for qwen3.5:27b | Low |

## Next Review
Check this doc before adding any new cron. Update after every change.

## Last Updated
2026-06-15 -- Switched 4 crons from kimi-k2.6 to qwen3.5:27b to reduce weekly Ollama usage burn. Added model reference table.
| API | Daily Calls | Limit | Buffer | Status |
|-----|-----------|-------|--------|--------|
| Jupiter (lite-api) | ~3,000 | ~5,000/day | 40% | Safe |
| Helius RPC | ~500 | 50K/day | 99% | Very Safe |
| DexScreener | ~50 | No known limit | — | Safe |
| Web Search (Ollama) | ~30 | ~100/day | 70% | Safe |

### Rate Limiting in Code
- **429 cooldown**: 10-min shared cooldown across all modules
- **Jupiter quotes**: max 3 retries with 5s backoff
- **DexScreener**: 0.5s delay between pair queries
- **Research module**: 1.5s sleep between Jupiter price calls
- **Daemon**: stops execution on 429, resumes next cycle

### TradeBot Cron Coordination
| Cron | When | Calls API | Impact |
|------|------|-----------|--------|
| TradeBot-Research | Every 2h | Jupiter, Helius | ~30s, writes signals |
| TradeBot-Executor | Every 10m | Jupiter, Helius | ~30s, reads signals, executes |
| TradeBot-PortfolioOverview | Every 4h | Helius | Light — 6/day |
| TradeBot-DailyResearch | 9:15am | Web Search | 3 calls, writes brief |

**SOL Safety** (added Jun 14):
- SOL_MIN_SAFE = 0.003 — trigger refill when SOL drops below this (ATA rent threshold)
- SOL_MIN_HYSTERIA = 0.01 — bot runs normally above this
- Refill: min $5 per cycle, up to 15% of USDC
- Refill simulates before sending (catches rent/mana issues)
- All buys simulate before sending
- Discord report includes SOL balance on every cycle
- If refill sim fails, bot reports the error immediately instead of silently dropping TXs

## Next Review
Check this doc before adding any new cron. Update after every change.

## Last Updated
2026-06-14 — Added SOL safety guards. Split Consolidated into Research + Executor crons.
