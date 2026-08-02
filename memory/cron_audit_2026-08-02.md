# Cron Audit Report — 2026-08-02

## Summary
- **Expected crons in config:** 29
- **Actual unique cron jobs found:** 35 (including duplicates and extras)
- **Duplicate jobs detected:** 5 pairs (10 crons)
- **Extra jobs not in expected config:** 3 (PromptPack crons)
- **Critical issues found:** 7
- **Warnings found:** 8

---

## Channel ID Reference
| Channel | Expected ID (from config) | Actual Resolved ID |
|---------|--------------------------|-------------------|
| #nova | 1470836415523983630 | 1470836415523983630 ✓ |
| #wordpress | 1471281549646364805 | 1471281549646364805 ✓ |
| #eveonion | 1470836416364126258 | 1484624659633934587 ⚠️ **MISMATCH** |
| #kybernauts | 1470836415685521440 | 1479156871641436265 ⚠️ **MISMATCH** |

**Note:** The expected config lists `#eveonion: 1470836416364126258` and `#kybernauts: 1470836415685521440`, but all actual crons resolve to `1484624659633934587` and `1479156871641436265` respectively. The system showed these as "resolved from..." in `cron list`, suggesting the configured references map to these IDs. The expected config file may have stale IDs.

---

## Audit Results (per expected config)

### CONTENT CRONS (#wordpress)

| # | NAME | MODEL | TIMEOUT | DELIVERY | FAILURE_ALERT | TOOLS_ALLOW | POST_LOG | ISSUES |
|---|------|-------|---------|----------|---------------|-------------|----------|--------|
| 1 | **ContentNova-aitoolalliance** | minimax-m3 | 480s | #wordpress ✓ | after=2, 1h ✓ | read,write,apply_patch,exec,web_search,web_fetch | YES ✓ | **MODEL WRONG** — expected deepseek-v4-flash, got minimax-m3. **TIMEOUT LOW** — expected 300s, got 480s (actually higher, ok). **Post-log references ContentNova-aitoolalliance** |
| 2 | **ContentNova-aibusinessinsider** | minimax-m3 | 600s | #wordpress ✓ | after=2, 1h ✓ | read,write,apply_patch,exec,web_search,web_fetch | YES ✓ | **MODEL WRONG** — expected deepseek-v4-flash, got minimax-m3. **TIMEOUT HIGH** — expected 300s, got 600s. **Post-log references ContentNova-aibusinessinsider** |
| 3 | **ContentNova-aicofounderstack** | minimax-m3 | 600s | #wordpress ✓ | after=2, 1h ✓ | read,write,apply_patch,exec,web_search,web_fetch | YES ✓ | **MODEL WRONG** — expected deepseek-v4-flash, got minimax-m3. **TIMEOUT HIGH** — expected 300s, got 600s. **Post-log references ContentNova-aicofounderstack** |

### EVEONION CRONS (#eveonion)

| # | NAME | MODEL | TIMEOUT | DELIVERY | FAILURE_ALERT | TOOLS_ALLOW | POST_LOG | ISSUES |
|---|------|-------|---------|----------|---------------|-------------|----------|--------|
| 4 | **EveOnion-NewsScan** | minimax-m3 | 480s | 1484624659633934587 | after=2, 1h ✓ | read,write,apply_patch,exec,web_search,web_fetch | YES ✓ | **TIMEOUT HIGH** — expected 180s, got 480s. Delivery channel ID mismatch vs expected config (see above). Post-log references EveOnion |
| 5 | **EveOnion-Article** | kimi-k2.6 | 480s | 1484624659633934587 | after=2, 1h ✓ | read,write,apply_patch,exec,web_search,web_fetch | YES ✓ | **TIMEOUT HIGH** — expected 300s, got 480s. Delivery channel ID mismatch vs expected config |
| 6 | **EveOnion-RedditTweet** | minimax-m3 | 480s | 1484624659633934587 | after=2, 1h ✓ | read,exec,web_search,web_fetch | YES ✓ | **TIMEOUT HIGH** — expected 180s, got 480s. Delivery channel ID mismatch vs expected config. **MISSING TOOLS:** needs write/apply_patch for post_log logging (prompt references post_log.py but toolsAllow lacks write/apply_patch — though exec can run python scripts that write) |
| 7 | **EveOnion-PersonaScan** | deepseek-v4-flash | 300s | 1484624659633934587 | after=2, 1h ✓ | read,write,apply_patch,exec,web_search,web_fetch | YES ✓ | **TIMEOUT HIGH** — expected 180s, got 300s. Delivery channel ID mismatch vs expected config. Post-log references EveOnion |

### KYBERNAUTS CRONS (#kybernauts)

| # | NAME | MODEL | TIMEOUT | DELIVERY | FAILURE_ALERT | TOOLS_ALLOW | POST_LOG | ISSUES |
|---|------|-------|---------|----------|---------------|-------------|----------|--------|
| 8 | **Kybernauts-Propaganda** | minimax-m3 | 180s | 1479156871641436265 | after=2, 1h ✓ | read,write,apply_patch,exec,image_generate,web_search | YES ✓ | **TIMEOUT OK** (expected 180s). Delivery channel ID mismatch vs expected config. Post-log references Kybernauts. **MISSING TOOLS:** needs upload-post for social media posting (prompt says "using upload-post skill" but toolsAllow lacks upload-post — though this may be a skill invocation, not a direct tool) |
| 9 | **Yagas-Intel-Collect** | minimax-m3 | 120s | 1479156871641436265 | MISSING | exec | YES (in nova-chat version) | **OLDER CRON (b36f7baa): FAILURE_ALERT MISSING entirely.** **NEWER CRON (f146de70): FAILURE_ALERT OK.** Duplicate exists. Older version has NO failureAlert, NO post_log in prompt. Delivery channel ID mismatch vs expected config |
| 10 | **Yagas-Propaganda-Post** | minimax-m3 | 180s | 1479156871641436265 | MISSING (older) / OK (newer) | exec (older) / read,write,apply_patch,exec,web_search,web_fetch (newer) | NO (older) / YES (newer) | **OLDER CRON (231a270e): FAILURE_ALERT MISSING.** **NEWER CRON (f52721ee): FAILURE_ALERT OK.** Duplicate exists. Older version prompt posts to Twitter/X AND Bluesky (violates "Discord-only" rule in newer config). Delivery channel ID mismatch vs expected config |

### AMAZON AFFILIATE CRONS (#wordpress)

| # | NAME | MODEL | TIMEOUT | DELIVERY | FAILURE_ALERT | TOOLS_ALLOW | POST_LOG | ISSUES |
|---|------|-------|---------|----------|---------------|-------------|----------|--------|
| 11 | **Amazon-Affiliate-Publish** | minimax-m3 | 480s | #wordpress ✓ | after=2, 1h ✓ | read,write,apply_patch,exec,web_search,web_fetch | YES ✓ | **NEWER CRON (5aec02c7): MODEL OK** (expected minimax-m3). **TIMEOUT OK** (expected 480s). Post-log present. **OLDER CRON (0b4757e7): MODEL WRONG** — expected minimax-m3, got deepseek-v4-flash. **TIMEOUT LOW** — expected 480s, got 180s. Duplicate exists. |
| 12 | **Amazon-Affiliate-Injector** | deepseek-v4-flash | 180s | #wordpress ✓ | after=2, 1h ✓ (newer) / MISSING (older) | read,write,apply_patch,exec (newer) / default (older) | YES (newer) / NO (older) | **NEWER CRON (895f97ba): MODEL OK, TIMEOUT OK, FAILURE_ALERT OK, POST_LOG OK.** **OLDER CRON (8b7e7792): FAILURE_ALERT MISSING entirely, POST_LOG missing from prompt, toolsAllowIsDefault=true (overly broad).** Duplicate exists. |
| 13 | **Amazon-Tracker-Weekly** | deepseek-v4-flash | 120s | 1524864332478021802 (newer) / #wordpress (older) | after=2, 1h ✓ (newer) / MISSING (older) | read,write,apply_patch,exec (newer) / default (older) | YES (newer) / NO (older) | **NEWER CRON (53f0d707): MODEL OK, TIMEOUT OK, FAILURE_ALERT OK, POST_LOG OK. BUT DELIVERS TO #finance (1524864332478021802), not #wordpress.** **OLDER CRON (cf11c261): FAILURE_ALERT MISSING, toolsAllowIsDefault=true, DELIVERS TO #wordpress.** Duplicate exists. Expected #wordpress but newer delivers to #finance. |

### OPS CRONS (#nova)

| # | NAME | MODEL | TIMEOUT | DELIVERY | FAILURE_ALERT | TOOLS_ALLOW | POST_LOG | ISSUES |
|---|------|-------|---------|----------|---------------|-------------|----------|--------|
| 14 | **spam-sweep-every-4h** | deepseek-v4-flash | 600s | #nova ✓ | MISSING | exec,read | N/A | **TIMEOUT HIGH** — expected 120s, got 600s. **FAILURE_ALERT MISSING entirely.** No post_log expected (ops cron) |
| 15 | **spam-pattern-discovery** | deepseek-v4-flash | 300s | #nova ✓ | MISSING | exec | N/A | **TIMEOUT HIGH** — expected 120s, got 300s. **FAILURE_ALERT MISSING entirely.** No post_log expected |
| 16 | **daily-brief-7am** | kimi-k2.6 | 300s | #nova ✓ | after=2, 1h ✓ | read,exec,web_search | N/A | **MODEL OK, TIMEOUT OK, FAILURE_ALERT OK.** No post_log expected (ops cron). toolsAllow OK |
| 17 | **gmail-cleanup-daily** | deepseek-v4-flash | 120s | #nova ✓ | MISSING | exec | N/A | **MODEL OK, TIMEOUT OK.** **FAILURE_ALERT MISSING entirely.** No post_log expected. toolsAllow very narrow (exec only) but adequate for single script run |
| 18 | **Iris-all-accounts-digest** | deepseek-v4-flash | 900s | #nova ✓ | after=1 (not 2), no cooldown | exec | N/A | **TIMEOUT HIGH** — expected 180s, got 900s. **FAILURE_ALERT CONFIGURED DIFFERENTLY** — after=1 (expected 2), no cooldownMs specified (expected 1h). toolsAllow narrow (exec only) but adequate |
| 19 | **Nova-Ops-Assessment** | deepseek-v4-flash | 180s | #nova ✓ | after=2, 1h ✓ | read,exec | N/A | **MODEL OK, TIMEOUT OK, FAILURE_ALERT OK.** No post_log expected. toolsAllow OK |
| 20 | **DS-Seed-Enforcer** | deepseek-v4-flash | 300s | #nova ✓ | after=2, 1h ✓ | read,write,apply_patch,exec,mem_search,mem_get | N/A | **MODEL OK.** **TIMEOUT HIGH** — expected 120s, got 300s. **FAILURE_ALERT OK.** No post_log expected. toolsAllow OK |
| 21 | **TD-Scanner** | deepseek-v4-flash | 300s | #nova ✓ | after=2, 1h ✓ | read,write,apply_patch,exec,web_search,mem_search,mem_get | N/A | **MODEL OK.** **TIMEOUT HIGH** — expected 120s, got 300s. **FAILURE_ALERT OK.** No post_log expected. toolsAllow OK |
| 22 | **NightSchool-8pm** | deepseek-v4-flash | 3600s | #nova ✓ | MISSING | exec,web_search,web_fetch,read,write | N/A | **MODEL OK, TIMEOUT OK** (expected 3600s). **FAILURE_ALERT MISSING entirely.** No post_log expected. toolsAllow OK |
| 23 | **NightSchool-NAS-Sync** | deepseek-v4-flash | 300s | #nova ✓ | after=2, 1h ✓ | read,exec | N/A | **MODEL OK, TIMEOUT OK.** **FAILURE_ALERT OK.** No post_log expected. toolsAllow OK |
| 24 | **Weekly-MemoryHygiene** | kimi-k2.6 | 900s | #nova ✓ | after=2, 1h ✓ | read,write,apply_patch,exec,mem_search,mem_get | N/A | **MODEL OK, TIMEOUT OK.** **FAILURE_ALERT OK.** No post_log expected. toolsAllow OK |
| 25 | **Daily-MemorySweep** | deepseek-v4-flash | 300s | #nova ✓ | after=3 (not 2), 1h | read,write,apply_patch,exec,mem_search,mem_get | N/A | **MODEL OK, TIMEOUT OK.** **FAILURE_ALERT DIFFERENT** — after=3 (expected 2). No post_log expected. toolsAllow OK |
| 26 | **Weekly-SkillUpdate** | deepseek-v4-flash | 120s | #nova ✓ | after=2, 1h ✓ | read,exec | N/A | **MODEL OK, TIMEOUT OK.** **FAILURE_ALERT OK.** No post_log expected. toolsAllow OK |
| 27 | **Weekly-SkillDiscovery** | deepseek-v4-flash | 300s | #nova ✓ | after=2, 1h ✓ | read,write,apply_patch,exec,web_search | N/A | **MODEL OK, TIMEOUT OK.** **FAILURE_ALERT OK.** No post_log expected. toolsAllow OK |
| 28 | **Finance-NAS-Backup** | deepseek-v4-flash | 60s | #finance (1524864332478021802) | after=2, 1h ✓ | exec | N/A | **MODEL OK.** **TIMEOUT LOW** — expected 300s, got 60s. **DELIVERY WRONG** — expected #nova, delivers to #finance. No post_log expected. toolsAllow narrow (exec only) |
| 29 | **Workspace-NAS-Backup** | deepseek-v4-flash | 1800s | #nova ✓ | after=2, 1h ✓ | read,write,apply_patch,exec | N/A | **MODEL OK.** **TIMEOUT HIGH** — expected 300s, got 1800s. **FAILURE_ALERT OK.** No post_log expected. toolsAllow OK |

---

## Duplicate Cron Jobs Found

| Job Name | Count | IDs | Recommendation |
|----------|-------|-----|----------------|
| Amazon-Affiliate-Injector | 2 | 895f97ba (nova-chat, newer), 8b7e7792 (wordpress, older) | **Delete older** (wordpress-owned). Newer has post_log, failureAlert, correct tools. |
| Yagas-Intel-Collect | 2 | b36f7baa (no owner, older), f146de70 (nova-chat, newer) | **Delete older** (no owner). Newer has failureAlert, post_log, web_search. |
| Yagas-Propaganda-Post | 2 | 231a270e (no owner, older), f52721ee (nova-chat, newer) | **Delete older** (no owner). Newer has failureAlert, correct Discord-only rule, post_log. Older posts to Twitter/X+Bluesky. |
| Amazon-Tracker-Weekly | 2 | 53f0d707 (nova-chat, newer), cf11c261 (wordpress, older) | **Delete older** (wordpress-owned). Newer has post_log, failureAlert. Note: newer delivers to #finance, older to #wordpress — expected is #wordpress per config. |
| Amazon-Affiliate-Publish | 2 | 0b4757e7 (wordpress, older), 5aec02c7 (nova-chat, newer) | **Delete older** (wordpress-owned). Newer has correct model (minimax-m3), correct timeout (480s), post_log. |

## Extra Cron Jobs (Not in Expected Config)

| Job Name | Model | Timeout | Delivery | Notes |
|----------|-------|---------|----------|-------|
| **PromptPack-aitoolalliance** | kimi-k2.6 | 420s | #wordpress | Daily prompt pack generation. Not in expected 29. Has post_log logic in prompt. |
| **PromptPack-aicofounderstack** | kimi-k2.6 | 420s | #wordpress | Daily prompt pack generation. Not in expected 29. |
| **PromptPack-aibusinessinsider** | kimi-k2.6 | 420s | #wordpress | Daily prompt pack generation. Not in expected 29. aibusinessinsider.org is Cloudflare-403 blocked per prompt. |

---

## Critical Issues Summary

### 🔴 CRITICAL: Wrong Models (ContentNova sites)
- ContentNova-aitoolalliance: **minimax-m3** instead of expected **deepseek-v4-flash**
- ContentNova-aibusinessinsider: **minimax-m3** instead of expected **deepseek-v4-flash**
- ContentNova-aicofounderstack: **minimax-m3** instead of expected **deepseek-v4-flash**

**Impact:** ContentNova sites are using creative model (minimax-m3) instead of ops model (deepseek-v4-flash). If the expected config is correct, these are misconfigured. However, the actual prompts are complex content-generation tasks that may genuinely benefit from minimax-m3. **Verify if expected config is stale or if crons need fixing.**

### 🔴 CRITICAL: Missing Failure Alerts
These crons have NO failureAlert config — failures go silently:
1. **spam-sweep-every-4h** (c96ff863)
2. **spam-pattern-discovery** (20a09bb0)
3. **gmail-cleanup-daily** (8b079437)
4. **NightSchool-8pm** (3071d872)
5. **Amazon-Affiliate-Injector OLD** (8b7e7792)
6. **Amazon-Tracker-Weekly OLD** (cf11c261)
7. **Yagas-Intel-Collect OLD** (b36f7baa)
8. **Yagas-Propaganda-Post OLD** (231a270e)

### 🔴 CRITICAL: Duplicate Jobs
5 pairs of duplicate crons running = wasted compute, race conditions, double-posting risk.

### 🟡 WARNING: Wrong Delivery Channel
- **Finance-NAS-Backup** delivers to #finance instead of expected #nova
- **Amazon-Tracker-Weekly (newer)** delivers to #finance instead of expected #wordpress

### 🟡 WARNING: Channel ID Mismatches
- Expected `#eveonion: 1470836416364126258` but actual crons use `1484624659633934587`
- Expected `#kybernauts: 1470836415685521440` but actual crons use `1479156871641436265`
- The system resolves these correctly ("resolved from..."), so the expected config file likely has stale IDs.

### 🟡 WARNING: Timeout Deviations
| Cron | Expected | Actual | Verdict |
|------|----------|--------|---------|
| spam-sweep-every-4h | 120s | 600s | Too high |
| spam-pattern-discovery | 120s | 300s | Too high |
| Iris-all-accounts-digest | 180s | 900s | Too high |
| DS-Seed-Enforcer | 120s | 300s | Too high |
| TD-Scanner | 120s | 300s | Too high |
| Workspace-NAS-Backup | 300s | 1800s | Too high |
| Finance-NAS-Backup | 300s | 60s | **Too low — likely to timeout** |
| EveOnion-NewsScan | 180s | 480s | Too high |
| EveOnion-Article | 300s | 480s | Too high |
| EveOnion-RedditTweet | 180s | 480s | Too high |
| EveOnion-PersonaScan | 180s | 300s | Too high |
| ContentNova-aibusinessinsider | 300s | 600s | Too high |
| ContentNova-aicofounderstack | 300s | 600s | Too high |
| Daily-MemorySweep | 300s | 300s | OK (failureAlert after=3 vs expected 2) |

---

## Recommendations

1. **Fix or confirm ContentNova models:** Either update expected config to reflect minimax-m3 (which may be correct for creative content) or change cron models to deepseek-v4-flash.
2. **Add failureAlert to all missing crons:** spam-sweep, spam-pattern-discovery, gmail-cleanup, NightSchool-8pm, and the older duplicate entries.
3. **Delete 5 older duplicate crons:** All owned by "wordpress" or have no owner, missing failureAlert/post_log, and superseded by newer nova-chat versions.
4. **Fix Finance-NAS-Backup timeout:** Increase from 60s to 300s; decide on delivery channel (#finance vs #nova).
5. **Fix Amazon-Tracker-Weekly delivery:** Newer version delivers to #finance but expected config says #wordpress.
6. **Update expected config channel IDs:** #eveonion and #kybernauts IDs are stale in the expected config file.
7. **Review EveOnion timeouts:** All 4 EveOnion crons have significantly higher timeouts than expected. May be intentional due to web_search usage.
8. **Review ops cron timeouts:** Several ops crons (spam-sweep, DS, TD) have higher timeouts than expected. May be intentional.
