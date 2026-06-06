# Errors

Command failures and integration errors.

---

## 2026-06-01 - Weekly cron timeouts (x3)
**Category:** integration
**Crons:** Iris-all-accounts-digest, Weekly-MemoryHygiene, Weekly-SkillUpdate

All three timed out by ~1s past their limit:
- Iris: 241s run / 240s limit → bumped to 300s
- MemoryHygiene: 121s run / 120s limit → bumped to 180s
- SkillUpdate: 121s run / 120s limit → bumped to 180s

Observation: These are the tightest-tolerance crons. All three are weekly or daily with multi-step payloads. The timeout bump should resolve — none had other errors (no runtime failures, no delivery issues).

## 2026-06-02 — Iris-all-accounts-digest 2nd timeout (300.6s / 300s limit)
**Category:** integration

Iris timed out again despite the 240→300s bump. The 2nd run took 300.6s vs the 300s limit — still ~0.2s over. Root cause: sequential IMAP connections across 4 Gmail accounts are slower than anticipated, with per-account scan times varying based on inbox size and connection quality.

**Fix:** Bumped timeout to 360s (+60s), enabled failure alerts (notify #nova after 1 consecutive error).

**Escalation path:** If it times out at 360s, the Iris script itself is hanging on a specific account — needs per-account timeout logic or account-specific debugging.
[kybernauts] Propaganda failed: Twitter/X auth not configured (no UPLOAD_POST_API_KEY or UPLOADPOST_API_KEY env var)
