# Nova AI V3 — Q3 2026 Development Roadmap

**Version:** 3.0.0
**Target Release:** September 30, 2026
**Current Phase:** Specification (June 2026)

---

## Sprint 1: Foundation (July 1–15)
**Goal:** Core infrastructure and security layer

### Week 1–2 Deliverables
- [ ] Airlock Security framework implementation
  - Prompt injection detection module
  - Input sanitization pipeline
  - System prompt isolation
- [ ] Sandbox execution environment
  - Docker container specs
  - Network whitelist system
  - Resource limit enforcement
- [ ] Audit trail system
  - SQLite schema design
  - Log ingestion pipeline
  - Query API
- [ ] Approval gate framework
  - Configurable rules engine
  - Human notification system
  - Undo/rollback mechanism

### Success Criteria
- 100% of agent actions logged with full context
- All L1/L2 actions execute without human delay
- L3+ actions trigger appropriate notifications within 5 seconds
- Prompt injection detection catches >95% of known patterns in test suite

### Risks
- **Sandbox performance**: Docker overhead may add 200-500ms per agent call
  - *Mitigation:* Benchmark early, consider gVisor if Docker is too slow
- **Complexity creep**: Security layer could delay other features
  - *Mitigation:* Hard scope limit — no additional security features beyond spec

---

## Sprint 2: Agent System (July 16–31)
**Goal:** Multi-agent orchestration and communication

### Week 3–4 Deliverables
- [ ] Agent Manager implementation
  - Task decomposition algorithm
  - Agent selection logic
  - Priority queue system
- [ ] Specialized agent templates
  - Research agent (web search, data gathering)
  - Writing agent (content creation)
  - Code agent (scripting, deployment)
  - Analysis agent (data analysis, reporting)
  - Communication agent (email, social)
- [ ] Inter-agent messaging protocol
  - Message schema definition
  - Async delivery system
  - Timeout and retry logic
- [ ] Conflict resolution system
  - Consensus algorithm
  - Escalation triggers
  - Human override paths

### Success Criteria
- 5 distinct agent types running simultaneously
- Task decomposition works for 80% of common tasks without human intervention
- Agent conflicts resolve automatically in >70% of cases
- End-to-end task completion (human request → agent output) in <30s for simple tasks

### Risks
- **Agent communication overhead**: Too many messages = slow system
  - *Mitigation:* Batch related messages, set max 10 messages per task
- **Model context limits**: Deep agents may hit token limits with long conversations
  - *Mitigation:* Implement conversation summarization before context limit

---

## Sprint 3: Memory System (August 1–15)
**Goal:** Tiered memory with semantic search

### Week 5–6 Deliverables
- [ ] Short-term memory (Redis)
  - Session context store
  - 4K-8K token window
  - Auto-expiry (session end)
- [ ] Medium-term memory (LanceDB)
  - 30-day rolling window
  - Project-scoped
  - Daily consolidation
- [ ] Long-term memory (LanceDB + JSON)
  - Permanent business knowledge
  - Human curation interface
  - Import from V2
- [ ] Episodic memory (SQLite)
  - Decision history schema
  - Outcome tracking
  - Lesson extraction
- [ ] Semantic search layer
  - Ollama embedding pipeline (nomic-embed-text)
  - Cross-memory-type search
  - Relevance scoring

### Success Criteria
- Memory recall finds relevant context in top-3 results >80% of time
- Consolidation runs daily without data loss
- V2 → V3 migration preserves all existing memory
- Search latency <500ms for typical queries

### Risks
- **LanceDB scalability**: May slow down with >100K entries
  - *Mitigation:* Partition by project, implement pagination
- **Embedding costs**: Local Ollama is free but slower than API
  - *Mitigation:* Accept latency trade-off for privacy; add API fallback option

---

## Sprint 4: Project Tracking (August 16–31)
**Goal:** Active project management with AI accountability

### Week 7–8 Deliverables
- [ ] Project dashboard
  - Active projects list
  - Status indicators
  - Resource allocation view
- [ ] Milestone system
  - Create, assign, track
  - Deadline integration
  - Blocker identification
- [ ] AI accountability framework
  - Agent commitment logging
  - Progress check-ins
  - Automatic escalation
- [ ] Calendar integration
  - Unified deadline view
  - Proactive nudging
  - Conflict detection (overlapping deadlines)

### Success Criteria
- All active projects visible in single dashboard
- Milestones update automatically based on agent activity
- 48-hour advance warning on all deadlines
- Blocker identification within 24 hours of occurrence

### Risks
- **Calendar complexity**: Multiple external calendars (Google, Outlook, Apple)
  - *Mitigation:* Start with Google Calendar only, add others post-launch
- **False urgency**: Too many notifications = notification fatigue
  - *Mitigation:* Batched daily digest + only urgent items as immediate alerts

---

## Sprint 5: Autonomy System (September 1–15)
**Goal:** Graded autonomy with real-world testing

### Week 9–10 Deliverables
- [ ] Autonomy level engine
  - L1-L5 implementation
  - Level transition logic
  - Trust score algorithm
- [ ] Safety invariants
  - Hard limit enforcement
  - Anomaly detection
  - Automatic halt triggers
- [ ] Real-world testing program
  - 5 beta testers (Layered Media clients)
  - 2-week test period per level
  - Feedback collection system
- [ ] Adjustment framework
  - Level fine-tuning based on test results
  - Rule customization per user
  - Override logging

### Success Criteria
- L1-L3 stable with zero safety incidents
- L4 runs overnight without human intervention for >80% of tasks
- L5 self-improvement proposals reviewed by human, not auto-executed
- Human override rate <20% at L3, <5% at L5

### Risks
- **User trust**: Users may not accept L4/L5 even if technically safe
  - *Mitigation:* Default to L2, make escalation opt-in with clear explanations
- **Unexpected edge cases**: Real-world usage reveals gaps not caught in testing
  - *Mitigation:* 24-hour observation period for any new L4/L5 user

---

## Sprint 6: Polish & Launch (September 16–30)
**Goal:** Production readiness and V3 launch

### Week 11–12 Deliverables
- [ ] Documentation
  - User guide (autonomy levels explained)
  - API reference
  - Migration guide from V2
- [ ] Performance optimization
  - Agent response time <5s (L1-2), <30s (L3-5)
  - Memory search <500ms
  - Audit log query <2s
- [ ] Monitoring & alerting
  - Agent health dashboard
  - Error rate tracking
  - Cost monitoring
- [ ] Launch preparation
  - Pricing page update ($100+)
  - Email announcement to V2 users
  - Product Hunt launch coordination

### Success Criteria
- 99.5% uptime for core services
- All critical paths tested with automated integration tests
- 50+ beta users migrated without data loss
- Launch day: zero critical bugs

---

## Resource Requirements

### Development
- 1 lead developer (full-time, August–September)
- 1 ML/AI engineer (part-time, July–September)
- 1 security reviewer (part-time, July–August)

### Infrastructure
- Development: $100/month (GPU instance for model testing)
- Staging: $50/month
- Production (launch): $200-500/month depending on user count

### External Services
- LanceDB Cloud: $29/month (production vector store)
- Optional: Helius RPC ($49/month) for Solana integrations
- Optional: SendGrid ($20/month) for notification emails

**Total estimated Q3 cost: $2,000-3,000**

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Security vulnerability in Airlock | Low | Critical | External audit, bug bounty, gradual rollout |
| Agent conflicts cause bad decisions | Medium | High | Human-in-the-loop for L4+, consensus algo |
| Memory system too slow at scale | Medium | Medium | Partitioning, API fallback, benchmark early |
| Users don't trust autonomy levels | Medium | High | Default L2, opt-in escalation, clear explanations |
| V2 → V3 migration data loss | Low | Critical | Backup-first migration, rollback capability |
| Ollama model updates break agents | Medium | Medium | Version pinning, test suite, API fallback |
| Scope creep delays launch | High | Medium | Hard sprint boundaries, weekly scope review |

---

## Post-Launch (Q4 2026)

- **October:** Monitor adoption, collect feedback, fix critical bugs
- **November:** First L5 users (invite-only), self-improvement validation
- **December:** V3.1 release (performance improvements, new agent types)

---

*Roadmap version: 1.0*
*Last updated: 2026-06-01*
*Next review: July 1, 2026 (start of Sprint 1)*
