# Automation Playbook

## Overview
AI automation in 2026 focuses on agentic workflows—systems that can take a goal and work through steps autonomously. The shift is from rigid scripts to flexible agents that understand intent, learn from context, and take initiative.

## Key Concepts

### Agent vs Traditional Automation
- **Traditional automation**: Fixed path, struggles with messy inputs, fails on exceptions
- **Agentic automation**: Chooses steps, handles variability, recovers from failures

### The Agent Loop
```
Goal → Decide next step → Use tool → Check result → Repeat → Done/Escalate
```

## Four Architecture Types

| Type | Best For | Main Risk |
|------|----------|-----------|
| **Single Agent** | Simple-medium tasks, fast iteration | Drift and looping |
| **Hierarchical (Manager + Workers)** | Complex tasks that split into parts | Coordination overhead |
| **Sequential Pipeline** | Repeatable processes with known path | Brittleness on edge cases |
| **Swarm (Decentralized)** | Exploration, debate, broad coverage | Hard to predict/debug |

### When to Use Each
- **Single agent**: Small tool set, linear tasks, well-defined goals
- **Hierarchical**: Need parallelism, separation of duties, permission boundaries
- **Pipeline**: Known fixed steps, validation requirements, fallback routes
- **Swarm**: Research, creative exploration, multi-perspective analysis

## Best Practices

### 1. Start Simple
First working version = single agent. Add multi-agent structure only when you have a clear reason:
- Need parallelism
- Need separation of duties
- Need better reliability
- Need tighter permission boundaries

### 2. Match Architecture to Risk
Ask: "How risky is a mistake?"
- Small annoyance → more freedom OK
- Financial/legal/customer harm → strict guardrails, human approval gates

### 3. Tool Design Matters
- Give smallest amount of freedom that delivers outcome
- Focus effort on tool design, safety, observability

### 4. Five Questions for Choosing Architecture
1. Do you already know the steps, or does the system need to figure them out?
2. How risky is a mistake?
3. How many systems does the agent need to touch?
4. Will the task finish in one sitting, or need checkpoints?
5. Do you need one capability, or many?

## Nova-Specific Implementation

### Current Setup (Already Done)
- AGENTS.md defines model tiering for cost efficiency
- Sub-agents (shards) for parallel task execution
- Heartbeat system for monitoring

### Recommended Patterns
1. **Single agent for cron tasks**: Simple, predictable, low cost
2. **Hierarchical for complex workflows**: Supervisor (qwen3.5-plus) delegates to workers (ollama)
3. **Swarm for research**: Multiple ollama agents exploring different angles

### Guardrails
- Max 4-6 active sub-agents
- Space out cron jobs to avoid overlaps
- Circuit breakers on external API calls
- Human approval for financial actions

## Tools & Platforms

### Build Your Own (Nova approach)
- OpenClaw for orchestration
- Ollama for local free inference
- OpenRouter for API fallback

### No-Code Platforms (2026)
- **Vellum AI**: Describe task, no code required
- **AutoGen**: Microsoft open-source agent framework
- **LangChain**: Full-stack agent development

## Success Metrics
- Track time saved AND output quality improvements
- Measure reduction in back-and-forth
- Monitor error rates and recovery time

## Status
✅ PLAYBOOK COMPLETE - 2026-03-05
