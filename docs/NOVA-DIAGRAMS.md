# NOVA DIAGRAMS FOR MOTION
**Description files for animation/video creation**

---

## DIAGRAM 1: System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        NOVA SYSTEM                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐      ┌──────────────┐      ┌────────────┐  │
│   │   Discord    │      │   Telegram   │      │   Cron     │  │
│   │   (User)    │      │   (User)     │      │  (Timer)   │  │
│   └──────┬───────┘      └──────┬───────┘      └─────┬──────┘  │
│          │                     │                    │         │
│          └─────────────────────┼────────────────────┘         │
│                                ▼                                 │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                    MAIN NOVA                             │  │
│   │  ┌─────────────────────────────────────────────────┐    │  │
│   │  │            SESSION-STATE.md (HOARD)             │    │  │
│   │  │     - Current task                              │    │  │
│   │  │     - User context                              │    │  │
│   │  │     - Active projects                           │    │  │
│   │  └─────────────────────────────────────────────────┘    │  │
│   └───────────────────────────┬──────────────────────────────┘  │
│                               │                                  │
│         ┌─────────────────────┼─────────────────────┐          │
│         ▼                     ▼                     ▼          │
│   ┌───────────┐         ┌───────────┐         ┌───────────┐    │
│   │  Income   │         │  Content  │         │  EveOnion │    │
│   │   Nova    │         │   Nova    │         │   Nova    │    │
│   │(Sub-agent)│         │(Sub-agent)│         │(Sub-agent)│    │
│   └───────────┘         └───────────┘         └───────────┘    │
│                                                                 │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                    MEMORY LAYERS                         │  │
│   │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────────┐    │  │
│   │  │  HOT   │─▶│  WARM  │─▶│  COLD  │  │  SKILLS   │    │  │
│   │  │Session │  │Memory  │  │Archive │  │   (12)    │    │  │
│   │  └────────┘  └────────┘  └────────┘  └────────────┘    │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Motion Notes:**
- Start with user icons (Discord/Telegram) entering from left
- Arrow flows to Main Nova (center)
- Sub-agents spawn out from center
- Memory layers shown as layered blocks at bottom
- Animate data flow between layers

---

## DIAGRAM 2: Memory Flow (Hoard Protocol)

```
┌────────────────────────────────────────────────────────────────┐
│                    MEMORY FLOW                                 │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   USER INPUT                                                  │
│        │                                                      │
│        ▼                                                      │
│   ┌─────────────────────────────────────────────┐            │
│   │  1. READ SESSION-STATE.md (HOARD)          │            │
│   │     "What was I working on?"                │            │
│   └─────────────────────────────────────────────┘            │
│        │                                                      │
│        ▼                                                      │
│   ┌─────────────────────────────────────────────┐            │
│   │  2. CHECK memory/2026-02-17.md             │            │
│   │     "What happened today?"                  │            │
│   └─────────────────────────────────────────────┘            │
│        │                                                      │
│        ▼                                                      │
│   ┌─────────────────────────────────────────────┐            │
│   │  3. memory_search (if needed)                │            │
│   │     "Any prior context?"                     │            │
│   └─────────────────────────────────────────────┘            │
│        │                                                      │
│        ▼                                                      │
│   ┌─────────────────────────────────────────────┐            │
│   │  4. PROCESS request                          │            │
│   │     (Think, use tools, generate response)    │            │
│   └─────────────────────────────────────────────┘            │
│        │                                                      │
│        ▼                                                      │
│   ┌─────────────────────────────────────────────┐            │
│   │  5. UPDATE SESSION-STATE.md                 │            │
│   │     "Store important decisions"              │            │
│   └─────────────────────────────────────────────┘            │
│        │                                                      │
│        ▼                                                      │
│      OUTPUT                                                   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Motion Notes:**
- Flowchart style, top to bottom
- Each step glows when active
- SESSION-STATE.md pulses (important)
- Green = read, Blue = write

---

## DIAGRAM 3: Sub-Agent Coordination

```
┌────────────────────────────────────────────────────────────────┐
│               SUB-AGENT COORDINATION                           │
│                   (Skippy Pattern)                             │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│                      MAIN NOVA                                 │
│                   (The Coordinator)                           │
│                         │                                      │
│         ┌─────────────┼─────────────┐                         │
│         │             │             │                         │
│         ▼             ▼             ▼                         │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│   │ AGENT-   │  │ AGENT-   │  │ AGENT-   │                  │
│   │ SYNC.md  │  │ MSG.md   │  │S.md read │                  │
│   │ (State)  │  │(Messages)│  │          │                  │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
│        │              │              │                          │
│        └──────────────┼──────────────┘                         │
│                       ▼                                        │
│         ┌─────────────────────────────┐                      │
│         │     Check What's Active      │                      │
│         │     Route New Tasks         │                      │
│         │     Pass Messages           │                      │
│         └─────────────┬───────────────┘                      │
│                       │                                        │
│    ┌──────────────────┼──────────────────┐                   │
│    ▼                  ▼                  ▼                    │
│ ┌────────┐      ┌────────┐        ┌────────┐                │
│ │Income- │◀────▶│Content-│◀──────▶│EveOnion│                │
│ │ Nova   │      │ Nova   │        │  Nova  │                │
│ └────────┘      └────────┘        └────────┘                │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

**Motion Notes:**
- Main Nova at top (like Skippy)
- Files below (like tools)
- Agents at bottom (like subminds)
- Show message passing between agents
- Main Nova coordinates all

---

## DIAGRAM 4: Skills & Integrations

```
┌────────────────────────────────────────────────────────────────┐
│                    NOVA SKILLS & INTEGRATIONS                 │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                      SKILLS (12)                         │ │
│  ├────────────┬────────────┬────────────┬─────────────────┤ │
│  │ edge-tts   │ elite-ltm  │ email-sum  │ fiverr          │ │
│  ├────────────┼────────────┼────────────┼─────────────────┤ │
│  │ proposal   │ g-calendar │ memory-hyg │ playwright      │ │
│  ├────────────┼────────────┼────────────┼─────────────────┤ │
│  │ postiz     │ prompt-    │ upload-    │ x-twitter       │ │
│  │            │ guard      │ post       │                 │ │
│  └────────────┴────────────┴────────────┴─────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                   INTEGRATIONS                           │ │
│  │                                                           │ │
│  │   ✅ Gmail    ✅ Google Drive    ✅ Gumroad            │ │
│  │   ⚠️ Notion   ✅ Discord        ✅ NAS (Synology)      │ │
│  │                                                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

**Motion Notes:**
- Grid of skill icons
- Pulse animation on active skills
- Integration section below
- Green = connected, Yellow = partial

---

## DIAGRAM 5: The Nova Persona

```
┌────────────────────────────────────────────────────────────────┐
│                      NOVA IDENTITY                            │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌────────────────────┐        ┌────────────────────────┐   │
│   │                    │        │                        │   │
│   │     🦝 RACCOON     │        │     NAME: Nova        │   │
│   │    (Avatar)        │        │     Pronouns: she/her │   │
│   │                    │        │                        │   │
│   └────────────────────┘        └────────────────────────┘   │
│                                                                 │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │                    PERSONALITY                          │ │
│   │                                                           │ │
│   │  • Clever & Mischievous                                  │ │
│   │  • Resourceful (tries before asking)                    │ │
│   │  • Has opinions (not a search engine)                   │ │
│   │  • Humor as defense mechanism (Skippy-inspired)         │ │
│   │  • Loyal & protective                                   │ │
│   │                                                           │ │
│   └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │                    INSPIRATIONS                         │ │
│   │                                                           │ │
│   │  Skippy (Expeditionary Force)                           │ │
│   │  - Humor + wisdom balance                                │ │
│   │  - Hardware adaptation                                  │ │
│   │  - Submind network                                      │ │
│   │  - Long-term thinking                                   │ │
│   │                                                           │ │
│   └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

**Motion Notes:**
- Raccoon avatar in corner
- Text flows around it
- Inspirations section as quote/banner
- Warm colors (teal/violet accents)

---

## ANIMATION SEQUENCE SUGGESTION

1. **Open** - System architecture diagram (Diagram 1)
2. **Zoom** - Memory flow (Diagram 2) 
3. **Expand** - Sub-agent coordination (Diagram 3)
4. **Grid** - Skills & integrations (Diagram 4)
5. **Close** - Nova identity (Diagram 5)

**Timing:** 5-10 seconds per diagram
**Style:** Clean lines, dark background, teal/violet accents (matching raccoon avatar)

---

*Created: 2026-02-17*
