# Kybernauts Clade - Persistent Knowledge Base

**CRITICAL:** This file is READ AT STARTUP by every Kybernauts/EveOnion session.
Any concept, terminology, or lore discussed MUST be recorded here.

## Core Concepts

### Alpha Force
- **Type:** Elite Kybernauts combat division
- **Purpose:** Rapid response PvP unit for Pochven defense
- **Recruitment Status:** Active
- **Requirements:** 
  - Triglavian ship proficiency
  - Pochven navigation experience
  - Team combat mindset
- **Contact:** http://join.kybernauts.space (ALWAYS include in recruitment posts)
- **OPSEC:** NEVER mention Alpha Force in public propaganda, tweets, or recruitment posts. Internal reference only.

### Pochven
- Triglavian-controlled space (region)
- Kybernauts' home territory
- High-risk, high-reward PvP environment

### Clade Structure
- **Kybernauts** = Main group
- **Clades** = Sub-divisions
- **Alpha Force** = Elite combat unit

## Taglines (Use for Propaganda — PUBLIC ONLY)
- "POCHVEN OR BUST"
- "UNDOCK OR DIE"
- "TRIANGLE DEFENDERS"
- "HUNT OR BE HUNTED"
- "FORWARD TO POCHVEN"
- "THE CLADE AWAITS"
- "JOIN OR BE CONSUMED"
- "TRIGLAVIAN GLORY"
- "ASCEND BEYOND"
- **NEVER USE:** "Alpha Force" or any reference to it in public posts (OPSEC)

## Visual Identity
- **Colors:** Dark purple (#1a0a2e), Bio-luminescent teal (#00d4aa), Void black (#0d0208)
- **Symbols:** Triglavian triple-triangle
- **Style:** Dark, geometric, ominous

## Propaganda Media Inventory
**Opus-provided media only — cycle through these for Twitter posts.**

| # | File | Type |
|---|------|------|
| 1 | `media/kybernauts/propaganda/coffee_bump_H.2641.mp4` | video |
| 2 | `media/kybernauts/propaganda/EVE_Poster_15.11.mp4` | video |
| 3 | `media/kybernauts/propaganda/EVE_Poster_191.mp4` | video |
| 4 | `media/kybernauts/propaganda/Kyber_Fleet11.mp4` | video |
| 5 | `media/kybernauts/propaganda/EVE_Poster_201.mp4` | video |

**Rule:** Only use files from this list + any future ones Opus provides. Cycle through them in rotation.

## Active Projects
- [ ] **Alpha Force recruitment PDF** - Create PDF explaining Alpha Force elite combat unit. Include: requirements, benefits, contact info.
- [ ] Twitter propaganda campaign
- [ ] Forum recruitment bumps

## How to Update This File
If Opus tells you about a new concept, terminology, or project:
1. ADD it to this file immediately
2. Categorize it (Concepts/Projects/etc.)
3. This is your ONLY persistent memory

## Last Updated
2026-04-29 - Alpha Force concept added by Opus
- Created this knowledge base file (was missing!)
- Added Alpha Force elite combat unit concept
- Defined core Kybernauts terminology

---

## Ship Fitting & Theorycrafting Guide
### (Learned from ashy.vargur.dev, Brave Dojo, wckg.net, EVE Academy, 2026-05-31)

### Fitting Workflow
Every fit should answer these questions in order:
1. **What am I trying to accomplish?** (PvE in Pochven? Fleet PvP? Solo? Tackle? Logi?)
2. **What is the best ship for this goal?** (Triglavian ship bonuses are the Kybernaut default)
3. **Is there a standardized doctrine fit?** (Alpha Force / SDC doctrines first)
4. **Can I do it cheaper by some method?** (Import from Jita vs buy local in R1O)
5. **Tech 2 (T2) should be default**, but often a meta module helps with fitting (CPU/grid)
6. **Time to comb zkill / eveworkbench / Pyfa**

### Core Fitting Concepts

#### Signature Radius
Every ship has a base signature radius (m). This is the invisible sphere that determines how easily weapons apply damage to you.
- **Smaller sig = harder to hit** (good for PvP, dodging damage)
- **MWD increases sig massively** when active (bad)
- **AB does NOT increase sig** (good)
- **Shield tank increases sig** (armor/shield rigs and mids)
- **Armor tank does NOT increase sig**
- Target Painters increase the target's sig (making them easier to hit)

#### Tanking Types

**Shield Tanking** (Kybernauts default for most doctrines)
- Uses **mid slots** for tank (Shield Extenders, Shield Boosters, Shield Hardeners)
- Frees **low slots** for damage/tracking/speed
- **Pros:** Better speed, better damage potential
- **Cons:** Larger signature radius, fewer utility mids
- Shield regen = passive or active (Shield Booster)

**Armor Tanking**
- Uses **low slots** for tank (Armor Plates, Armor Repairers, Resistance Hardeners)
- Frees **mid slots** for EWAR, cap, application modules
- **Pros:** Smaller signature radius, more utility mids
- **Cons:** Slower (armor plates reduce speed), potentially less DPS
- Armor ships often rely on buffer (raw HP) + logi, not local reps

**Hull Tanking**
- Uses structure HP (Damage Control II + Hull rigs)
- Meme but viable on certain hull-bonus ships
- Not a standard Kybernaut doctrine

#### Capacitor (Cap)
- Everything needs cap: guns, reps, MWD, tackle, hardeners
- **Cap-stable = cap regenerates faster than you spend it**
- **Cap-unstable = you eventually run dry** (can still work with cap injection / cap booster)
- Cap Boosters = mid-slot, carry charges, instant cap injection
- Neutralizers / NOS = drain enemy cap / steal it

#### Damage Application

**Turrets (Hybrid, Projectile, Energy, Precursor)**
- **Optimal range** = 100% hit chance
- **Falloff** = hit chance degrades past optimal
- **Tracking speed** = how fast your guns can swivel
- **Transversal velocity** = how fast the target is moving across your view
- Hit chance = function of (range, tracking, transversal, signature)
- If target's transversal > your tracking, you miss
- Target Painters, Webs, Grapplers help with application

**Missiles**
- Always hit if within max flight range
- **Explosion radius** vs target signature radius
- **Explosion velocity** vs target speed
- If target is fast and small, you barely scratch them
- Target's absolute speed matters (not transversal)
- RLML (Rapid Light Missile Launchers) are frigate killers

**Precursor Weapons (Triglavian)**
- **Entropic Disintegrators** = single-beam, infinite ammo, damage RAMP UP over time
- Spool mechanic: starts low, hits max after ~90 seconds continuous fire
- You want to STAY on target (no transversal issues like turrets)
- Optimal range matters a LOT
- Dampermuter's tracking computers help with range/application

#### Propulsion
- **MWD (MicroWarpdrive)** = 500% speed, massive sig bloom, uses lots of cap
- **AB (Afterburner)** = ~150% speed, no sig bloom, lower cap use
- **Scram** (Warp Scrambler, 2 points) shuts down MWD but NOT AB
- **Disruptor** (Warp Disruptor, 1 point) does NOT shut down MWD
- MWD + Scram = signature tanking (get close, orbit fast, sig blooms but you're too close)

### Tools of the Trade
1. **Pyfa** (Python Fitting Assistant) — Gold standard for theorycrafting
   - https://github.com/pyfa-org/Pyfa/releases
   - Import EFT format fits, simulate damage, cap stability, etc.
2. **EVE Workbench** — Online fitting database, browse fits by ship/role
   - https://eveworkbench.com/
3. **zKillboard losses** — See what actually dies and how it's fitted
   - Great for "what do real people fly in Pochven?"
4. **EVE Fitting Tool (EFT)** — Old but classic format, still readable
5. **EVEmon** — Skill planning, ship browser to find bonus-related fits

### How to Read a Fit (EFT Format Example)
```
[Vedmak, Pochven Hunter]

1600mm Steel Plates II
Damage Control II
Multispectrum Energized Membrane II
Multispectrum Energized Membrane II
Entropic Radiation Sink II

50MN Quad LiF Restrained Microwarpdrive
Warp Scrambler II
Stasis Webifier II
Medium Electrochemical Capacitor Booster II, Navy Cap Booster 800

Heavy Entropic Disintegrator II, Mystic M

Medium Ancillary Current Router II
Medium Trimark Armor Pump II
Medium Trimark Armor Pump II

Hobgoblin II x5

Navy Cap Booster 800 x5
```
- `[Vedmak, Pochven Hunter]` = Ship name + Fit name
- Each section = High, Medium, Low slots + Rigs + Drones + Cargo

### Fitting for Pochven (Kybernaut-Specific)

**Key Pochven Environmental Factors:**
- **No local chat** (except in station) — you never know who's in system
- **Triglavian rats** shoot ALL damage types but favor precursor (thermal/explosive)
- **Drifter/Sleeper/EDENCOM rats** also present
- **No stargates** — travel via filaments or Pochven wormholes
- **Filament travel** = arrive at random beacon, possible immediate PvP
- **Standings matter** — positive Triglavian standings = rats don't shoot you

**PvE in Pochven:**
- Vedmak / Kikimora for site running
- Active tank (Shield Booster or Armor Repairer) because sites take time
- AB preferred over MWD (no sig bloom, rats can't apply as well)
- Damage specific: Triglavian rats are weak to EM/Thermal
- **NEVER fly what you can't afford to lose**

**PvP in Pochven:**
- **Small gang / solo** = most common (Pochven isn't nullsec blob warfare)
- **Brawling** (close range) favored over kiting (due to site beacons, filament landing)
- **Scram + Web** = core tackle (shut down MWD, hold them close)
- **Triglavian ships** excel at brawling (disintegrator spool rewards staying on target)
- **Nemesis stealth bomber** for filament camping
- **Leshak** = battleship brawler, insane spooled DPS
- **Rodiva** = remote armor repair (logistics), key for small-gang sustainability

**Kybernaut Doctrine Philosophy:**
- Triglavian ships first (bonuses, aesthetics, lore)
- Shield OR armor depending on ship bonuses (Damavik = armor, Vedmak = flexible)
- MWD for fleet work, AB for solo/small gang
- Cap boosters over cap stability (burst tank)
- Always fit tackle (Scram/Web) — Pochven is a PvP zone
- Drones = Hobgoblins (thermal) for PvE, Warriors (EM) for PvP, or EC-300s (jam)

### Common Fitting Mistakes
- **Not enough cap** — dead in the water after 30 seconds
- **No tackle** — they warp away, you get nothing
- **All tank, no damage** — survive forever, kill nothing
- **All damage, no tank** — glass cannon, alpha'd off field
- **Wrong resist profile** — shield-tanking with EM holes vs Blood Raiders
- **MWD without Scram** — they just burn away
- **Wrong ammo** — shooting close-range ammo at 50km

### Recording Kybernaut-Specific Fits
When Opus or a fleet commander provides a doctrine fit:
1. **Record it here** in this knowledge base (Ship Name + Role + EFT format)
2. **Note the intended use** (Alpha Force PvP, Pochven PvE, solo, fleet)
3. **Update as metas change**

### Alpha Force Doctrine (Placeholder)
Awaiting Opus/SDC commander to provide specific ship fits.
When received, record below:
```
[SHIP NAME, ROLE]
-- fit goes here --
Purpose: 
Skill reqs:
```

---
