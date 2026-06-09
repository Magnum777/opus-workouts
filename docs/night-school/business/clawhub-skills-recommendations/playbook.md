# ClawHub Skills Recommendations for AI Co-Founder Stack

## Executive Summary

This playbook outlines recommended third-party integrations (skills) for the Nova AI Co-Founder product, organized by product tier (V1, V2, V3). These skills transform Nova from a chat assistant into a complete business co-founder.

---

## Priority Quick Wins

| Priority | Skill | Use Case | Complexity |
|----------|-------|----------|------------|
| 1 | **Postiz** | Auto-post blog → social (28+ platforms) | Medium |
| 2 | **Stripe** | Invoicing/payments | Medium |
| 3 | **LinkedIn** | Professional content automation | Medium |
| 4 | **ElevenLabs** | Voice synthesis (V2) | Low |
| 5 | **Mem0** | Persistent memory (V2) | Low |

---

## V1: Starter Tier ($25)

### Already Available (Built-in)
- **Discord** - Chat integration
- **Notion** - Brain/knowledge management  
- **GitHub** - Version control
- **Slack** - Team communications
- **Weather** - Context awareness

### Recommended for V1

#### 1. Postiz - Social Media Scheduling ⭐ TOP PRIORITY
**What it does:** All-in-one agentic social media scheduling tool
- Schedule posts to 28+ platforms (X, LinkedIn, Reddit, Bluesky, etc.)
- AI-powered post ideation and content generation
- Built-in Canva-like AI image generator
- Auto-engagement (auto-like, auto-comment at milestones)
- Analytics dashboard
- Public API for automation
- n8n and Make.com integrations

**Pricing:** 
- Free tier available
- 7-day trial for $0
- Self-hosting option (avoid monthly fees)

**Why it matters:** Complete social media automation in one skill. Perfect for auto-blogging workflow: WordPress post → AI Polish → Postiz → 28 platforms.

**Implementation:** Wrap existing Postiz API (docs.postiz.com/public-api)

#### 2. WordPress
**What it does:** Already have XML-RPC capability, wrap as formal skill
- Create/update/publish posts
- Manage media library
- Handle comments

**Status:** Low priority - core functionality exists

#### 3. RSS Reader
**What it does:** Monitor industry feeds for content ideas
- Track competitor blogs
- News aggregation
- Content inspiration pipeline

#### 4. Stripe - Payments ⭐ HIGH VALUE
**What it does:** Payment processing and invoicing
- Send invoices
- Process payments
- Subscription management
- Payment webhooks

**Pricing:** 2.9% + $0.30 per transaction (standard)

**Why it matters:** Complete income stack with Gumroad. Nova can generate invoices and track payments.

#### 5. LinkedIn Automation
**What it does:** Professional networking automation
- Post scheduling
- Connection requests
- Profile optimization suggestions

**Status:** Medium priority - consider Postiz covers most

---

## V2: Pro Tier ($49-79)

### Voice & Communication

#### 6. ElevenLabs - Voice Synthesis ⭐ ALREADY HAVE KEY
**What it does:** State-of-the-art AI voice synthesis
- Text-to-speech with lifelike voices
- Voice cloning (with consent)
- Multi-language support
- Low-latency API
- Speech to transcription

**Pricing:** Credit-based system
- Character limit varies by tier
- v3 (alpha) at 80% fewer credits until June 2025

**Why it matters:** Transforms Nova from text-only to voice companion. User already has API key.

**Implementation:** User has key - integrate with OpenClaw TTS

#### 7. Voice Call (Phone)
**What it does:** Handle incoming/outgoing phone calls
- AI voice receptionist
- Call routing
- Voicemail transcription

**Status:** Future consideration

#### 8. Zoom Integration
**What it does:** Meeting automation
- Schedule meetings
- Generate summaries
- Action items extraction

---

### Automation

#### 9. n8n - Self-Hosted Automation ⭐ HIGH VALUE
**What it does:** Connect 900+ services via workflows
- Self-hosted (free) or cloud ($20+/month)
- Open source
- Extensive integrations
- Runs on NAS/server

**Pricing:**
- Self-hosted: Free (but infrastructure ~$300-500/month for production)
- Cloud: $20/month (2,500 executions), $50/month (10,000 executions)

**Why it matters:** Core infrastructure for connecting all skills. Perfect for Nova's automation needs.

**Implementation:** Can be wrapped as skill for common workflows

#### 10. Zapier
**What it does:** Cloud workflow automation
- 6,000+ app integrations
- No-code builder
- Cloud-hosted

**Pricing:** Free tier available, paid from $20/month

**Status:** Alternative to n8n, easier but recurring cost

#### 11. IFTTT
**What it does:** Simple applets for consumer automation
- 900+ services
- Simple triggers/actions

**Status:** Lower priority - n8n more powerful

---

### Research & Intelligence

#### 12. Perplexity - AI Research
**What it does:** AI-powered search and research
- Web research with citations
- Source synthesis
- Topic deep dives

**Status:** Could wrap existing Brave Search (already configured)

#### 13. Tavily - Deep Research
**What it does:** Specialized AI research API
- Academic and web research
- Structured outputs
- Multi-source synthesis

---

## V3: Enterprise Tier ($100+)

### Security & Monitoring

#### 14. Healthcheck - System Monitoring ⭐ ALREADY HAVE SKILL
**What it does:** Security hardening and risk-tolerance configuration
- Host security audits
- Firewall/SSH/update hardening
- Periodic health checks

**Status:** Available as OpenClaw skill

#### 15. Uptime Kuma
**What it does:** Website monitoring
- Self-hosted (free)
- Status pages
- Alert notifications

**Implementation:** Can run on NAS

#### 16. Sentinel - Security Alerting
**What it does:** Security monitoring and alerts
- Anomaly detection
- Alert routing
- Compliance reporting

---

### Advanced AI

#### 17. Mem0 - Persistent Memory ⭐ CRITICAL FOR V2
**What it does:** Intelligent memory layer for AI agents
- Compresses chat history into optimized memory
- 90% lower token usage vs full context
- 91% reduced latency
- User preference learning
- Cross-session continuity

**Funding:** $24M Series A (YC, Peak XV, Basis Set)

**Why it matters:** KEY differentiator for V2. Solves the "forgetfulness" problem that makes AI assistants feel dumb.

**Implementation:** Install via `npm install mem0ai` or cloud API

#### 18. Vector DB - Knowledge Retrieval
**What it does:** Semantic search over documents
- Pinecone, Weaviate, Qdrant options
- Semantic caching
- RAG pipelines

---

## Implementation Roadmap

### Phase 1: V1 Skills (This Week)
1. **Postiz** - High impact, social media automation
2. **Stripe** - Complete income stack
3. Document existing capabilities

### Phase 2: V2 Skills (Next Sprint)
1. **ElevenLabs** - Voice integration (key ready!)
2. **Mem0** - Memory layer (critical)
3. **n8n** - Automation infrastructure

### Phase 3: V3 Skills (Future)
1. Security/hardening
2. Advanced monitoring
3. Enterprise features

---

## Skill Integration Complexity

| Skill | API Type | Wrapper Effort | Priority |
|-------|----------|----------------|----------|
| Postiz | REST | Medium | 1 |
| Stripe | REST | Medium | 2 |
| ElevenLabs | REST | Low | 4 |
| Mem0 | Python/Cloud | Low | 5 |
| n8n | REST | Medium | 3 |
| LinkedIn | Graph API | High | 3 |

---

## Security Notes

- Only install skills from trusted sources
- Recent malware issues reported in prompt injection attempts
- Keep API keys in secure credential storage
- Use environment variables for secrets

---

## Sources

- Postiz: postiz.com
- ElevenLabs:icing
- Mem elevenlabs.io/pr0: mem0.ai, GitHub mem0ai/mem0
- n8n: n8n.io/pricing
- TechCrunch: Mem0 Series A coverage

---

*Last Updated: 2026-02-18*
*Topic: ClawHub Skills Recommendations*
*Status: Research Complete*
