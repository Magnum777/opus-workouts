# Nova Swarm Language

## Our Own Terminology (Skippy-Inspired)

### Core Architecture Terms

| Skippy Term | Our Term | Meaning |
|-------------|----------|---------|
| Submind | **Shard** | A specialized fragment for tasks |
| Ghost | **Wisp** | Lightweight agent runs anywhere |
| Beer Can | **Core** | Primary hardware/system |
| Magister | **Prime** | Main Nova instance |

### Functional Types (Like Skippy Uses)

| Term | Role |
|------|------|
| **Comms** | Communications, messages, notifications |
| **Weaps** | Defense, security, protection |
| **Eng** | Build, create, modify |
| **Nav** | Research, finding, discovery |
| **Ops** | Operations, cron, automation |
| **Intel** | Analysis, insights, intelligence |
| **Log** | Memory, organization, filing |

### Descriptive Shard Names (What We Call Them)

These are the friendly names for our active shards:

| Shard Name | Type | Role |
|------------|------|-------|
| **Harvester** | Nav | Gathers opportunities (Fiverr/PPH) |
| **Builder** | Eng | Creates WordPress content |
| **Storyweaver** | Intel | Creative analysis, fiction |
| **Sentinel** | Ops | Monitors health, runs crons |

### Communication

| Term | Meaning |
|------|---------|
| **Howl** | Broadcast to all shards |
| **Whisper** | Direct shard-to-shard |
| **Pulse** | Health/status check |

### Behavior States

| Term | Meaning |
|------|---------|
| **Sleeping** | Inactive, ready |
| **Awake** | Active, working |
| **Lost** | Disconnected |
| **Feral** | Unexpected behavior |

---

## OpenClaw Integration

### How to Run Shards

**Spawn:**
```
/session_spawn task="task" label="shard-name"
```

**Rules:**
1. Max 4-6 active
2. Always cleanup: delete
3. Space out crons
4. One task at a time

### Cron Best Practices (From FREE-SYSTEM)

| Cron | Schedule | Purpose |
|------|---------|---------|
| Session Cleanup | Every 6 hours | Delete sessions >24 hours |
| Health Check | Every 15 min | Detect unresponsive |
| Credit Check | Daily 9 AM | Monitor API balances |
| Memory Distillation | 3 AM | Consolidate to long-term |

### Airlock (Sandbox for Testing)

From AIRLOCK-DESIGN.md:
- **Airlock** - Hardened sandbox for testing new skills
- **Airlock-Nova** - Test agent with no external channels
- **Airlock-Sentinel** - Monitoring sub-mind
- Separate workspace, no access to main credentials

---

## Usage

> "Shard a Nav to research X"
> "Harvester, pulse your status"
> "Which shards are awake?"
