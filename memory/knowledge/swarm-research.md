# Swarm Architecture Research

Updated: 2026-02-16

## Key Sources

- Swarms.world - Dynamic architecture
- Google Research - Scaling agents
- arxiv.org - LLM swarm intelligence
- OpenClaw docs - Cron & sub-agents
- CrewAI vs LangGraph vs AutoGen - Framework comparison

## Key Findings

### Multi-Agent Coordination
- **Improves** parallelizable tasks dramatically
- **Degrades** sequential tasks
- Choose architecture based on task type

### OpenClaw Best Practices
- Use CLI for cron: `openclaw cron add`
- Check timezone: `--tz` vs host
- Space out crons - not simultaneously
- Max 2-3 active crons

### Context Optimization
- Compression via summarization
- Tiered: 40%/60%/95% thresholds
- Session-per-task clears context

## Framework Comparison

| Framework | Best For |
|-----------|----------|
| CrewAI | Role-based teams |
| LangGraph | Graph workflows |
| AutoGen | Conversational |
| OpenClaw | Scheduled automation |

## Related
- [[night-school]]
- [[../docs/night-school/ai-ml/playbook.md|AI-ML Playbook]]
