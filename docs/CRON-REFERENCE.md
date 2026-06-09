# Cron Job Reference

> Current as of 2026-05-08. All times Eastern (America/New_York).

## Active Cron Jobs

### TradeBot

| ID | Name | Schedule | Agent | Model | Channel |
|----|------|----------|-------|-------|---------|
| 4d9ef30e | TradeBot-Scout | Every 10min | tradebot | deepseek-v4-flash:cloud | #tradebot |
| f3662f2c | TradeBot-Executor | Every 15min (5min offset) | tradebot | deepseek-v4-flash:cloud | #tradebot |
| 7f691ad4 | TradeBot-CryptoResearch | Every 1hr | tradebot | deepseek-v4-flash:cloud | #tradebot |

### EveOnion

| ID | Name | Schedule | Agent | Model | Channel |
|----|------|----------|-------|-------|---------|
| d4bb7a00 | EveOnion-NewsScan | Daily 8am ET | eveonion | deepseek-v4-flash:cloud | #eveonion |
| 005d8eba | EveOnion-DailyTweet | Daily 2:30pm ET | eveonion | deepseek-v4-flash:cloud | #eveonion |
| f4567195 | EveOnion-Article | Tue+Fri 9am ET | eveonion | deepseek-v4-flash:cloud | #eveonion |

### Kybernauts

| ID | Name | Schedule | Agent | Model | Channel |
|----|------|----------|-------|-------|---------|
| d27750c9 | Kybernauts-Propaganda | Every 2 days 6pm ET | kybernauts | deepseek-v4-flash:cloud | #kybernauts |
| ac348e21 | Kybernauts-ForumBump | Sunday 6pm ET | kybernauts | deepseek-v4-flash:cloud | #kybernauts |

### Daily Brief

| ID | Name | Schedule | Agent | Model | Channel |
|----|------|----------|-------|-------|---------|
| 0552b684 | daily-brief-7am | Daily 7am ET | nova-chat | (default) | #general |

## Deleted Jobs

| Name | Deleted | Reason |
|------|---------|--------|
| Kybernauts-HealthCheck | 2026-05-08 | Opus didn't want daily health check |

## Cron Management

```bash
openclaw cron list                    # List all jobs
openclaw cron list --include-disabled # Include disabled jobs
openclaw cron runs <jobId>            # View run history
```

In-session management via the `cron` tool:
- `cron action=add` — Create new job
- `cron action=update jobId=<id>` — Update job
- `cron action=remove jobId=<id>` — Delete job
- `cron action=run jobId=<id>` — Trigger immediately

## Adding New Cron Jobs

When creating cron jobs, follow these patterns:

1. **Use isolated sessions** (`sessionTarget: "isolated"`) for all cron tasks
2. **Specify agentId** to route to the correct agent (tradebot, eveonion, kybernauts)
3. **Use deepseek-v4-flash:cloud** for cost efficiency unless the task needs better reasoning
4. **Set delivery channel** explicitly: `"to": "channel:<DISCORD_CHANNEL_ID>"`
5. **Include context** in the message — cron sessions start fresh with no conversation history
6. **Reference file paths** with absolute paths (`C:\Users\compj\.openclaw\workspace\...`)