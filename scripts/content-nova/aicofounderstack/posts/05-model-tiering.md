# Model Tiering: Why I Run 3 AI Models Instead of 1 (And Save 70%)

**Author:** James "Opus" Henderson  
**Date:** June 2026  
**Tags:** AI, Cost Optimization, Ollama, OpenClaw, Local LLMs

---

## The Problem

Running everything on a premium cloud model (Kimi K2.5, GPT-4, Claude 3.5) is expensive. For a solo operator with multiple daily automations, costs stack fast.

Old setup: Everything → Kimi K2.5  
Result: ~$40-60/month in API calls for research, writing, analysis, and code generation.

New setup: Route by task complexity  
Result: ~$12-15/month. Same output quality. Faster for simple tasks.

## The Three-Tier System

| Tier | Model | Cost | Use Case | Speed |
|------|-------|------|----------|-------|
| **Fast/Free** | Qwen3:14b (Ollama local) | $0 | Classification, summaries, simple drafting | Instant |
| **Balanced** | DeepSeek V3.2 (cloud) | ~$0.001/1K tokens | Content generation, research, code | 2-3s |
| **Premium** | Kimi K2.5 (cloud) | ~$0.003/1K tokens | Orchestration, complex reasoning, final polish | 5-8s |

## What Each Tier Actually Does

**Fast Tier (Qwen3:14b)**
- Spam email classification
- Topic tagging for articles
- Simple sentiment analysis
- Cron job status summaries
- Pre-filtering research results

**Balanced Tier (DeepSeek V3.2)**
- First drafts of blog posts
- Web research synthesis
- Code generation (Python scripts)
- Trading signal analysis
- Email response drafting

**Premium Tier (Kimi K2.5)**
- Final edit of published content
- Complex multi-step decisions
- Strategy recommendations
- Error analysis and debugging
- Orchestrator coordination

## Real Routing Examples

**TradeBot pipeline:**
1. Scout checks 20 tokens → Qwen3 classifies "worth researching" vs "ignore" (free)
2. Researcher analyzes 5 tokens → DeepSeek evaluates momentum and risk ($0.002)
3. Orchestrator decides to buy 1 token → Kimi confirms the decision ($0.005)
**Total:** ~$0.007 per trade cycle vs. $0.025 if everything ran on Kimi

**Content Nova pipeline:**
1. Research 10 topics → Qwen3 picks the best 3 (free)
2. Write 3 article drafts → DeepSeek generates 1,200 words each ($0.04)
3. Final edit and SEO optimization → Kimi polishes ($0.02)
**Total:** ~$0.06 per article vs. $0.18 if everything ran on Kimi

## The Hardware

The local tier runs on my desktop:
- AMD Ryzen 9800X3D (16 cores)
- Radeon 9070 XT (32 GB VRAM)
- 32 GB system RAM
- Windows 10

Qwen3:14b loads in ~4 seconds, processes 1K tokens in ~2 seconds. For tasks that don't need creative reasoning, it's indistinguishable from cloud models.

## When Local Models Fail

**Hallucinations on factual tasks.** Qwen3:14b occasionally generates fake URLs or misattributes quotes. DeepSeek and Kimi are more reliable for anything that needs verification.

**Code quality drops on complex logic.** For multi-file projects or API integrations, Kimi produces cleaner, more maintainable code. Qwen3 is fine for single-file scripts.

**Context window limits.** Qwen3:14b has 32K context — enough for most tasks. But for analyzing 50+ page documents, Kimi's 200K context wins.

## The Cost Breakdown (Monthly)

| Category | Old (All Kimi) | New (Tiered) | Savings |
|----------|----------------|--------------|---------|
| Content generation | $25 | $8 | 68% |
| Trading research | $15 | $4 | 73% |
| Email/classification | $5 | $0 | 100% |
| Code/debugging | $10 | $3 | 70% |
| **Total** | **$55** | **$15** | **73%** |

That's $480/year in savings — enough to pay for the GPU upgrade that makes the local tier possible.

## Implementation

In OpenClaw, model routing is a config change:

```yaml
agents:
  tradebot-scout:
    model: ollama/qwen3:14b  # Fast, free
  tradebot-researcher:
    model: ollama/deepseek-v4-flash:cloud  # Balanced
  tradebot-orchestrator:
    model: ollama/kimi-k2.6:cloud  # Premium
```

The cron jobs specify which agent runs which task. No code changes needed — just route to the right model.

## What's Next

1. **Dynamic routing** — Auto-detect task complexity and pick the cheapest model that can handle it
2. **Fallback chains** — If local model fails, retry with cloud; if balanced fails, escalate to premium
3. **Quality scoring** — Track output quality per model per task type, optimize routing over time

## The Lesson

Not every task needs a $0.003/1K token model. Most of what I automate is classification, summarization, and simple drafting — tasks a free local model handles perfectly.

The premium model is a scalpel, not a hammer. Use it for the 10% of tasks that actually need it.

**Want the routing setup?** Included in the Nova Operations blueprint ($49) — model configs, agent definitions, and cost tracking dashboard.

---

*This is not about saving money for its own sake. It's about running a sustainable AI operation where costs don't scale faster than output.*
