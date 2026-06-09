# Cron Model Tiering Playbook

## Overview

Optimize AI agent costs by routing tasks to appropriate models based on complexity, urgency, and budget. This playbook covers tiered model strategies for OpenClaw cron jobs and sub-agents.

## Why Tier Models?

**Cost variance is massive:**
- GPT-4/Claude Opus: $5-15 per 1M tokens
- Mid-tier (GPT-4o-mini, Haiku): $0.50-2 per 1M tokens
- Budget (DeepSeek, Qwen): $0.10-0.50 per 1M tokens
- Local (Ollama): Free (your hardware)

**Example savings:** Routing 80% of tasks to cheap models = 60-70% cost reduction while maintaining quality on complex tasks.

## Model Tiers (2026 Pricing)

### Tier 1: Premium ($$$)
**Use for:** Complex reasoning, high-stakes decisions, creative work

| Model | Provider | Cost (input/output) | Best For |
|-------|----------|---------------------|----------|
| Grok-4 | xAI | ~$5/$15 per 1M | Complex reasoning, debugging |
| Claude Opus 4 | Anthropic | ~$15/$75 per 1M | High-stakes analysis |
| GPT-5.1 | OpenAI | ~$10/$30 per 1M | General premium tasks |
| Kimi-K2.5 | Moonshot | ~$2/$8 per 1M | Long context, nuanced tasks |

### Tier 2: Mid-Range ($$)
**Use for:** Standard tasks, content generation, moderate complexity

| Model | Provider | Cost (input/output) | Best For |
|-------|----------|---------------------|----------|
| MiniMax-M2.5 | MiniMax | ~$1/$4 per 1M | Creative writing, analysis |
| Claude Haiku 3.5 | Anthropic | ~$0.80/$4 per 1M | Fast responses, classification |
| GPT-4o-mini | OpenAI | ~$0.15/$0.60 per 1M | General tasks |
| Gemini 2.5 Flash | Google | ~$0.075/$0.30 per 1M | Fast, cheap, good quality |

### Tier 3: Budget ($)
**Use for:** Simple tasks, classification, routing, high-volume

| Model | Provider | Cost (input/output) | Best For |
|-------|----------|---------------------|----------|
| DeepSeek V3.2 | DeepSeek | ~$0.14/$0.28 per 1M | Best value, coding |
| Qwen 2.5/3 | Alibaba | ~$0.10/$0.30 per 1M | General tasks |
| Grok-4 Fast | xAI | ~$0.50/$2 per 1M | Fast premium-lite |

### Tier 4: Local (Free)
**Use for:** High-volume, simple tasks, testing, development

| Model | Provider | Cost | Best For |
|-------|----------|------|----------|
| Qwen3:14b | Ollama | Free | General tasks, sub-agents |
| DeepSeek-R1:7b | Ollama | Free | Reasoning, analysis |
| Llama 3.1:8b | Ollama | Free | Simple classification |

## Routing Strategies

### Strategy 1: Task Complexity Routing

```
┌─────────────────────────────────────────┐
│           Incoming Task                 │
└─────────────────────────────────────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │ Classify Complexity │
         └─────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
┌────────┐    ┌──────────┐    ┌──────────┐
│ Simple │    │ Moderate │    │ Complex  │
│        │    │          │    │          │
│ Tier 4 │    │ Tier 2-3 │    │ Tier 1   │
│ Local  │    │ Budget   │    │ Premium  │
└────────┘    └──────────┘    └──────────┘
```

**Classification criteria:**
- **Simple:** Summarization, classification, extraction, formatting
- **Moderate:** Content generation, analysis, multi-step reasoning
- **Complex:** Architecture decisions, debugging, creative strategy

### Strategy 2: Cost-Aware Fallback

```
Primary: DeepSeek V3.2 ($0.14/1M)
   │
   ├─→ Success → Done
   │
   └─→ Rate limit/Error
         │
         ▼
Fallback 1: Qwen 2.5 ($0.10/1M)
   │
   ├─→ Success → Done
   │
   └─→ Rate limit/Error
         │
         ▼
Fallback 2: Ollama Qwen3:14b (Free)
   │
   └─→ Final fallback
```

**Tools for this:**
- **ModelRelay** - Auto-routes to fastest available free model
- **OpenRouter** - Unified API with automatic failover
- **Custom gateway** - Build your own routing logic

### Strategy 3: OpenClaw Native Tiering

```yaml
# In your OpenClaw config or session spawn

# Default (most tasks)
default_model: "moonshot/kimi-k2.5"

# Heavy tasks (explicit override)
heavy_task_model: "xai/grok-4"

# Local/free (budget mode)
local_model: "ollama/qwen3:14b"

# Reasoning tasks
reasoning_model: "ollama/deepseek-r1:7b"
```

**Usage:**
```javascript
// Simple task - free
sessions_spawn({
  task: "Summarize this article",
  model: "ollama/qwen3:14b"
})

// Complex task - premium
sessions_spawn({
  task: "Debug this architecture issue",
  model: "xai/grok-4"
})

// Default - let AGENTS.md decide
sessions_spawn({
  task: "Write a blog post"
  // Uses kimi-k2.5 by default
})
```

## OpenClaw Best Practices

### Cron Job Model Assignment

| Cron Type | Recommended Model | Why |
|-----------|-------------------|-----|
| Health checks | ollama/qwen3:14b | Simple, frequent, free |
| Memory distillation | ollama/deepseek-r1:7b | Needs reasoning, local |
| Daily summaries | moonshot/kimi-k2.5 | Nuanced, good quality |
| Income research | ollama/qwen3:14b | High volume, cheap |
| Complex analysis | xai/grok-4 | Deep reasoning needed |

### Sub-Agent Tiering

```javascript
// Orchestrator (makes decisions)
const orchestrator = sessions_spawn({
  task: "Coordinate research workflow",
  model: "moonshot/kimi-k2.5",  // Mid-tier for decisions
  mode: "session"
})

// Workers (do the work)
const researchers = [
  sessions_spawn({
    task: "Research topic A",
    model: "ollama/qwen3:14b",  // Free for parallel work
    mode: "run",
    cleanup: "delete"
  }),
  sessions_spawn({
    task: "Research topic B",
    model: "ollama/qwen3:14b",
    mode: "run",
    cleanup: "delete"
  })
]
```

### Context Optimization

**Reduce costs by reducing tokens:**

1. **Summarize before sending:**
   - 40-60% input cost reduction
   - Use cheap model to summarize, expensive to analyze

2. **Tiered context thresholds:**
   - 40%: Compress old messages
   - 60%: Summarize conversation
   - 95%: Emergency truncation

3. **Session per task:**
   - New session = fresh context = no baggage
   - Delete sessions after completion

## Implementation: Model Gateway

**Build a simple router:**

```javascript
async function routeTask(task, complexity) {
  const models = {
    simple: "ollama/qwen3:14b",
    moderate: "moonshot/kimi-k2.5",
    complex: "xai/grok-4"
  }
  
  const model = models[complexity] || models.moderate
  
  return sessions_spawn({
    task,
    model,
    cleanup: "delete"
  })
}

// Auto-classify (use cheap model to classify)
async function autoRoute(task) {
  const classification = await classifyComplexity(task)  // Free model
  return routeTask(task, classification)
}
```

## Monitoring & Optimization

### Track These Metrics

1. **Cost per task type**
   - Identify over-served tasks (using expensive model unnecessarily)
   - Find under-served tasks (cheap model failing, needs upgrade)

2. **Success rate by model**
   - If cheap model fails 30%+ → upgrade tier
   - If expensive model succeeds 100% on simple tasks → downgrade

3. **Latency vs cost**
   - Sometimes paying 2x for 10x speed is worth it
   - Batch non-urgent tasks for off-peak

### Weekly Review

```markdown
## Model Usage Review (Week of YYYY-MM-DD)

**Total spend:** $X.XX
**Tasks routed:** N

**By tier:**
- Tier 1 (Premium): X tasks, $Y.YY
- Tier 2 (Mid): X tasks, $Y.YY
- Tier 3 (Budget): X tasks, $Y.YY
- Tier 4 (Local): X tasks, $0.00

**Optimization opportunities:**
- [ ] Task type X always succeeds on Tier 3 → downgrade
- [ ] Task type Y fails 40% on Tier 2 → upgrade
- [ ] Consider batching Z tasks for off-peak
```

## Key Takeaways

1. **Default to cheap** - Start with budget/local, upgrade only when needed
2. **Classify before routing** - Use free model to determine complexity
3. **Fallback chains** - Always have a backup model ready
4. **Monitor continuously** - Track success rates and adjust
5. **Local is your friend** - Ollama for high-volume, simple tasks

---

*Generated by Night School - 2026-02-27*
