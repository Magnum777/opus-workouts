# Video 1 Script: "Install Nova in 10 Minutes"

**Target length:** 8 minutes
**Style:** Screen recording + voiceover. Fast-paced, no filler.

---

## [0:00] Hook

**Visual:** Fast montage of Nova doing things — checking email, posting to Discord, analyzing data, writing content.

**Voiceover:**
"What if you had an employee who never slept, never forgot anything, and handled all the work you hate?"

**Visual:** Cut to host at desk, casual, no corporate vibe.

"That's Nova. And in the next 10 minutes, you're going to install one on your own machine."

---

## [0:30] The Product

**Visual:** Show Gumroad product page. $149 price. Scroll through what's included.

**Voiceover:**
"Nova AI Cofounder V3. It's not a chatbot. It's not a subscription. It's a self-hosted AI coworker that lives on your computer, works while you sleep, and actually does things."

**Visual:** Quick list of included items:
- Setup script
- PDF guide
- Video walkthroughs
- Prompt library
- 7-day onboarding

"For $149, you get the full setup package, a 30-page guide, these video walkthroughs, and a 7-day onboarding sequence that teaches Nova who you are and how you work."

---

## [1:00] Download

**Visual:** Screen recording. Download the ZIP from Gumroad receipt. Extract it.

**Voiceover:**
"After purchase, download the ZIP and extract it anywhere. I put mine in C:\Tools."

**Visual:** Show folder contents. setup/, config/, prompts/, docs/.

"Here's what you get. The setup folder has the installer. Config has templates for Nova's personality and your profile. Prompts has the 7-day intake. And docs has the full guide."

---

## [1:30] Run the Installer

**Visual:** Right-click PowerShell, Run as Administrator. Type the install command.

**Voiceover:**
"Open PowerShell as admin. Navigate to the setup folder. And run install.ps1."

**Visual:** Show terminal output. Prerequisites check — Python, Git, Node, Ollama.

"The script checks what you have and installs what's missing. Python, Git, Node.js, Ollama for the AI model. All automatic."

**Visual:** Green checkmarks appearing. One yellow warning about Docker.

"It'll ask about Docker — you can skip it, it's optional. Native install is faster."

---

## [2:30] OpenClaw Gateway

**Visual:** Terminal shows OpenClaw Gateway downloading and installing.

**Voiceover:**
"Next it installs the OpenClaw Gateway — this is the runtime that connects everything. The AI model, the skills, your channels."

**Visual:** Show the gateway folder structure.

"It lives in your home directory under .openclaw. Everything Nova needs is right here."

---

## [3:00] Channel Setup

**Visual:** Terminal prompts for Discord token. Show discord.com/developers/applications. Create app, bot, copy token.

**Voiceover:**
"Now it asks about channels. How do you want to talk to Nova?"

**Visual:** Enter Discord token. Then Telegram — skip. WhatsApp — skip.

"I use Discord for most things, so I enter my bot token. Telegram and WhatsApp are optional. You can add them later."

---

## [3:30] Skills

**Visual:** Terminal shows core skills installing. Then optional skills prompt.

**Voiceover:**
"Skills are Nova's capabilities. Core skills install automatically — web search, browser automation, memory management."

**Visual:** Yes to gmail-cleanup. Yes to wordpress-pro. No to ai-social-media. Yes to upload-post.

"Then it asks about optional skills. I want Gmail cleanup and WordPress publishing. Social media can wait."

---

## [4:00] Templates

**Visual:** Show files being copied to ~/.openclaw/workspace/

**Voiceover:**
"Now it copies the template files — SOUL.md for Nova's personality, USER.md for your profile, AGENTS.md for workspace rules, TOOLS.md for your machine specs, and MEMORY.md for long-term storage."

**Visual:** Open SOUL.md in Notepad. Default raccoon personality.

"By default, Nova is a raccoon — clever, resourceful, slightly mischievous. You can change this later."

---

## [4:30] Launch Intake

**Visual:** Terminal shows "Nova is installed. Run 'openclaw nova-intake' to start Day 1."

**Voiceover:**
"Install complete. Now we run the intake — a 7-day onboarding that teaches Nova who you are."

**Visual:** Run the command. Day 1 prompt appears.

"Day 1 is identity — your name, your business, your timezone, how you work best. Takes about 5 minutes."

**Visual:** Answer prompts quickly (sped up 3x). Type DONE.

"That's it. Day 1 complete."

---

## [5:30] First Interaction

**Visual:** Open web chat. Type "Hey Nova, what's my timezone?"

**Voiceover:**
"Let's test it. Nova, what's my timezone?"

**Visual:** Response: "America/New_York. You told me during intake."

"She remembers. Already."

---

## [6:00] First Task

**Visual:** Type "/delegate Research AI assistant pricing"

**Voiceover:**
"Let's do something real. I need to know what competitors charge for AI assistants."

**Visual:** Nova responds: "Task accepted. I'll research pricing and report back."

"Nova goes off, searches the web, analyzes results."

**Visual:** Wait 30 seconds. Result appears.

"Here's the breakdown — ChatGPT Plus at $20, Claude Pro at $20, but nothing at the $149 self-hosted level. Good data for my pricing page."

---

## [7:00] Summary

**Visual:** Show everything installed — Gateway running, Discord bot online, skills installed, templates configured.

**Voiceover:**
"In 10 minutes: OpenClaw Gateway installed, Discord bot connected, 6 core skills ready, personality configured, first task completed."

**Visual:** Show Gumroad page again. $149.

"Nova AI Cofounder V3. $149 one-time. No subscription. Your AI coworker, on your machine, working while you sleep."

**Visual:** CTA screen.

"Link in description. 25% off with code NOVA25 for the first 100 buyers."

---

## [7:30] Outro

**Visual:** Host back on screen.

**Voiceover:**
"Questions? Drop them below. Or join our Discord — link in description. No paid support, just a community of people running AI coworkers."

**Visual:** Subscribe button, Discord link.

"See you in the next video — Day 1 with Nova."
