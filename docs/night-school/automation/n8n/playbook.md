# n8n Automation - Playbook

## Overview

**n8n** is a fair-code workflow automation platform with native AI capabilities. It combines visual building with custom code, can be self-hosted or cloud-based, and offers 400+ integrations.

- **Website:** https://n8n.io/
- **GitHub:** https://github.com/n8n-io/n8n (175k+ stars)
- **Category:** Automation / AI Workflows
- **Tier:** V2 Pro ($49-79)

---

## Why n8n for AI Co-Founder Stack?

### Key Benefits

1. **Self-Hosted Option** - Full control over data, no cloud dependency
2. **Native AI Support** - Built-in AI agent nodes, LLM integration
3. **400+ Integrations** - Connect to virtually any service
4. **Visual Workflow Builder** - No-code with custom code flexibility
5. **Open Source** - Community edition available

### Use Cases for Nova (AI Co-Founder)

| Use Case | Description |
|----------|-------------|
| Content Pipeline | WordPress → Social Media auto-posting |
| Lead Capture | Form submissions → CRM → Follow-up |
| Research Automation | Perplexity/Tavily → Summarization → Storage |
| Income Tracking | Fiverr/PPH → Spreadsheet → Dashboard |
| Notification Routing | Alerts → Discord/Telegram/Slack |

---

## Pricing (2025)

### Cloud Plans
| Plan | Price | Features |
|------|-------|----------|
| Free | $0 | 1 user, 100 runs/month |
| Pro | €20/mo | Unlimited runs, more users |
| Enterprise | Custom | SSO, RBAC, SLA |

### Self-Hosted (True Cost)
| Component | Cost |
|-----------|------|
| n8n Software | FREE (Community Edition) |
| Server (VPS) | $20-50/mo |
| Cloud Credits (AI) | $50-200/mo |
| **Total** | **$70-250/mo** |

> **Note:** While n8n software is free, production self-hosted environments typically cost $200-500/month when factoring in infrastructure and AI credits.

---

## Integration with OpenClaw

### Possible Skill Wrappers

1. **Workflow Trigger** - Receive webhooks from n8n
2. **Run Workflow** - Trigger n8n workflows via API
3. **AI Agent Node** - Leverage n8n's AI capabilities
4. **Database Ops** - Query results from n8n executions

### Architecture

```
OpenClaw (Nova)
    ↓ webhook/trigger
n8n (Self-hosted or Cloud)
    ↓
400+ Integrations
    ↓
Results back to Nova
```

---

## Self-Hosted AI Starter Kit

n8n offers a **Self-hosted AI Starter Kit** - an open-source template that quickly sets up a local AI environment:
- https://github.com/n8n-io/self-hosted-ai-starter-kit

Combines n8n with curated compatible AI products for building secure, self-hosted AI workflows.

---

## Alternatives

| Tool | Pros | Cons |
|------|------|------|
| **Zapier** | Easier, more integrations | Expensive, cloud-only |
| **IFTTT** | Simple, free tier | Limited for AI |
| **n8n** | Self-hostable, AI-native | Requires setup |

---

## Recommendations for AI Co-Founder Stack

### For V2 (Pro - $49-79)
- **Priority:** Medium-High
- **Value:** High for automation-heavy users
- **Alternative:** Start with Zapier (easier), migrate to n8n for self-hosting

### For V3 (Enterprise - $100+)
- Include n8n as standard automation backbone
- Self-hosted on NAS or dedicated VPS
- Full data sovereignty

---

## Quick Start (Cloud)

1. Sign up at https://n8n.io/
2. Start with free tier
3. Explore AI agent templates
4. Connect OpenClaw via webhooks

---

## Resources

- Docs: https://docs.n8n.io/
- AI Docs: https://n8n.io/ai/
- Community: https://community.n8n.io/
- Reddit: r/n8n

---

*Created: 2026-02-20*
*Topic: Night School - n8n Automation*
