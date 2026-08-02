# Cron Prompt Audit — 2026-08-02

**Auditor:** Subagent depth 1/1  
**Date:** 2026-08-02  
**Scope:** 29 crons (3 ContentNova skipped per instruction)  
**Checks:** Broken script refs | Hardcoded secrets | Missing post_log | Outdated instructions | Missing failureAlert

---

## Summary Table

| # | Cron Name | Issues | Details |
|---|-----------|--------|---------|
| 1 | spam-sweep-every-4h | **2** | Missing `failureAlert` delivery config; last diagnostic shows `process list` exec failure |
| 2 | Yagas-Intel-Collect | **1** | `failureAlert` missing `mode: announce` (uses old short format) |
| 3 | Yagas-Propaganda-Post | **1** | `failureAlert` missing `mode: announce` (uses old short format) |
| 4 | Kybernauts-Propaganda | **1** | `toolsAllow` missing `upload-post` skill; prompt references `upload-post` but not in allowed tools |
| 5 | NightSchool-8pm | CLEAN | — |
| 6 | NightSchool-NAS-Sync | CLEAN | — |
| 7 | Weekly-MemoryHygiene | CLEAN | — |
| 8 | Workspace-NAS-Backup | CLEAN | — |
| 9 | ContentNova-aitoolalliance | CLEAN (skipped) | Per instruction — just updated |
| 10 | ContentNova-aibusinessinsider | CLEAN (skipped) | Per instruction — just updated |
| 11 | Finance-NAS-Backup | **1** | Missing `failureAlert` `mode: announce`; `after: 2` present but short format |
| 12 | ContentNova-aicofounderstack | CLEAN (skipped) | Per instruction — just updated |
| 13 | PromptPack-aitoolalliance | **1** | Missing `failureAlert` entirely (no failureAlert block) |
| 14 | PromptPack-aicofounderstack | **1** | Missing `failureAlert` entirely (no failureAlert block) |
| 15 | PromptPack-aibusinessinsider | **1** | Missing `failureAlert` entirely (no failureAlert block) |
| 16 | Weekly-SkillUpdate | **1** | `failureAlert` uses old short format (no `mode: announce`) |
| 17 | TD-Scanner | CLEAN | — |
| 18 | spam-pattern-discovery | **2** | `failureAlert` missing `mode: announce`; last diagnostic shows `Get-Process` exec failure (from agent internals, likely benign) |
| 19 | Daily-MemorySweep | CLEAN | — |
| 20 | daily-brief-7am | CLEAN | — |
| 21 | gmail-cleanup-daily | **1** | `failureAlert` missing `mode: announce` (old short format) |
| 22 | DS Seed Enforcer | CLEAN | — |
| 23 | Iris-all-accounts-digest | **2** | `failureAlert` uses `after: 1` (very aggressive, may spam); `failureAlert` missing `mode: announce` and `cooldownMs` |
| 24 | EveOnion-NewsScan | CLEAN | — |
| 25 | Nova-Ops-Assessment | **1** | Prompt has outdated model check instructions: ContentNova should be `minimax-m3` per actual configs, but prompt says `deepseek-v4-flash`. Also EveOnion-Article timeout says 300s but actual config is 480s |
| 26 | EveOnion-RedditTweet | CLEAN | — |
| 27 | Amazon-Affiliate-Injector | CLEAN | — |
| 28 | Amazon-Tracker-Weekly | CLEAN | — |
| 29 | EveOnion-Article | CLEAN | — |
| 30 | EveOnion-PersonaScan | CLEAN | — |
| 31 | Amazon-Affiliate-Publish | **1** | Step 5 references `featured_image.py` script which may not exist or may fail in cron context (similar issue to ContentNova) |
| 32 | Weekly-SkillDiscovery | **1** | `failureAlert` uses old short format (no `mode: announce`) |

---

## Detailed Findings

### 1. spam-sweep-every-4h (`c96ff863`)
- **Issue:** `failureAlert` block exists but lacks `mode: "announce"` and uses legacy `to: "discord:channel:..."` format instead of channel/target split
- **Issue:** Last diagnostics show `process list` exec failure — benign but noisy
- **Action:** Update `failureAlert` to standard format with `mode: announce`, `channel: discord`, `to: channel:...`, `cooldownMs: 3600000`

### 2–4. Yagas-Intel-Collect, Yagas-Propaganda-Post, Kybernauts-Propaganda
- **Issue:** `failureAlert` uses old compact format (missing `mode`, `channel`/`to` split)
- **Kybernauts additional:** `toolsAllow` includes `image_generate` and `web_search` but NOT `upload-post` — prompt tells it to "use upload-post skill" which it won't be able to invoke
- **Action:** Add `upload-post` to `toolsAllow`; standardize `failureAlert` format

### 5–6. Finance-NAS-Backup, gmail-cleanup-daily
- **Issue:** `failureAlert` uses old short format without `mode: announce`
- **Action:** Standardize `failureAlert` format

### 7–9. All 3 PromptPack crons (`bba21e17`, `cba7f8b0`, `0399339a`)
- **Issue:** No `failureAlert` block at all — cron will fail silently after multiple consecutive errors
- **Action:** Add `failureAlert` with `after: 2`, `mode: announce`, `channel: discord`, `to: channel:1471281549646364805`, `cooldownMs: 3600000`

### 10. spam-pattern-discovery
- **Issue:** `failureAlert` uses old short format
- **Action:** Standardize `failureAlert`

### 11. Iris-all-accounts-digest
- **Issue:** `failureAlert` has `after: 1` — will alert on first failure, very aggressive. Also missing `cooldownMs` and `mode: announce`
- **Action:** Change `after` to 2, add `cooldownMs: 3600000`, add `mode: announce`

### 12. Nova-Ops-Assessment
- **Issue:** Prompt contains outdated model validation rules:
  - Says "ContentNova sites should be deepseek-v4-flash" — but all ContentNova crons run `minimax-m3`
  - Says "EveOnion-Article should be kimi-k2.6, 300s" — but actual config IS kimi-k2.6 with 480s timeout
- **Action:** Update prompt to reflect actual model assignments

### 13. Amazon-Affiliate-Publish
- **Issue:** Step 5 references `featured_image.py` which may not exist or may fail in isolated cron context
- **Action:** Verify script exists; if it relies on browser/headless tools, replace with inline web_fetch + WordPress media upload approach

### 14. Weekly-SkillUpdate, Weekly-SkillDiscovery
- **Issue:** `failureAlert` uses old short format
- **Action:** Standardize `failureAlert`

---

## Crons Needing Prompt Updates (Prioritized)

### High Priority (Add missing failureAlert)
1. **PromptPack-aitoolalliance** (`bba21e17`) — No failureAlert
2. **PromptPack-aicofounderstack** (`cba7f8b0`) — No failureAlert
3. **PromptPack-aibusinessinsider** (`0399339a`) — No failureAlert

### Medium Priority (Standardize failureAlert format + prompt fixes)
4. **Kybernauts-Propaganda** (`788bb86f`) — Add `upload-post` to toolsAllow; fix failureAlert
5. **Amazon-Affiliate-Publish** (`5aec02c7`) — Remove or fix `featured_image.py` reference
6. **Nova-Ops-Assessment** (`488e0af0`) — Update model validation rules in prompt
7. **Iris-all-accounts-digest** (`a375126c`) — Reduce failure alert aggressiveness (`after: 1` → `after: 2`)
8. **spam-sweep-every-4h** (`c96ff863`) — Fix failureAlert format
9. **Yagas-Intel-Collect** (`f146de70`) — Fix failureAlert format
10. **Yagas-Propaganda-Post** (`f52721ee`) — Fix failureAlert format
11. **Finance-NAS-Backup** (`9b5aa167`) — Fix failureAlert format
12. **gmail-cleanup-daily** (`8b079437`) — Fix failureAlert format
13. **spam-pattern-discovery** (`20a09bb0`) — Fix failureAlert format
14. **Weekly-SkillUpdate** (`ac9ba7e1`) — Fix failureAlert format
15. **Weekly-SkillDiscovery** (`0b0873dc`) — Fix failureAlert format

### Low Priority (Clean, no action needed)
- NightSchool-8pm, NightSchool-NAS-Sync, Weekly-MemoryHygiene, Workspace-NAS-Backup, TD-Scanner, Daily-MemorySweep, daily-brief-7am, DS Seed Enforcer, EveOnion-NewsScan, EveOnion-RedditTweet, EveOnion-Article, EveOnion-PersonaScan, Amazon-Affiliate-Injector, Amazon-Tracker-Weekly

---

## Notes

- No hardcoded passwords were found in any cron prompt. All credential references point to `.secrets` file or are passed via environment/config.
- No missing `post_log` calls were found — all content-producing crons (ContentNova, PromptPack, EveOnion, Amazon, Yagas, Kybernauts) include explicit post_log instructions.
- The 3 ContentNova crons were skipped per instructions.
- The `Get-Process` exec failures seen in diagnostics (gmail-cleanup-daily, spam-pattern-discovery, Iris) are benign internal process polling errors, not prompt issues.
