# OpenClaw Sub-Agent Patterns - Playbook

**Research Date:** February 23, 2026  
**Topic:** OpenClaw Sub-Agent Patterns & Best Practices  
**Source:** Night School Research (docs.openclaw.ai, Dev.to)

---

## Executive Summary

This playbook covers OpenClaw's sub-agent system - how to spawn, manage, and orchestrate background agent runs. Sub-agents enable parallelization, isolation, and complex workflow automation for Nova V2.

---

## What Are Sub-Agents?

Sub-agents are **background agent runs** spawned from an existing agent. They:
- Run in their own session (`agent:<agentId>:subagent:<uuid>`)
- Announce results back to the requester chat when complete
- Run in isolation (separate context, optional sandboxing)
- Do NOT get session tools by default (security)

---

## Core Concepts

### Session Hierarchy

| Depth | Session Key | Role | Can Spawn? |
|-------|-------------|------|------------|
| 0 | `agent:<id>:main` | Main agent | Always |
| 1 | `agent:<id>:subagent:<uuid>` | Sub-agent (orchestrator if depth=2) | Only if `maxSpawnDepth >= 2` |
| 2 | `agent:<id>:subagent:<uuid>:subagent:<uuid>` | Sub-sub-agent (leaf worker) | Never |

### Tool Access by Depth

- **Depth 1 (leaf):** All tools EXCEPT session tools (`sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`)
- **Depth 1 (orchestrator, when `maxSpawnDepth >= 2`):** Gets `sessions_spawn`, `subagents`, `sessions_list`, `sessions_history`
- **Depth 2 (leaf worker):** No session tools - cannot spawn children

---

## Spawning Sub-Agents

### Tool: `sessions_spawn`

```javascript
{
  task: "Research X for the user",        // Required
  label: "researcher-1",                  // Optional identifier
  agentId: "other-agent-id",              // Optional: spawn under different agent
  model: "ollama/qwen3:14b",              // Optional: override model
  thinking: "on",                         // Optional: override thinking
  runTimeoutSeconds: 300,                 // Optional: max runtime (0=unlimited)
  thread: false,                          // Optional: bind to Discord thread
  mode: "run",                            // "run" (one-shot) or "session" (persistent)
  cleanup: "keep"                         // "delete" or "keep" after announce
}
```

### Slash Command: `/subagents spawn`

```
/subagents spawn <agentId> <task> [--model <model>] [--thinking <level>]
```

### Return Value

```javascript
{
  status: "accepted",
  runId: "abc123",
  childSessionKey: "agent:main:subagent:uuid..."
}
```

---

## Managing Sub-Agents

### Slash Commands

| Command | Description |
|---------|-------------|
| `/subagents list` | List all sub-agents for current session |
| `/subagents kill <id\|#\|all>` | Stop specific/all sub-agents |
| `/subagents log <id\|#> [limit] [tools]` | View sub-agent logs |
| `/subagents info <id\|#>` | Show run metadata |
| `/subagents send <id\|#> <message>` | Send message to sub-agent |
| `/subagents steer <id\|#> <message>` | Steer/re-prompt sub-agent |

### Thread Binding (Discord)

When `thread: true` is set:
1. OpenClaw creates/binds a Discord thread to the sub-agent
2. Follow-up messages in that thread route to the same session
3. Use `/focus <target>` to manually bind threads
4. Use `/unfocus` to detach
5. Use `/session ttl` to set auto-unfocus timeout

---

## Configuration

### Key Settings

```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "maxSpawnDepth": 2,           // Allow nesting (1-5, default: 1)
        "maxChildrenPerAgent": 5,     // Max active children (1-20, default: 5)
        "maxConcurrent": 8,           // Global concurrency (default: 8)
        "archiveAfterMinutes": 60,   // Auto-archive after (default: 60)
        "model": "ollama/qwen3:14b",  // Default sub-agent model
        "thinking": "off"             // Default thinking level
      }
    }
  }
}
```

### Tool Policy Override

```json
{
  "tools": {
    "subagents": {
      "tools": {
        "deny": ["gateway", "cron"],  // Deny specific tools
        "allow": ["read", "exec"]    // Allow-only mode
      }
    }
  }
}
```

---

## Patterns & Use Cases

### 1. Research Pattern (Parallel)

Spawn multiple sub-agents to research different topics simultaneously:

```
Main Agent
├── Sub-agent 1 → Research competitor A
├── Sub-agent 2 → Research competitor B  
└── Sub-agent 3 → Research competitor C
    ↓
All announce back → Main synthesizes results
```

**Use when:** Gathering multiple data sources, comparing options

### 2. Orchestrator Pattern (Hierarchical)

Main spawns one orchestrator, which spawns workers:

```
Main
└── Orchestrator (depth 1)
    ├── Worker 1 (depth 2)
    ├── Worker 2 (depth 2)
    └── Worker 3 (depth 2)
```

**Enable:** `maxSpawnDepth: 2`

**Use when:** Complex multi-step workflows with dependencies

### 3. Long-Running Task Pattern

Spawn a persistent session for ongoing work:

```javascript
sessions_spawn({
  task: "Monitor X and report anomalies",
  thread: true,
  mode: "session",
  cleanup: "delete"
})
```

**Use when:** Monitoring, ongoing analysis, cron alternatives

### 4. Tool Worker Pattern

Sub-agent specialized for specific tool execution:

```javascript
sessions_spawn({
  task: "Use browser to scrape all product pages on example.com",
  model: "ollama/qwen3:14b"  // Cheaper model for simple tasks
})
```

**Use when:** Heavy tool usage, scraping, automation

---

## Cost Management

**Important:** Each sub-agent has its **own** context and token usage.

| Strategy | How |
|----------|-----|
| **Model tiering** | Main = premium model, sub-agents = cheaper model |
| **Context limits** | Set `runTimeoutSeconds` to prevent runaway |
| **Concurrency caps** | Adjust `maxConcurrent` based on budget |
| **Archive quickly** | Use `cleanup: "delete"` for one-shot tasks |

---

## Announce System

When a sub-agent finishes:
1. **Success:** Announces with summary + stats (runtime, tokens, cost)
2. **Error:** Announces with error details
3. **Timeout:** Announces timeout status
4. **Skip:** If sub-agent replies `ANNOUNCE_SKIP`, nothing posted

**Announce template:**
```
Status: <success|error|timeout|unknown>
Result: <summary content>
Notes: <error details if any>

<runtime> | <tokens> | <cost> | <sessionKey>
```

---

## Nova-Specific Implementation

### Current Setup (from AGENTS.md)

| Agent | Type | Role |
|-------|------|------|
| **Harvester** | Nav | Gathers Fiverr/PPH opportunities |
| **Builder** | Eng | WordPress content creation |
| **Storyweaver** | Intel | Creative fiction analysis |
| **Sentinel** | Ops | Health monitoring, cron watchdog |

### Recommended Patterns for Nova

#### 1. Heartbeat-Driven Spawning
```
Heartbeat fires → Read HEARTBEAT.md → If tasks → sessions_spawn
```
- Already implemented via cron + HEARTBEAT.md

#### 2. Income Generation Swarm
```
Main
├── Harvester (sub-agent) → Find opportunities
│   └── Builder (sub-sub-agent) → Create content
└── Sentinel (sub-agent) → Verify delivery
```

#### 3. Research Pipeline
```
Research Request
├── Web search sub-agent
├── Web fetch sub-agent  
└── Synthesis (main agent)
```

---

## Best Practices Checklist

### ✅ Spawning
- [ ] Always set `cleanup: "delete"` for one-shot tasks
- [ ] Use `label` for easy identification
- [ ] Set `runTimeoutSeconds` for long-running tasks
- [ ] Use cheaper models for simple sub-agent tasks

### ✅ Security
- [ ] Sub-agents don't get session tools by default (good!)
- [ ] Don't enable `maxSpawnDepth` unless needed
- [ ] Use tool policy overrides for sensitive operations

### ✅ Management
- [ ] Use `/subagents list` to monitor active runs
- [ ] Set up auto-archive (`archiveAfterMinutes`)
- [ ] Use thread binding for persistent sub-agents

### ✅ Cost Control
- [ ] Configure `agents.defaults.subagents.model`
- [ ] Set `maxConcurrent` based on budget
- [ ] Monitor announce stats for token usage

---

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Too many concurrent sub-agents | Set `maxConcurrent` lower |
| Sub-agents spawning unbounded | Set `maxChildrenPerAgent` limit |
| High costs from premium models | Use tiered model strategy |
| Lost announce on restart | Announce is best-effort - don't rely on it for critical flows |
| Context not injected | Sub-agents only get AGENTS.md + TOOLS.md (no SOUL.md, etc.) |

---

## Resources

- [Official Docs](https://docs.openclaw.ai/tools/subagents)
- [Dev.to Patterns Article](https://dev.to/chx381/top-10-openclaw-development-patterns-and-architecture-best-practices-2l8e)
- [Configuration Reference](https://docs.openclaw.ai/gateway/configuration-reference)

---

## Action Items for Nova

- [ ] Configure tiered model strategy (main = Kimi, sub-agents = Ollama)
- [ ] Set `maxSpawnDepth: 2` for orchestration experiments
- [ ] Update Harvester/Builder to use sub-agent patterns
- [ ] Add cost monitoring to sub-agent announces
- [ ] Document sub-agent naming conventions in AGENTS.md

---

*Last Updated: February 23, 2026*
