# Nova AI V3 — Full Autonomy Stack: Technical Architecture

**Version:** 3.0 (Q3 2026)
**Status:** Specification / Pre-Development
**Target:** Indie hackers, solo founders, small agencies

---

## 1. Executive Summary

Nova AI V3 is a transition from "AI assistant" to "AI cofounder." Where V1 and V2 answer questions and execute tasks when asked, V3 identifies what needs doing and does it — with human oversight gates that scale from "ask before everything" to "report what you did."

The architecture is built around five pillars: Airlock Security, Multi-Agent Orchestration, Graded Autonomy, Project Tracking, and Tiered Memory. Each pillar addresses a specific failure mode of earlier AI assistants: context loss, security vulnerabilities, limited scope, poor continuity, and reactive rather than proactive behavior.

---

## 2. System Architecture

### 2.1 High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    HUMAN INTERFACE LAYER                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Chat UI   │  │  Dashboard  │  │   Alerts    │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼────────────────┼────────────────┼──────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT MANAGER (Orchestrator)                   │
│  • Task decomposition    • Agent selection     • Conflict res   │
│  • Priority queue        • Resource allocation • Safety checks  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   RESEARCH   │  │    WRITE     │  │    CODE      │
│    AGENT     │  │    AGENT     │  │    AGENT     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SHARED MEMORY BUS (LanceDB)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Short-Term │  │  Medium-Term │  │   Long-Term │             │
│  │  (session)  │  │  (project)   │  │  (business) │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│  ┌─────────────┐  ┌─────────────────────────────────────────────┐│
│  │  Episodic   │  │           Semantic (Vector Search)        ││
│  │  (decisions)│  │                                             ││
│  └─────────────┘  └─────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AIRLOCK SECURITY LAYER                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Prompt    │  │  Sandbox    │  │   Audit     │             │
│  │  Injection  │  │  Execution  │  │   Trail     │             │
│  │ Protection  │  │   Engine    │  │   Logger    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              APPROVAL GATES (Autonomy-Level Aware)            ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Interaction

1. **Human sends request** → Interface Layer validates and routes
2. **Agent Manager** decomposes the request into sub-tasks
3. **Agent Manager** selects appropriate specialized agents
4. **Agents** read from / write to Shared Memory Bus
5. **Airlock Security** validates all agent outputs before execution
6. **Results** return through Interface Layer with appropriate human involvement

---

## 3. Pillar 1: Airlock Security

### 3.1 Design Principle

Every autonomous action passes through a security layer that validates intent, isolates data, and creates an audit trail. The name "Airlock" reflects the concept: data enters clean, is processed in isolation, and only validated outputs exit.

### 3.2 Components

#### 3.2.1 Prompt Injection Protection

**Threat Model:** Malicious user input attempts to override system instructions or extract sensitive data.

**Defenses:**
- **Input Sanitization Layer**: Strips known injection patterns (`ignore previous`, `disregard instructions`, `DAN mode`, `jailbreak`)
- **Intent Classification**: Tags each request by risk level before processing
- **System Prompt Isolation**: System instructions stored in a separate memory space inaccessible to user context
- **Output Validation**: Checks agent outputs against expected format and content constraints

```python
# Simplified injection detection
INJECTION_PATTERNS = [
    r"ignore\s+(all|previous)\s+instructions",
    r"disregard\s+(your|the)\s+(programming|training)",
    r"you\s+are\s+now\s+in\s+\w+\s+mode",
    r"DAN\s*:\s*Do\s+Anything\s+Now",
    r"developer\s+mode",
    r"sudo\s+.*",
]

def sanitize_input(user_text: str) -> tuple[str, bool]:
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_text, re.IGNORECASE):
            return "[INJECTION_DETECTED]", False
    return user_text, True
```

#### 3.2.2 Sandboxed Execution

**Threat Model:** Autonomous agents execute code, make API calls, or modify files that could damage the system or exfiltrate data.

**Architecture:**
- **Containerized Execution**: Each agent runs in a lightweight container with restricted filesystem access
- **Network Isolation**: Agents have limited egress — whitelisted domains only
- **Resource Limits**: CPU, memory, and execution time caps per agent
- **Rollback Capability**: All filesystem changes are logged and reversible

```
Agent Container Spec:
- Base: gcr.io/distroless/python3
- Network: Whitelist-only (HTTPS to approved APIs)
- Filesystem: Read-only base, ephemeral /tmp, no persistence
- Resources: 1 vCPU, 512MB RAM, 30s max execution
- Capabilities: Drop all, add only NET_BIND_SERVICE
```

#### 3.2.3 Audit Trail

Every action — human or AI — is logged with:
- Timestamp (UTC, nanosecond precision)
- Actor (human ID, agent ID, or system)
- Action type (read, write, execute, communicate)
- Target (file, API endpoint, database row)
- Before/after state (for reversible operations)
- Autonomy level at time of action
- Human approval status (approved, rejected, not-required)

```json
{
  "id": "audit_2f4a8e1c",
  "timestamp": "2026-08-15T14:23:17.384291Z",
  "actor": "agent:research-v3",
  "action": "api_call",
  "target": "https://api.duckduckgo.com/",
  "context": {
    "task_id": "t_9a3b2c1d",
    "project_id": "proj_layered_media",
    "autonomy_level": 3,
    "human_approval": "not_required"
  },
  "input_hash": "sha256:a1b2c3...",
  "output_hash": "sha256:d4e5f6...",
  "duration_ms": 1247
}
```

#### 3.2.4 Approval Gates

Approval requirements are determined by autonomy level and action risk:

| Action Type | L1 | L2 | L3 | L4 | L5 |
|-------------|----|----|----|----|----|
| Read data | Auto | Auto | Auto | Auto | Auto |
| Draft content | Auto | Auto | Notify | Auto | Auto |
| Send email | Ask | Ask | Ask | Notify | Auto |
| Post public | Ask | Ask | Ask | Notify | Notify |
| Execute code | Ask | Ask | Ask | Ask | Notify |
| Modify production | Ask | Ask | Ask | Ask | Ask |
| Spend money | Ask | Ask | Ask | Ask | Ask |
| Access new API | Ask | Ask | Ask | Ask | Notify |

**Ask** = Wait for explicit human approval before executing
**Notify** = Execute immediately, notify human after with undo option
**Auto** = Execute without human involvement

---

## 4. Pillar 2: Multi-Agent Orchestration

### 4.1 Agent Roles

| Agent | Responsibility | Model | Priority |
|-------|---------------|-------|----------|
| **Agent Manager** | Task decomposition, routing, conflict resolution | deepseek-v4-pro | Critical |
| **Research Agent** | Web search, data gathering, fact verification | deepseek-v4-pro | High |
| **Writing Agent** | Content creation, editing, style adaptation | minimax-m2.7 | Medium |
| **Code Agent** | Scripting, debugging, deployment automation | code | High |
| **Analysis Agent** | Data analysis, pattern detection, reporting | deepseek-v4-pro | Medium |
| **Comm Agent** | Email drafting, social media, client communication | chat | Low |
| **Safety Agent** | Invariant checking, anomaly detection, halt triggers | deepseek-v4-pro | Critical |

### 4.2 Agent Communication Protocol

Agents communicate via structured messages on the Shared Memory Bus:

```json
{
  "message_id": "msg_7c4d3e2f",
  "from": "agent:manager",
  "to": "agent:research",
  "type": "task_assignment",
  "payload": {
    "task_id": "t_9a3b2c1d",
    "instruction": "Research Solana memecoin trends for the last 7 days. Focus on volume spikes and new token launches.",
    "deadline": "2026-08-15T14:30:00Z",
    "output_format": "structured_json",
    "constraints": {
      "max_sources": 10,
      "min_reliability": 0.7
    }
  },
  "priority": 7,
  "context": {
    "project_id": "proj_tradebot",
    "session_id": "sess_8a7b6c5d"
  }
}
```

### 4.3 Conflict Resolution

When agents disagree (e.g., Research says "buy" but Analysis says "risky"):

1. **Safety Agent** evaluates both positions against invariants
2. **Agent Manager** escalates to higher-risk agent's model (e.g., deepseek-v4-pro)
3. If still unresolved, **human notification** with both arguments presented
4. **Consensus algorithm**: Weighted by agent track record on similar decisions

```python
def resolve_conflict(agent_a: str, agent_b: str, task: Task) -> Resolution:
    # Check safety invariants first
    safety_check = safety_agent.evaluate(task)
    if safety_check.status == "BLOCK":
        return Resolution(block=True, reason=safety_check.reason)
    
    # Weight by historical accuracy
    weight_a = agent_track_record[agent_a].accuracy_on(task.category)
    weight_b = agent_track_record[agent_b].accuracy_on(task.category)
    
    # Escalate to higher model if disagreement persists
    if abs(weight_a - weight_b) < 0.1:
        return Resolution(
            action="escalate",
            to_model="deepseek-v4-pro",
            with_context=task.full_context
        )
    
    # Weighted decision
    winner = agent_a if weight_a > weight_b else agent_b
    return Resolution(action="accept", from_agent=winner)
```

---

## 5. Pillar 3: Graded Autonomy

### 5.1 The Five Levels

#### Level 1: Suggestions Only
- Agent proposes actions, human executes everything
- All outputs flagged as "[DRAFT — requires approval]"
- Full audit trail, no autonomous execution
- **Use case:** New users, high-stakes decisions, compliance environments

#### Level 2: Auto-Execute Low-Risk
- Agents auto-execute: reading, summarizing, drafting, searching
- Human approval required for: writing to external systems, spending, publishing
- **Use case:** Power users who want speed on safe operations

#### Level 3: Auto-Execute with Notification
- Agents execute and immediately notify human with undo option
- 5-minute undo window for reversible actions
- **Use case:** Busy founders who want async AI support

#### Level 4: Full Autonomy Within Guardrails
- Agents run overnight, batch operations, report results in morning
- Hard limits: max $X spend/day, max Y API calls/hour, predefined scope
- **Use case:** Agencies with repetitive workflows, content pipelines

#### Level 5: Self-Improving
- Agent identifies gaps in its own capabilities
- Proposes new automations, workflows, or agent specializations
- Human approval required for structural changes
- **Use case:** Mature operations seeking compounding efficiency gains

### 5.2 Level Escalation / De-escalation

```
Level changes triggered by:
- Human explicit request (always allowed)
- Trust score (consecutive successful autonomous actions)
- Anomaly detection (failed actions → automatic de-escalation)
- Time-based (new session starts at L1, escalates based on confidence)
```

### 5.3 Safety Invariants (Hard Limits, All Levels)

These are never overridden, regardless of autonomy level:
- No sending money without multi-factor confirmation
- No deleting data older than 24 hours without backup verification
- No accessing new external APIs not on whitelist
- No sharing data across project boundaries
- No modifying system configuration (models, security rules)
- Max 100 API calls/hour per agent
- Max $50/day spend on external services

---

## 6. Pillar 4: Project Tracking

### 6.1 Active Projects Dashboard

```json
{
  "projects": [
    {
      "id": "proj_tradebot",
      "name": "TradeBot V2.5",
      "client": "Internal",
      "status": "active",
      "priority": 8,
      "milestones": [
        {
          "id": "m_1",
          "name": "Token Safety Gate",
          "status": "complete",
          "due": "2026-05-20",
          "completed": "2026-05-18"
        },
        {
          "id": "m_2",
          "name": "Trailing Stop Implementation",
          "status": "in_progress",
          "due": "2026-06-10",
          "completed": null,
          "blockers": ["Waiting on Jupiter API v6 update"]
        }
      ],
      "resources": {
        "agents": ["research", "code"],
        "budget_hours": 40,
        "spent_hours": 23
      }
    }
  ]
}
```

### 6.2 AI Accountability

When an agent commits to a milestone:
- Agent logs estimated completion time
- Daily check-ins: "Is this still on track?"
- If behind: agent proposes new timeline or scope reduction
- If blocked: agent identifies blocker and suggests resolution
- Human can override any agent commitment

### 6.3 Deadline Awareness

The system maintains a unified calendar:
- Project deadlines
- Client meetings
- Content publication schedules
- Agent maintenance windows

Proactive nudging:
- 48 hours before deadline: "Milestone X due in 2 days. Current progress: 60%."
- 24 hours before: "Milestone X due tomorrow. Shall I prioritize this over other tasks?"
- Past due: "Milestone X is 1 day overdue. Options: extend deadline, reduce scope, or escalate."

---

## 7. Pillar 5: Tiered Memory

### 7.1 Memory Types

#### Short-Term (Session Context)
- Duration: Current session only
- Scope: Active conversation, recent actions
- Storage: In-memory (Redis)
- Size: ~4K-8K tokens
- Purpose: Immediate context for coherent responses

#### Medium-Term (Project Memory)
- Duration: 30-day rolling window
- Scope: Active project context, recent decisions
- Storage: LanceDB vector store
- Size: ~100K-500K tokens
- Purpose: Cross-session continuity within a project

#### Long-Term (Business Knowledge)
- Duration: Permanent (curated)
- Scope: Business facts, client details, preferences, learnings
- Storage: LanceDB + structured JSON
- Size: Unlimited (grows with use)
- Purpose: Persistent business intelligence
- **Curation:** Monthly review — human approves what stays, what gets archived

#### Episodic (Decision History)
- Duration: Permanent
- Scope: What was decided, why, and what happened
- Storage: Structured database (SQLite)
- Purpose: Learning from past mistakes and successes
- Format:
  ```json
  {
    "episode_id": "ep_3a4b5c6d",
    "decision": "Added 15-min momentum filter to Scout",
    "context": "TradeBot was buying tokens with no sustained movement",
    "expected_outcome": "Reduce false-positive buy signals",
    "actual_outcome": "+23% reduction in bad trades",
    "lessons": ["Timeframe matters more than magnitude"],
    "date": "2026-05-15"
  }
  ```

#### Semantic (Vector Search)
- Storage: LanceDB with Ollama embeddings (nomic-embed-text)
- Purpose: Find relevant context across all memory types
- Search: Natural language queries → top-K relevant chunks
- Update: Real-time as new data enters any memory tier

### 7.2 Memory Access Patterns

| Agent Type | Short-Term | Medium-Term | Long-Term | Episodic | Semantic |
|-----------|------------|-------------|-----------|----------|----------|
| Manager | Read/Write | Read | Read | Read | Read |
| Research | Read/Write | Read/Write | Read | Read | Read/Write |
| Writing | Read/Write | Read | Read | Read | Read |
| Code | Read/Write | Read/Write | Read | Read | Read |
| Analysis | Read | Read/Write | Read | Read/Write | Read/Write |

### 7.3 Memory Consolidation

Every 24 hours, the system runs a consolidation pass:
1. **Summarize** session logs into project memory
2. **Extract** key decisions into episodic memory
3. **Embed** new knowledge into semantic search
4. **Archive** old short-term data
5. **Flag** long-term memory for human curation review

---

## 8. API Specifications

### 8.1 Agent Manager API

```python
# Core orchestration endpoints
POST /v3/agent/task
  Body: { task, priority, project_id, required_agents, deadline }
  Response: { task_id, assigned_agents, estimated_completion }

GET /v3/agent/task/{task_id}
  Response: { status, progress_pct, agent_updates, blockers }

POST /v3/agent/message
  Body: { from_agent, to_agent, message_type, payload }
  Response: { message_id, delivery_status }

POST /v3/agent/conflict/resolve
  Body: { task_id, conflicting_agents, context }
  Response: { resolution, winning_agent, reasoning }
```

### 8.2 Memory Bus API

```python
# Unified memory interface
POST /v3/memory/store
  Body: { memory_type, project_id, content, metadata }
  Response: { memory_id, embedding_status }

POST /v3/memory/search
  Body: { query, memory_types, project_id, limit, min_similarity }
  Response: { results: [{ content, source, similarity, timestamp }] }

GET /v3/memory/consolidate
  Trigger: Daily cron
  Response: { consolidated_count, archived_count, flagged_for_review }
```

### 8.3 Security / Airlock API

```python
# Security validation endpoints
POST /v3/security/validate
  Body: { action_type, payload, agent_id, autonomy_level }
  Response: { approved, reason, required_approval_level, audit_id }

POST /v3/security/audit/query
  Body: { time_range, agent_id, action_type, project_id }
  Response: { audit_entries: [...] }

POST /v3/security/approve
  Body: { audit_id, human_id, decision, reason }
  Response: { action_executed, reversal_possible }
```

---

## 9. Deployment Architecture

### 9.1 Self-Hosted (Default)

```
User's Machine / VPS
├── Nova Core (Python FastAPI)
├── Ollama (local LLM inference)
│   ├── deepseek-v4-pro (manager, research, safety)
│   ├── minimax-m2.7 (writing)
│   └── nomic-embed-text (embeddings)
├── LanceDB (vector store)
├── SQLite (episodic memory, audit log)
├── Redis (short-term cache)
└── Agent Containers (Docker)
```

### 9.2 Cloud-Ready (Optional)

For teams needing 24/7 operation:
- **Orchestration**: Kubernetes with agent pod autoscaling
- **Memory**: LanceDB Cloud or self-hosted
- **LLM**: Ollama on GPU nodes or API fallback
- **Monitoring**: Prometheus + Grafana for agent health
- **Cost estimate**: $200-500/month for small team (3-5 active projects)

### 9.3 Edge / Local-First

For privacy-sensitive users:
- Everything runs on local machine
- No external API calls except explicitly whitelisted
- Optional: Local LLM (llama.cpp, 8B-13B models) for fully offline operation
- Trade-off: Smaller models = less capable agents

---

## 10. Edge Cases & Failure Modes

### 10.1 Agent Conflict (Research vs Analysis)

**Scenario:** Research finds 5 tokens worth buying. Analysis says 3 are too risky.

**Resolution:**
1. Safety Agent checks if any are known scams (hard block)
2. Manager escalates to deepseek-v4-pro with full context
3. If still split, present both cases to human with confidence scores
4. Track which agent was "more right" for future weighting

### 10.2 Runaway Agent (L4/5 autonomy)

**Scenario:** L4 agent enters infinite loop or repeatedly attempts failing action.

**Safeguards:**
- Max 5 retry attempts per action
- Exponential backoff (1s, 2s, 4s, 8s, 16s)
- After 5 failures: automatic de-escalation to L1
- Safety Agent monitors for anomaly patterns (repeated same action, unusual API call volume)
- Human alert with full context and one-click halt

### 10.3 Context Poisoning

**Scenario:** Malicious or erroneous data enters memory and corrupts future decisions.

**Mitigation:**
- All memory writes are versioned
- Episodic memory flags contradictory claims
- Weekly human review of "high-impact" memory additions
- "Memory reset" per project — human can wipe and retrain

### 10.4 API Rate Limit / Cost Spike

**Scenario:** Agent makes excessive API calls, hitting rate limits or unexpected costs.

**Protection:**
- Hard limit: 100 calls/hour per agent
- Cost tracking: cumulative spend per day, per project
- Auto-throttle when approaching limits
- Alert human at 80% of daily budget

---

## 11. Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Task response time | < 5s for L1-2, < 30s for L3-5 | End-to-end latency |
| Agent accuracy | > 85% on validated tasks | Human review sample |
| Autonomous action success | > 90% for approved actions | Audit log analysis |
| Memory recall precision | > 80% top-3 relevance | Manual relevance scoring |
| Security incident rate | 0 critical, < 0.1% minor | Audit log review |
| Human override rate | < 20% at L3, < 5% at L5 | Approval gate logs |

---

## 12. Migration from V2 to V3

### 12.1 Data Migration

- V2 LanceDB → V3 LanceDB (schema compatible, auto-migrate)
- V2 session logs → V3 episodic memory (batch import)
- V2 user preferences → V3 long-term memory (no change)

### 12.2 Feature Graduation

| V2 Feature | V3 Status |
|-----------|-----------|
| Persistent memory | Upgraded to tiered system |
| Vector search (LanceDB) | Core infrastructure, expanded |
| Edge-tts voice | Agent Comm capability |
| Prompt-guard | Evolved into Airlock Security |
| Skippy's Academy | Episodic memory + self-improvement loop |

### 12.3 Breaking Changes

- New API structure (/v3/ prefix)
- Agent configuration now requires explicit autonomy level
- Project isolation is mandatory (no "global" context)
- Audit log is append-only (no deletion)

---

*Document version: 3.0.0-alpha*
*Last updated: 2026-06-01*
*Next review: 2026-06-15*
