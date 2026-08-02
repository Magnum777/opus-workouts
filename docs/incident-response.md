# Incident Response Process

## Severity Levels

**P0 — Critical (wake Opus immediately)**
- Site DOWN (site_monitor.py reports HTTP failure)
- Data loss (backup failed + NAS unreachable)
- Security breach (unauthorized access detected)
- Cron failed 3+ consecutive times on a P0 job (content pipeline, backup)

**P1 — High (surface in next heartbeat, fix if possible)**
- Cron failed 2x (failure alert triggers)
- Content quality validator FAIL on published article
- Disk space WARNING (<15% free)
- SSL cert expiring <14 days

**P2 — Medium (log, fix in next maintenance window)**
- Cron failed 1x (transient, usually self-recovers)
- Content quality validator WARN
- Disk space trending low (>80% used)
- Minor script errors that don't break functionality

**P3 — Low (track, batch fix weekly)**
- Cosmetic issues (formatting, non-blocking diagnostics)
- Code quality improvements
- Performance optimizations

## Response Protocol

### P0 — Critical
1. Alert Opus in #nova immediately with: what broke, impact, and what you're trying
2. Attempt automatic fix (restart cron, re-run script, switch fallback)
3. If auto-fix fails within 10 minutes, escalate again with: what failed, what was tried
4. Document in memory/error-log.md

### P1 — High
1. Log in memory/error-log.md
2. Attempt fix if straightforward (re-run, retry, adjust)
3. Surface in next ops assessment or heartbeat
4. If not resolved in 24h, escalate to P0

### P2 — Medium
1. Log in memory/error-log.md
2. Queue for next maintenance window (Sunday ops)
3. Fix during scheduled time

### P3 — Low
1. Log in memory/error-log.md
2. Batch with other P3s for weekly review

## Cron Failure Handling

| Consecutive Failures | Action |
|---------------------|--------|
| 1 | Log, monitor (may be transient) |
| 2 | Failure alert fires to #nova (already configured) |
| 3 | Escalate to P1, attempt auto-fix |
| 5+ | Escalate to P0, wake Opus |

## Content Pipeline Failures

- ContentNova/PromptPack publish fails → check WordPress API, retry once
- Quality validator FAIL → auto-fix if possible (word count, headings), flag in report
- Post log gap detected → surface in ops assessment
- Duplicate title detected → surface in ops assessment, skip publish

## Contacts

- Opus (owner): Discord #nova, critical decisions only
- System: #nova channel for automated alerts
- Backup check: Weekly ops assessment (9am ET daily)