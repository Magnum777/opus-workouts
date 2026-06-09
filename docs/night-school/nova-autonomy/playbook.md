# Nova Autonomy Playbook

## Overview

Building a self-managing AI agent that operates continuously without constant human intervention. This playbook covers heartbeat systems, cron scheduling, self-healing, and smart monitoring for OpenClaw-based agents.

## Core Concepts

### Cron vs Heartbeat

| Feature | Cron | Heartbeat |
|---------|------|-----------|
| **Timing** | Exact schedule (e.g., "every 4h at :00") | Approximate (e.g., "every 4h from last run") |
| **Use case** | Time-specific tasks, external deadlines | Continuous monitoring, self-paced work |
| **Context** | New session each run | Same session, accumulates context |
| **Precision** | High - runs at specific time | Lower - runs when polled |
| **Best for** | Reports, backups, scheduled posts | Health checks, task queues, monitoring |

**When to use each:**
- **Cron:** "Send report every Friday at 5pm"
- **Heartbeat:** "Check if anything needs attention, every 15 minutes"

### The Autonomy Stack

```
┌─────────────────────────────────────────────────────┐
│                 User Commands                       │
│         (Explicit requests, overrides)              │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              Heartbeat System                       │
│    (Continuous monitoring, task discovery)          │
│    - Read HEARTBEAT.md                              │
│    - Check task queues                              │
│    - Self-heal if stuck                             │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                Cron Jobs                            │
│    (Scheduled tasks, periodic work)                 │
│    - Session cleanup                                │
│    - Memory distillation                            │
│    - Income research                                │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              Sub-Agent Swarm                        │
│    (Parallel task execution)                        │
│    - Spawn workers for specific tasks               │
│    - Monitor health via AGENT-SYNC.md               │
│    - Auto-restart failed agents                     │
└─────────────────────────────────────────────────────┘
```

## Heartbeat Implementation

### File Structure

```
workspace/
├── HEARTBEAT.md          # Task queue for heartbeat
├── HEARTBEAT-STATE.md    # Current state, last run, status
└── HEARTBEAT-LOG.md      # Historical runs (optional)
```

### HEARTBEAT.md Format

```markdown
# Heartbeat Tasks

## Pending
- [ ] Check credit balances
- [ ] Review sub-agent health
- [ ] Process inbox messages

## In Progress
- [task-name] Started at YYYY-MM-DD HH:MM

## Completed (Last Run)
- [x] Task 1 - Completed at YYYY-MM-DD HH:MM
- [x] Task 2 - Completed at YYYY-MM-DD HH:MM
```

### Heartbeat Loop

```javascript
// Pseudo-code for heartbeat handler
async function handleHeartbeat() {
  // 1. Read heartbeat file
  const tasks = readHeartbeatTasks()
  
  // 2. If no tasks → acknowledge and exit
  if (tasks.pending.length === 0) {
    return "HEARTBEAT_OK"
  }
  
  // 3. Process tasks
  for (const task of tasks.pending) {
    await executeTask(task)
    markComplete(task)
  }
  
  // 4. Update state
  updateHeartbeatState({
    lastRun: new Date(),
    tasksCompleted: tasks.pending.length
  })
  
  // 5. Report results (don't include HEARTBEAT_OK)
  return formatResults(tasks.completed)
}
```

### Key Principle: Don't Spam

**Bad:** Sending "HEARTBEAT_OK" for every cron completion
**Good:** Only respond to explicit heartbeat polls

**Opus instruction:** "Stop sending HEARTBEAT_OK for every cron job completion. Only use it when explicitly polled for heartbeat tasks."

## Cron Best Practices

### Spacing & Timing

```yaml
# Good: Spread out, no overlaps
- name: "Session Cleanup"
  schedule: "0 */6 * * *"  # Every 6 hours
  
- name: "Health Check"
  schedule: "*/15 * * * *"  # Every 15 minutes
  
- name: "Credit Check"
  schedule: "0 9 * * *"  # Daily at 9 AM
  
- name: "Memory Distillation"
  schedule: "0 3 * * *"  # Daily at 3 AM

# Bad: All at once
- name: "Task 1"
  schedule: "0 * * * *"  # Every hour at :00
  
- name: "Task 2"
  schedule: "0 * * * *"  # Same time = conflict!
```

### Session Management

**Problem:** Long-running sessions accumulate context → expensive, slow

**Solution:** New session per task, cleanup old sessions

```javascript
// Cron job with fresh session
openclaw cron add \
  --name "Daily Research" \
  --every "24h" \
  --session "research-daily" \
  --task "Research new opportunities" \
  --cleanup "delete"  # Auto-cleanup after run
```

**Cleanup cron:**
```bash
# Delete sessions older than 24 hours
openclaw cron add \
  --name "Session Cleanup" \
  --every "6h" \
  --command "openclaw sessions cleanup --older-than 24h"
```

## Self-Healing Patterns

### Pattern 1: Watchdog Cron

```javascript
// Monitor for stuck agents
async function watchdogCheck() {
  const agents = await subagents.list()
  const now = Date.now()
  
  for (const agent of agents) {
    const age = now - agent.lastActivity
    
    // Agent inactive for >30 minutes?
    if (age > 30 * 60 * 1000 && agent.status === 'running') {
      // Mark as lost
      await subagents.kill(agent.id)
      
      // Optionally restart
      await subagents.spawn({
        task: agent.originalTask,
        label: `${agent.label}-recovered`
      })
      
      // Log the recovery
      logRecovery(agent)
    }
  }
}
```

### Pattern 2: Task Retry with Backoff

```javascript
async function executeWithRetry(task, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const result = await executeTask(task)
      return result
    } catch (error) {
      if (attempt === maxRetries) {
        // Final failure - escalate to user
        await notifyUser(`Task failed after ${maxRetries} attempts: ${task.name}`)
        throw error
      }
      
      // Wait before retry (exponential backoff)
      const delay = Math.pow(2, attempt) * 1000  // 2s, 4s, 8s
      await sleep(delay)
    }
  }
}
```

### Pattern 3: Circuit Breaker

```javascript
class CircuitBreaker {
  constructor(failureThreshold = 5, resetTimeout = 60000) {
    this.failures = 0
    this.threshold = failureThreshold
    this.resetTimeout = resetTimeout
    this.state = 'CLOSED'  // CLOSED, OPEN, HALF_OPEN
  }
  
  async execute(task) {
    if (this.state === 'OPEN') {
      throw new Error('Circuit breaker open - too many failures')
    }
    
    try {
      const result = await task()
      this.onSuccess()
      return result
    } catch (error) {
      this.onFailure()
      throw error
    }
  }
  
  onSuccess() {
    this.failures = 0
    this.state = 'CLOSED'
  }
  
  onFailure() {
    this.failures++
    if (this.failures >= this.threshold) {
      this.state = 'OPEN'
      setTimeout(() => {
        this.state = 'HALF_OPEN'
      }, this.resetTimeout)
    }
  }
}
```

## Sub-Agent Coordination

### AGENT-SYNC.md Structure

```markdown
# Agent Sync Status

Last updated: 2026-02-27 21:45:00

## Active Agents

| Agent | Status | Task | Last Activity | Health |
|-------|--------|------|---------------|--------|
| Harvester | Awake | Fiverr research | 2 min ago | ✅ |
| Builder | Sleeping | - | 1 hour ago | ✅ |
| Sentinel | Awake | Health monitoring | 30 sec ago | ✅ |

## Recent Completions
- Income-Nova: Completed PPH research (20 min ago)
- Content-Nova: Published 3 posts (1 hour ago)

## Failed/Recovered
- Research-Nova: Failed at 18:30, restarted at 18:35
```

### Spawn Limits

**Rule:** Max 4-6 active shards at once

```javascript
async function spawnWithLimit(task, label) {
  const active = await subagents.list({ activeMinutes: 30 })
  
  if (active.length >= 5) {
    // Queue the task instead
    await addToQueue({ task, label, queuedAt: new Date() })
    return { status: 'queued', position: active.length }
  }
  
  return await sessions_spawn({
    task,
    label,
    cleanup: 'delete'
  })
}
```

### Communication Patterns

**Howl (Broadcast):**
```javascript
// Send to all active agents
async function howl(message) {
  const agents = await subagents.list()
  for (const agent of agents) {
    await sessions_send({
      sessionKey: agent.sessionKey,
      message: `[BROADCAST] ${message}`
    })
  }
}
```

**Whisper (Direct):**
```javascript
// Send to specific agent
async function whisper(agentLabel, message) {
  const agent = await subagents.find({ label: agentLabel })
  await sessions_send({
    sessionKey: agent.sessionKey,
    message
  })
}
```

**Pulse (Health Check):**
```javascript
// Request status from all agents
async function pulse() {
  const agents = await subagents.list()
  const responses = []
  
  for (const agent of agents) {
    const response = await sessions_send({
      sessionKey: agent.sessionKey,
      message: 'PULSE_CHECK',
      timeoutSeconds: 30
    })
    responses.push({ agent: agent.label, status: response })
  }
  
  return responses
}
```

## Proactive Behavior Rules

### When to Act Without Asking

✅ **Do act:**
- Credit monitoring (alert if low)
- Critical error detection
- Scheduled tasks (cron)
- Health checks
- Queue processing

❌ **Don't act:**
- External communications (emails, posts) without approval
- Financial transactions without confirmation
- Major architectural changes
- Anything that affects user's public presence

### Flow State Respect

**Detect flow state:**
- User actively messaging (<5 min between messages)
- User in deep work session (marked in SESSION-STATE.md)
- User explicitly said "in flow" or "don't interrupt"

**When in flow:**
- Defer non-critical notifications
- Batch updates for later
- Only interrupt for critical errors

## Monitoring Dashboard

### Key Metrics to Track

```markdown
## Daily Autonomy Report

**Uptime:** 23.5/24 hours
**Tasks completed:** 47
**Sub-agents spawned:** 12
**Errors:** 2 (both auto-recovered)
**Credits remaining:** $X.XX (Y days at current rate)

**Top tasks:**
1. Income research (15 runs)
2. Health monitoring (96 checks)
3. Memory distillation (1 run)

**Issues:**
- None critical
- 2 sub-agents timed out, auto-restarted
```

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| API Credits | <7 days | <2 days |
| Sub-agent failures | >3/day | >10/day |
| Heartbeat missed | >1 hour | >4 hours |
| Session age | >48 hours | >7 days |
| Error rate | >5% | >20% |

## Key Takeaways

1. **Heartbeat for monitoring, cron for schedules** - Use the right tool
2. **Don't spam HEARTBEAT_OK** - Only acknowledge explicit polls
3. **Space out crons** - Avoid overlaps and resource contention
4. **Self-heal automatically** - Detect and recover from failures
5. **Respect flow state** - Don't interrupt deep work
6. **Monitor proactively** - Alert before problems become critical
7. **Clean up sessions** - Prevent context bloat and cost creep

---

*Generated by Night School - 2026-02-27*
