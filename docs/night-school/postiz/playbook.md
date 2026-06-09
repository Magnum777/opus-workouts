# Postiz - Social Media Scheduling Tool

## What is Postiz?

Postiz is an all-in-one, agentic social media scheduling tool with AI capabilities. It's open-source and can be either hosted (SaaS) or self-hosted. The platform enables scheduling, analytics, AI content generation, and automation across 28+ social media platforms.

## Key Features

| Feature | Description |
|---------|-------------|
| **Multi-platform scheduling** | Facebook, Instagram, TikTok, YouTube, Reddit, LinkedIn, Dribbble, Threads, Pinterest, X (Twitter) |
| **AI Content Assistant** | AI agent that helps generate post ideas and content |
| **AI Image Generator** | Built-in Canva-like design tool + AI image generation |
| **Cross-posting** | Post to multiple channels simultaneously |
| **Analytics** | Comprehensive performance tracking |
| **Team Collaboration** | Invite team members, comment, and schedule together |
| **Auto-actions** | Auto-post, auto-like, auto-comment when reaching milestones |
| **Public API** | Full API access for custom integrations |
| **Automation** | Native integrations with n8n, Make.com, Zapier |

## Pricing

| Option | Cost | Details |
|--------|------|---------|
| **Self-hosted (Open Source)** | **Free** | Deploy on your own cloud (Docker/Cloudflare) |
| **Starter** | ~$15/mo | Basic features, limited channels |
| **Standard** | $23/mo | AI features + 5 channels |
| **Agency** | $79/mo | Full features, unlimited channels |

**Note:** 7-day free trial available. No permanent free plan, but self-hosting is free forever.

## Integration with AI Co-Founder Stack

### For V1 (Starter - $25)
Postiz would be a **critical addition** for automating the content pipeline:
- Connect WordPress blog → auto-post to social platforms
- Use AI to generate platform-specific variations
- Schedule content in advance for consistent posting

### Integration Options

1. **API Integration** (Recommended for OpenClaw)
   - Use Postiz Public API to schedule posts
   - Connect from any agent via HTTP requests
   - Can be wrapped as an OpenClaw skill

2. **n8n Integration**
   - Postiz has native n8n node
   - Build workflows: WordPress → Postiz → Social
   - Already on the V2 recommended skills list

3. **Automation Triggers**
   - New blog post → automatically schedule to LinkedIn, X, Reddit
   - Content recycling for older posts

## Implementation Notes

- **Self-hosting recommended** for free unlimited use
- Docker deployment is straightforward
- API key required for integrations
- Supports webhooks for real-time triggers

## Risks / Considerations

- Requires OAuth setup for each social platform
- Self-hosting needs maintenance (updates, etc.)
- API rate limits may apply on hosted plans

## Next Steps

1. Test Postiz API with a free self-hosted instance
2. Create OpenClaw skill wrapper for scheduling posts
3. Build n8n workflow: WordPress webhook → AI reformat → Postiz → publish

---

*Research completed: 2026-02-18*
