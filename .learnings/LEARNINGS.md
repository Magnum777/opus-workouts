# Nova Learnings Archive

## 2026-06-06 — Cron Model Assignment Fix

**Issue:** Kybernauts-Propaganda and Kybernauts-ForumBump crons were failing with "Agent couldn't generate a response" when assigned to `kimi-k2.6`.

**Root cause:** `kimi-k2.6` appears to timeout or struggle on ops/scans tasks that involve browser automation, exec commands, and tool-heavy workflows. The model works fine for creative writing but not for agent-turn cron payloads with complex tool use.

**Fix:** Switched both back to `deepseek-v4-flash:cloud` per AGENTS.md rule — "Use deepseek-v4-flash for ops/scans (checks, sweeps, data pulls, simple reports)."

**Lesson:** Don't default to kimi-k2.6 for all cron tasks just because it's the main model. Match model to task type. Document this in scheduler.md.

---

## 2026-06-06 — Git Commit Hygiene

**Issue:** Workspace had 580 untracked files (PDFs, screenshots, output artifacts) mixed with 26 actual tracked changes.

**Fix:** Used `git add -u` to stage only modified tracked files, committed with descriptive message. Left untracked artifacts alone.

**Lesson:** For workspace repos with heavy artifact generation, `git add -u` is the right approach — don't blindly `git add .`.
