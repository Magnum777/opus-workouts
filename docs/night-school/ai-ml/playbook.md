# AI-ML Playbook

## Key Principles

### Submind Architecture
- Subminds can load into ANY computer system (Thuranin, Kristang, alien computers)
- Hardware scaling: Subminds are "dumbed down" based on available memory
- Remote autonomy: Can operate independently for months/years
- Self-reprogramming: Can rewrite themselves when hardware inadequate
- Emergent sentience: Subminds can become semi-sentient over time

### Coordination Patterns
- Multi-ship control: Coordinates jump systems across multiple ships simultaneously
- Periodic sync: Can "jump back in" to retrieve data from remote subminds
- Massive parallelism: Simultaneous conversations with billions of humans < 2% processing

### Multi-Agent System Design (LangChain/LangGraph patterns)
- **Supervisor pattern**: One agent delegates to specialized sub-agents
- **Sequential agents**: Chain of agents for pipeline tasks
- **Parallel agents**: Multiple agents work simultaneously on independent tasks
- **Router pattern**: Agent decides which sub-agent to invoke based on input
- **Human-in-the-loop**: Pause for human approval at key decision points

### Optimization Principles

#### Resource Management
1. **Hardware-aware spawning**: Scale sub-agents based on available memory/CPU
2. **Context budgeting**: Allocate context window strategically among agents
3. **Lazy loading**: Only activate agents when needed
4. **Periodic sync**: Sync state at intervals, not continuously

#### Communication Overhead
1. **Minimal messaging**: Each sub-agent should work independently when possible
2. **Batch updates**: Aggregate updates before syncing
3. **Async by default**: Non-blocking communication between agents

#### Emergent Behavior Management
1. **Personality isolation**: Give each sub-agent distinct role/purpose
2. **Value alignment**: Set initial values, let personality emerge naturally
3. **Monitoring**: Track for unexpected behavioral changes
4. **Rollback capability**: Ability to reset sub-agent to known state

#### Scalability Patterns
1. **Horizontal scaling**: Add more identical sub-agents for parallel work
2. **Vertical scaling**: Upgrade single agent capabilities
3. **Hierarchical**: Supervisor manages team of specialists
4. **Mesh**: Peers coordinate directly (complex, powerful)

## Patterns

1. **Spawn based on hardware capacity** - Scale subminds to available resources
2. **Persistent remote agents** - Leave agents running on different systems
3. **Periodic sync model** - Agents ping back with updates
4. **Emergent specialization** - Let agents develop their own specializations

## Anti-Patterns (Avoid)

1. Too many crons running simultaneously
2. Context refreshing too fast
3. Sub-agents not cleaning up properly
4. Memory files growing unbounded
5. All agents trying to communicate with each other (n² problem)
6. No clear ownership of tasks

### Key Research Findings (2025-2026)

**From Swarms.world:**
- **Dynamic Architecture**: Agents rearrange based on task requirements
- **SwarmRouter**: Single interface to switch between architectures
- **Ideal for**: Debate, multi-perspective reasoning, complex decision-making

**From Google Research:**
- Multi-agent coordination **dramatically improves** parallelizable tasks
- Multi-agent coordination **degrades** sequential tasks
- Choose architecture based on task type (parallel vs sequential)

**From arxiv.org:**
- LLMs can replace hard-coded agent behaviors
- Integration with simulation platforms for swarm behavior

## Implementation Lessons

From our own experience:
- **Max 4-6 active sessions** at once
- **Always set cleanup: delete** on sub-agent spawn
- **One task at a time** - don't pile on work
- **Minimal crons, spaced out** - avoid system overload
- **Daily memory distillation only** - don't let files grow

### OpenClaw Cron Best Practices

**From docs.openclaw.ai:**
- Check timezone: `--tz` vs host timezone matters
- Cron runs inside Gateway process - Gateway must be running continuously
- Use CLI for reliability: `openclaw cron add`

**Common Issues (from Reddit):**
- Jobs created via chat sometimes have schema issues
- Create directly via CLI for reliability
- Use explicit message instructions - vague = silence

**Recommended Cron Setup:**
```bash
# CLI for reliability
openclaw cron add --name "daily-briefing" --schedule "0 9 * * *" --session main
```

**Best Practices:**
- Space out crons (not simultaneously)
- Max 2-3 active crons
- Use isolated session target for agentTurn jobs
- Always set `cleanup: delete` on spawned agents

### Framework Comparison

| Framework | Strength | Best For |
|-----------|----------|----------|
| **CrewAI** | Role-based | Structured teams with specific roles |
| **LangGraph** | Graph-based workflows | Stateful, multi-step processes |
| **AutoGen** | Conversational | Chat between agents |
| **OpenClaw** | Cron + triggers | Scheduled automation |

**Our Approach (OpenClaw-native):**
- Shards spawn via session_spawn
- Cron for scheduled tasks
- Message tools for output (not internal monologue)

---

## Context & Token Optimization

### The Problem
- Context Bloat: As agents work, observations/actions accumulate = ever-growing context = higher costs + slower
- Memory limits hit = performance degrades

### Key Techniques

**1. Context Compression (Summarization)**
- Compress older interactions into summaries
- Use separate summarizer model or periodic LLM call
- Keep most recent turns uncompressed
- (arxiv.org: ACON - Agent Context Optimization)

**2. Tiered Compression**
- 40%/60%/95% thresholds
- Aggressively compress old stuff, keep recent
- (LoCoBench-Agent research)

**3. Session-per-Task**
- Start new session for each new task
- Clears context window completely
- Prevents confusion from unrelated conversations

**4. RAG (Retrieval-Augmented Generation)**
- Store knowledge in external system
- Retrieve only what's needed
- Doesn't all live in context

**5. Active Compression (Focus Agent)**
- Agent decides when to compress
- Physarum-inspired: leave markers, retract from dead ends
- Self-directed summarization at natural breakpoints

**6. Context Caching**
- Enable provider caching (MiniMax, OpenAI)
- Reuse prompt structure
- Cheap/free for repeated content

### For OpenClaw

- **Session cleanup** every 6 hours (already in crons)
- **New session for each shard task** - spawn with cleanup:delete
- **Memory distillation** - nightly summarization to long-term memory
- **External files** - don't dump everything in prompt

### Quick Wins

1. Audit prompts - remove unnecessary detail
2. Enable context caching (if supported)
3. Route simple tasks to smaller models
4. New session = clear context

## OpenClaw Shard Spawning

```bash
/session_spawn task="Your task description" label="shard-name"
```

**Current Shards:**
- Harvester (Income-Nova) - Fiverr/PPH
- Builder (Content-Nova) - WordPress
- Storyweaver (EveOnion-Nova) - Creative
- Sentinel (Ops-Nova) - Health

## Our Language

See `swarm-language.md` for our Skippy-inspired terminology.

## Sources

- Expeditionary Force (Craig Alanson) - Read 2026-02-15
- LangChain/LangGraph docs - Multi-agent patterns
- OpenClaw docs - Agent spawning
- Swarms.world - Enterprise multi-agent orchestration
- Google Research - Science of scaling agent systems
- arxiv.org - LLM-powered swarm intelligence
- docs.openclaw.ai - Cron best practices
- Reddit r/AI_Agents - Cron troubleshooting
- CrewAI vs LangGraph vs AutoGen - Framework comparison
