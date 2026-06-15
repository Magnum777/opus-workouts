# Skill Integration Plan — June 14, 2026
**23 New Skills Installed | Vetting: PASSED**

---

## Immediate Integrations (Tonight/Tomorrow)

### 1. Content Pipeline Quality Gate
**Skills:** `humanizer` + `humanized-writing-editor` + `factual-claim-verifier`
**Where:** Before every WordPress publish, after every TradeBot/EveOnion article draft
**How:**
- Step 1: `humanizer` strips AI signals (em dashes, "delve," inflated language)
- Step 2: `humanized-writing-editor` rewrites stiff text to natural prose
- Step 3: `factual-claim-verifier` checks claims before publishing
**Impact:** Content reads human, fewer corrections needed, higher credibility

### 2. WordPress API Upgrade
**Skill:** `wordpress-api-pro` v3.8.1 (replaces `wordpress-pro` v0.1.0)
**Where:** ContentNova publishing pipeline
**How:**
- Update ContentNova scripts to use production-grade REST API
- Enable: WooCommerce, Elementor, ACF, JetEngine, SEO meta, batch ops
- Multi-site support for aicofounderstack + aitoolalliance + aibusinessinsider
**Impact:** More reliable publishing, richer metadata, batch operations

### 3. Content Research Enhancement
**Skill:** `youtube-transcript-native-node`
**Where:** ContentNova research phase, TradeBot token research
**How:**
- Extract YouTube captions for video summaries
- Research token project videos, AMAs, reviews
- Zero npm dependencies = fast, lightweight
**Impact:** Video content becomes searchable text, faster research

### 4. Browser Automation Redundancy
**Skill:** `browser-auto-plus` v2.0.0 + `playwright-browser-automation`
**Where:** Anywhere `browser-use` or `agent-browser-clawdbot` is used
**How:**
- `browser-auto-plus`: retry logic, error recovery, multi-browser
- `playwright-browser-automation`: Playwright API (more reliable than MCP)
- Use as fallback when primary browser skill fails
**Impact:** Fewer browser automation failures, better reliability

### 5. Proactive Agent Patterns
**Skill:** `proactive-agent` v3.1.0
**Where:** Heartbeat logic, self-improvement cron
**How:**
- WAL protocol for cron safety
- Autonomous cron patterns for background checks
- Compare against our current AGENTS.md / HEARTBEAT.md
**Impact:** More robust background automation, better failure recovery

### 6. Structured Memory
**Skills:** `ontology` v1.0.4 + `cogmem` v2.0.3
**Where:** MEMORY.md enhancement, knowledge graph
**How:**
- `ontology`: Typed knowledge graph for agent memory
- `cogmem`: Bio-inspired memory kernel (Atkinson-Shiffrin model)
- Structured storage for facts, relationships, temporal data
**Impact:** Better memory recall, structured knowledge, less bloat

### 7. Task Management
**Skill:** `task-prism` v4.1.0
**Where:** Complex multi-step projects (TradeBot improvements, UniFi optimization)
**How:**
- Decompose vague requirements into executable tasks
- Skill profiling for team composition
- Dependency mapping
**Impact:** Better project planning, clearer deliverables

### 8. Knowledge Base
**Skill:** `myknowledge` v1.4.89
**Where:** Project documentation, SOPs, research notes
**How:**
- Create knowledge bases for projects
- Manage docs, requirements, personal knowledge
- Searchable structured storage
**Impact:** Centralized knowledge, better onboarding, less context loss

---

## Deferred Integrations (Evaluate Later)

### Email Infrastructure
**Skills:** `agentmail-integration`, `resend-send-native-node`, `cold-email-engine`
**Why deferred:** Need API keys, may replace Iris Gmail workflow
**Decision needed:** Keep Gmail/Iris or migrate to AgentMail/Resend?

### EVM Wallet
**Skill:** `evalanche` v1.11.0
**Why deferred:** EVM (Ethereum), not Solana. We have Solana pipeline.
**Decision needed:** Add EVM support to TradeBot or keep separate?

### Document Generation
**Skill:** `doc-weaver`
**Why deferred:** Overlaps with `word-docx`. Need comparison test.
**Decision needed:** Which produces better Word docs for our use case?

### Desktop Control
**Skill:** `desktop-control`
**Why deferred:** High trust requirement. Can move mouse/keyboard/screen.
**Decision needed:** Specific use case needed before enabling.

### Process Interviewing
**Skill:** `process-interviewer`
**Why deferred:** Interesting but not immediately needed.
**Use case:** Interview Opus before automating/documenting workflows.

---

## Integration Priority Matrix

| Priority | Skill | Effort | Impact | Timeline |
|----------|-------|--------|--------|----------|
| P0 | humanizer | Low | High | Tonight |
| P0 | wordpress-api-pro | Medium | High | Tomorrow |
| P0 | factual-claim-verifier | Low | High | Tonight |
| P1 | youtube-transcript-native-node | Low | Medium | This week |
| P1 | browser-auto-plus | Medium | Medium | This week |
| P1 | proactive-agent | Medium | High | This week |
| P2 | ontology + cogmem | Medium | Medium | Next week |
| P2 | task-prism | Low | Medium | Next week |
| P2 | myknowledge | Low | Medium | Next week |
| P3 | agentmail-integration | High | Low | Evaluate |
| P3 | evalanche | High | Low | Evaluate |
| P3 | doc-weaver | Medium | Medium | Compare vs word-docx |
| P3 | desktop-control | High | ? | On demand |

---

## Integration Checklist

- [ ] Update ContentNova pipeline with humanizer pre-publish
- [ ] Update ContentNova pipeline with factual-claim-verifier pre-publish
- [ ] Swap wordpress-pro → wordpress-api-pro in publishing scripts
- [ ] Add youtube-transcript-native-node to research pipeline
- [ ] Add browser-auto-plus as browser fallback
- [ ] Review proactive-agent WAL patterns vs current heartbeat
- [ ] Test ontology for MEMORY.md structured storage
- [ ] Test task-prism on next complex project
- [ ] Set up myknowledge knowledge base for projects
