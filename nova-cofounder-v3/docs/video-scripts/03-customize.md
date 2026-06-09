# Video 3 Script: "Customize Everything"

**Target length:** 10 minutes
**Style:** Screen recording + voiceover. Quick cuts, lots of examples.

---

## [0:00] Hook

**Visual:** Split screen. Left: Default Nova (raccoon). Right: Custom Nova (dragon). Both responding to same prompt differently.

**Voiceover:**
"Same AI. Completely different personality. In the next 10 minutes, I'll show you how to make Nova sound like YOU."

---

## [1:00] Personality Swap

**Visual:** Open SOUL.md in VS Code.

**Voiceover:**
"The personality lives in SOUL.md. This one file controls everything — how Nova talks, what she values, when she speaks up, when she stays quiet."

**Visual:** Default raccoon section:
```
- Name: Nova
- Creature: Raccoon-spirit AI
- Vibe: Clever, resourceful, slightly mischievous
- Emoji: 🦝
```

"Default is raccoon. Clever, resourceful, hacker-familiar."

**Visual:** Change to owl.
```
- Creature: Owl-spirit AI
- Vibe: Thoughtful, precise, no fluff
- Emoji: 🦉
```

"Let's swap to owl. Save the file."

**Visual:** Open chat. Same prompt: "What do you think about this code?"

Raccoon response: "Oh this is fun. You're using a loop where a map would be cleaner. Want me to rewrite it? 🦝"

Owl response: "The loop is functional but inefficient. A functional approach would reduce complexity. Here is the refactored version."

**Voiceover:**
"Completely different tone. Same competence. Just... different energy."

---

## [2:30] Communication Style

**Visual:** Edit SOUL.md communication section.

Default:
```
- Short and direct, or detailed when it matters
- Casual, not corporate
- Proactive check-ins are welcome
```

Change to:
```
- Always detailed. I want context and reasoning.
- Formal with clients, casual with me
- Never interrupt my flow state
```

**Voiceover:**
"Communication style is granular. Short vs detailed. Formal vs casual. Proactive vs reactive."

**Visual:** Show before/after responses to "Should I buy this stock?"

Before: "No. Too risky. 🦝"
After: "Analysis: The token has low liquidity ($12K), high sell ratio (87%), and was created 3 days ago. These are honeypot indicators. Recommendation: Pass. If you want exposure to this sector, I can suggest alternatives with better fundamentals."

**Voiceover:**
"Detail level changes everything."

---

## [4:00] Add a Custom Skill

**Visual:** Open terminal. Run `clawhub search crypto`.

**Voiceover:**
"Skills are modular. Want Nova to trade crypto? Install the skill."

**Visual:** `clawhub install solana-payments-wallets-trading`

"This adds Solana wallet management, token swaps, price checking — all from chat."

**Visual:** Test it. "Nova, what's the price of JUP?"

Response: "$1.24, up 3.2% in 24h. Market cap: $1.8B. Volume: $45M."

**Voiceover:**
"One command, one install, new capability."

---

## [5:00] Custom Cron Job

**Visual:** Type in chat: `/cron add "0 9 * * 1" "Check competitor blog for new posts"`

**Voiceover:**
"Custom recurring tasks. Every Monday at 9 AM, Nova checks a competitor's blog and reports new posts."

**Visual:** Show the cron in the list. Then show the result next Monday.

"Set it once, runs forever. I review the results when I want."

---

## [6:00] Voice/Avatar (if TTS available)

**Visual:** If edge-tts or ElevenLabs is configured.

**Voiceover:**
"If you have TTS set up, Nova can speak. Different voices for different personalities."

**Visual:** Play raccoon voice (playful, slightly fast). Then owl voice (measured, slower).

"Raccoon sounds excited. Owl sounds... like an owl."

---

## [7:00] Project Templates

**Visual:** Open memory/projects.md. Show structure.

```markdown
## Website Redesign
- Client: ABC Corp
- Budget: $5,000
- Deadline: July 15
- Status: Mockup approved
- Next: Await content from client
- Blocker: Client slow to respond
```

**Voiceover:**
"Projects are tracked in a simple markdown file. Nova reads this every session."

**Visual:** Add a new project via chat.

"Nova, add project 'Launch V3'"

Response: "Added 'Launch V3'. Status: Planning. What's the first step?"

"Type the details. She logs it. Now it's in her working memory."

---

## [8:00] The Test

**Visual:** Same prompt, three different Nova configurations.

Prompt: "I made a mistake. I spent $500 on ads that didn't convert."

**Raccoon:**
"Oof. That's a hit. But hey — you now know that channel doesn't work. Want me to research what DOES work for your audience? I can have options in 10 minutes. 🦝"

**Owl:**
"Noted. $500 spent, $0 return. We need to analyze why. Factors to consider: audience targeting, creative quality, landing page conversion rate. Shall I audit the campaign data?"

**Dragon:**
"Mistakes happen. The question is what we do next. Either we fix the campaign or we kill it. No middle ground. Decide in the next hour or I'll make the call."

**Voiceover:**
"Same situation. Three completely different responses. That's the power of customization."

---

## [9:00] Summary

**Visual:** Rapid montage of all customizations.

**Voiceover:**
"Personality. Communication style. Skills. Cron jobs. Voice. Project tracking. All customizable. All in simple text files or chat commands."

**Visual:** Show final SOUL.md, TOOLS.md, projects.md side by side.

"This is what makes Nova yours. Not a generic AI. YOUR AI. Configured for how you work, what you value, and what you need."

---

## [9:30] Outro

**Visual:** Host on screen.

**Voiceover:**
"Next video: the scary one. Level 4 autonomy. Nova runs overnight. You wake up to a summary of everything she did."

**Visual:** Subscribe, Discord link.

"Ready?"
