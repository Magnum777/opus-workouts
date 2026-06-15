# Learnings Log

## 2026-06-14 — Correction: Stop Running Broken Crons

**Category:** correction
**Source:** Opus, #kybernauts

**Rule:** If a cron (or any automated task) fails with a **persistent/systemic error** — missing script, bad credentials, upstream API change, broken config — **do NOT keep manually re-running it**. One retry is fine if the failure looks transient (rate limit, temporary timeout). If it fails again with the same root cause, **stop immediately**.

**Exception:** If I can actually fix the root cause in the same session (correct path, install missing package, update config), then fix it. If the fix requires the human (new password, new API key, external account recovery), **stop and report the blocker instead of burning tokens on repeated failures**.

**What I did wrong today:**
- ForumBump failed 6 times with the same EVE SSO login issue
- I kept queuing it again and again because "the user said retry all failed crons"
- Each run cost tokens and accomplished nothing
- I should have stopped after the first or second failure and reported: "ForumBump is broken — EVE SSO creds are stale, needs you to update"

**WAL protocol reminder:** When corrected, write first, respond second. This entry is that write.
