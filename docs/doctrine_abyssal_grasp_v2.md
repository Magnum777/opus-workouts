# Abyssal Grasp v2 - T1 Cruiser Brawler Doctrine vs. Dual-Prop Armor Kikimora Fleets

## Threat Analysis (Actual Fit from zKill 135760034)

**Actual Kikimora Fit Decoded:**

```
[Kikimora, Actual Enemy Fit]

Light Entropic Disintegrator II
Small Energy Neutralizer II

5MN Cold-Gas Enduring Microwarpdrive
1MN Afterburner II
LFT Enduring Sensor Dampener

Entropic Radiation Sink II
Multispectrum Coating II
Multispectrum Energized Membrane II
Damage Control II

Small Trimark Armor Pump I
Small Trimark Armor Pump I
Small Trimark Armor Pump I

Cargo: Warp Scrambler II, 5MN MWD, Small Remote Armor Repairer, Tracking Disruptor, Guidance Disruptor, multiple EWAR scripts, ammo, booster
```

**What This Tells Us:**

1. **Dual Propulsion (MWD + AB):** This is a CLOSER. MWD to burn at kiters (2km/s), AB for when scram shuts down MWD. They can chase anything.
2. **Armor Buffer Tank (Trimarks x3 + DC + MEM + Coating):** ~12-15k EHP. NOT a glass cannon. Survives alpha better.
3. **Sensor Dampener Fitted:** Reduces your lock range. A cruiser that normally locks 70km might drop to 30-40km.
4. **Small Energy Neutralizer:** Cap warfare at 6-8km.
5. **Entropic Radiation Sink II:** Spooled DPS is their kill weapon.
6. **Cargo Flexibility:** They carry scram, remote repper, tracking disruptor, and guidance disruptor in cargo. They SWAP mids based on fight type.
   - **Damp config (standard):** Can reduce your lock range but CANNOT hold you down (no scram)
   - **Scram config (aggressive):** Swaps damp for scram = can hold you but loses damps
   - **TD config:** Swaps damp for tracking disruptor = hurts your turret tracking
   - **Remote rep:** Two Kikimoras can rep each other if they coordinate

**Critical Weakness:** They MUST choose between tackle and EWAR. They cannot have both simultaneously without docking.

---

## Kikimora Threat Profile

| Metric | Value | Implication |
|--------|-------|-------------|
| Speed (MWD) | ~2,000 m/s | Can close 30km in 15s. Kiting is HARD. |
| Speed (AB) | ~400 m/s | Slow in brawl. Web them and they're nearly stationary. |
| Optimal range | ~8-10km | Must be inside this to do damage. |
| Spooled DPS | ~350-450 | At 90s spool. At 10s = ~30% = ~120 DPS. |
| Tank | ~12-15k EHP buffer | Survives 5-8 seconds of focused fire. Not 1-shot. |
| Neut range | ~6-8km | Kills active tank cap. Buffer is neut-immune. |
| Damp range | ~40-50km | Reduces your lock range by 30-50%. |
| Sig radius | ~65m | Destroyer sig. Cruiser guns apply reasonably. |
| Cargo scram | Swappable | If you see scrams, they gave up damps. |
| Cargo remote rep | Swappable | Fleet logistics if they coordinate. |

**The Race:** Can you kill them in <15 seconds before their spool reaches lethal levels AND before they MWD + scram a kiter?

---

## Doctrine: "Abyssal Grasp v2" — Revised Brawler Comp

### Philosophy
**Punch through their buffer before spool wins. Scram + dual web to hold them. Neuts to kill their MWD cap. DPS wins the race.**

Since they have ~12-15k EHP and can chase kiters, we must brawl. But we must brawl with enough DPS to kill them in 10-15 seconds, not 5.

**Key changes from v1:**
1. **Every ship MUST have a web.** The Kikimora has NO web fitted. If we web them, their AB speed drops from 400m/s to ~80m/s. They can't escape. They can't create transversal.
2. **Buffer tank over active tank.** Their small neut kills Shield Boosters and Armor Repairers. Buffer (plates + DC + resists) is immune to neuts.
3. **Neuts on Vexors kill their MWD cap.** Without cap, MWD dies. They can only AB at 400m/s (80m/s when webbed).
4. **Focus fire is CRITICAL.** 12k EHP means one cruiser shooting = 25s to kill. Eight cruisers = 3s. Call primary. Switch together. No exceptions.
5. **Moa is the anchor.** Dual web + scram holds them while fleet kills.

---

### Fleet Composition (10-man squad)

| Ship | Qty | Role |
|------|-----|------|
| Vexor "Grappler" | 4 | Mainline DPS — drones + blasters + neuts |
| Thorax "Fist" | 3 | Secondary DPS — pure blaster alpha |
| Moa "Anchor" | 1 | Heavy tackle — dual web + scram + tank |
| Arbitrator "Blindside" | 1 | TDs + drone DPS + neuts |
| Griffin "Snare" | 1 | Fast tackle + ECM jam |

**Total cost:** ~160M ISK for the squad (still cheap)

---

## Detailed Math (Why This Wins)

**4 Vexors + 3 Thoraxes focused fire on ONE Kikimora:**
- 4x Vexor DPS: ~500 each = 2,000 DPS (drones + blasters + neuts don't add DPS but kill cap)
- 3x Thorax DPS: ~550 each = 1,650 DPS
- **Combined: ~3,650 DPS**
- Kikimora EHP: ~13,000
- **Time to kill: ~4 seconds**

At 4 seconds, disintegrator spool is at ~5% = ~20 DPS. They barely scratch you.

**With Arbitrator drones + Griffin:**
- Total DPS: ~4,000+
- Kill one Kikimora every 3-4 seconds under focus fire
- 20 Kikimora fleet = dead in 60-80 seconds
- Your cruisers have 15-20k EHP buffer each. Even if 10 Kikimoras spool to 50% (~200 DPS each) = 2,000 DPS. Your tank survives 8-10 seconds. That's enough time to kill 2-3 Kikimoras, reducing incoming DPS.

---

## Fits (EVE Copy-Paste Format)

### Vexor — "Grappler" (Mainline DPS + Neuts)

```
[Vexor, Abyssal Grasp v2 - Grappler]

Heavy Ion Blaster II
Heavy Ion Blaster II
Small Energy Neutralizer II
Small Energy Neutralizer II

10MN Afterburner II
Fleeting Compact Stasis Webifier
Warp Scrambler II
Multispectrum Energized Membrane II

1600mm Steel Plates II
IFFA Compact Damage Control
Drone Damage Amplifier II
Drone Damage Amplifier II

Medium Trimark Armor Pump I
Medium Anti-EM Pump I
Medium Anti-Explosive Pump I

Ogre II x4
Warrior II x5
Hobgoblin II x5

Navy Cap Booster 400 x10
```

**Stats:**
- DPS: ~500 (blasters + drones)
- Tank: ~18k EHP armor (buffer — neut immune)
- Speed: ~450m/s with AB
- Neuts: 2x Small Neut II = ~100 GJ/s cap drain
- Web: 60% speed reduction on target
- Role: Primary DPS. Scram + web a Kikimora. Neuts kill its MWD cap. Drones + blasters kill it in 4s under focus fire.

**Why this fit:**
- **Buffer tank (plates + DC) = immune to their neut.** If you fit a Shield Booster or Armor Repairer, their neut kills it. Buffer just sits there.
- **2x small neuts = 100 GJ/s drain.** Their MWD uses ~40 GJ/s. Their hardener uses ~10 GJ/s. Their disintegrator uses ~5 GJ/s. Total: ~55 GJ/s. Your neuts drain 100 GJ/s. Their cap goes NEGATIVE. MWD dies within 5 seconds.
- **Web = 60% speed reduction.** Kikimora AB = 400m/s. Webbed = 160m/s. Moa web stacks on top = dual web = ~80m/s. They cannot escape. Cannot create transversal. Your blasters track perfectly.

---

### Thorax — "Fist" (Pure Blaster Alpha)

```
[Thorax, Abyssal Grasp v2 - Fist]

Heavy Ion Blaster II
Heavy Ion Blaster II
Heavy Ion Blaster II
Heavy Ion Blaster II
Heavy Ion Blaster II

10MN Afterburner II
Fleeting Compact Stasis Webifier
Warp Scrambler II
Multispectrum Energized Membrane II

1600mm Steel Plates II
IFFA Compact Damage Control
Magnetic Field Stabilizer II
Magnetic Field Stabilizer II

Medium Trimark Armor Pump I
Medium Anti-EM Pump I
Medium Anti-Explosive Pump I

Warrior II x5

Navy Cap Booster 400 x10
```

**Stats:**
- DPS: ~550 (5 blasters + drones)
- Tank: ~17k EHP armor (buffer)
- Speed: ~470m/s with AB
- Role: Secondary DPS. Follow the Vexors. Scram + web, overheat blasters, delete Kikimoras.

**Why this fit:**
- **5 blasters = highest cruiser DPS in the game.** No other T1 cruiser matches Thorax raw blaster output.
- **Buffer tank = neut immune.** Same logic as Vexor.
- **Web = mandatory.** Every Thorax must have a web. If you don't web them, their 400m/s AB creates transversal. Blasters miss. You die.

---

### Moa — "Anchor" (Heavy Tackle)

```
[Moa, Abyssal Grasp v2 - Anchor]

Heavy Electron Blaster II
Heavy Electron Blaster II
Heavy Electron Blaster II
Heavy Electron Blaster II
Heavy Electron Blaster II

50MN Quad LiF Restrained Microwarpdrive
Warp Scrambler II
Fleeting Compact Stasis Webifier
Stasis Webifier II
Medium Shield Extender II

Magnetic Field Stabilizer II
Damage Control II

Medium Core Defense Field Extender I
Medium Core Defense Field Extender I
Medium Anti-EM Screen Reinforcer I

Warrior II x3

Navy Cap Booster 400 x10
```

**Stats:**
- DPS: ~350 (blasters + drones)
- Tank: ~20k EHP shield
- Speed: ~1.3km/s with MWD
- Role: Primary tackle. Burn at a Kikimora, scram + dual web. It stops moving. Fleet kills it.

**Why this fit:**
- **MWD (not AB) to close distance.** Kikimoras have MWD too. If your Moa uses AB, they can outpace you. MWD ensures you get tackle first.
- **Dual web = 80% speed reduction stacked.** Kikimora AB = 400m/s. One web = 160m/s. Two webs = ~80m/s. They're a stationary target.
- **Shield buffer = neut-resistant (not immune).** Shield Extender is passive. No cap needed. But hardener uses cap — if neut hits, hardener cycles off. Still, 20k raw shield is decent buffer.
- **Scram = shuts down their MWD.** Once scrammed, their MWD dies. They must AB at 400m/s (webbed = 80m/s). Dead.

**Critical role:** The Moa is the fleet anchor. If the Moa dies before getting tackle, call a Thorax to scram. Always have a backup tackle ready.

---

### Arbitrator — "Blindside" (TDs + Drone DPS + Neuts)

```
[Arbitrator, Abyssal Grasp v2 - Blindside]

Small Energy Neutralizer II
Small Energy Neutralizer II
Small Energy Neutralizer II

50MN Quad LiF Restrained Microwarpdrive
Tracking Disruptor II, Optimal Range Disruption Script
Warp Scrambler II
Fleeting Compact Stasis Webifier

Damage Control II
Drone Damage Amplifier II
Drone Damage Amplifier II
400mm Steel Plates II

Medium Drone Speed Augmentor I
Medium Drone Speed Augmentor I
Medium Anti-Explosive Pump I

Warrior II x5

Optimal Range Disruption Script x1
Tracking Speed Disruption Script x1
Navy Cap Booster 400 x10
```

**Stats:**
- TD strength: 1x Tracking Disruptor II with range script = reduce turret optimal by ~35-40%
- Drone DPS: ~180 (5x Warrior II with DDA IIs)
- Neuts: 3x Small Neut II = ~150 GJ/s cap drain
- Tank: ~14k EHP armor
- Speed: ~1.2km/s with MWD
- Role: EWAR + cap warfare + secondary DPS. Burn at enemy, scram + web + neuts + TDs.

**Why this fit:**
- **3x neuts = 150 GJ/s cap drain.** Their MWD uses 40 GJ/s. Total cap use: ~55 GJ/s. Your neuts drain 150. Their cap collapses instantly. MWD dies. Hardener dies. Disintegrator spool resets if cap runs dry.
- **TD with range script = disintegrator optimal drops from 10km to ~6km.** At 6km optimal, their damage at 8-10km (where we brawl) drops significantly. Less incoming DPS = more time to kill them.
- **Drones + neuts = no cap use for drone DPS.** Even if you're neuted dry, drones keep shooting.
- **MWD to close fast.** You need to be in neut + scram range (8km). MWD gets you there.

**Target priority:** Arbitrator should neut + TD the Kikimora that the Moa is tackling. If cap allows, neut a second Kikimora.

---

### Griffin — "Snare" (Fast Tackle + ECM)

```
[Griffin, Abyssal Grasp v2 - Snare]

Light Missile Launcher II, Caldari Navy Scourge Light Missile

1MN Afterburner II
Initiated Compact Warp Scrambler
Fleeting Compact Stasis Webifier
Multispectrum Shield Hardener II

Signal Distortion Amplifier II
Signal Distortion Amplifier II

Small Particle Dispersion Projector I
Small Particle Dispersion Projector I
```

**Stats:**
- Speed: ~750m/s with AB
- ECM strength: ~8-10 (with SDA IIs)
- Role: Fast tackle + jam. AB (not MWD) so if they scram you, your prop still works.

**Why this fit:**
- **AB = scram-proof propulsion.** If they swap damp for scram and scram you, your AB keeps running. MWD would die.
- **Scram + web = hold Kikimoras that try to escape.** If a Kikimora tries to burn away from the Moa, Griffin catches it.
- **ECM jam = 40-50% chance to completely remove one Kikimora from the fight for 20 seconds.** When jam lands, that Kikimora's disintegrator stops. Free kill.
- **Frigate sig = 35m.** Kikimora disintegrator tracks cruisers well but struggles with frigates. Harder for them to apply DPS to you.

---

## Tactics: The Brawl

### Landing on Grid (Jumping Into Them)

**0-5 seconds:**
1. **ALL ships: Overheat prop, burn at the enemy.** Moa uses MWD. Vexors/Thoraxes use AB. Griffin uses AB.
2. **Moa (Anchor):** Pick the CLOSEST Kikimora. Burn directly at it. Lock it.
3. **Vexors/Thoraxes:** Follow the Moa. Lock nearest Kikimoras.
4. **Arbitrator:** Burn at the Moa's target. Prepare neuts + TDs.
5. **Griffin:** Pick a Kikimora on the flank. Get ready to scram if it tries to escape.

**5-10 seconds:**
1. **Moa gets in scram range (8km).** Scram + web 1. Web 2. Call primary on comms.
2. **Vexors:** Scram + web the same target. Apply neuts. Launch drones (if not already out).
3. **Thoraxes:** Scram + web. Overheat blasters. Open fire.
4. **Arbitrator:** Scram + web. Apply neuts. TD with range script.
5. **Griffin:** Scram + web a secondary target or the primary.

**Target dies in 3-5 seconds.** 8 ships shooting one 13k EHP Kikimora = 3,650 DPS. Dead before spool matters.

**10-20 seconds:**
1. **Moa calls next primary:** nearest Kikimora.
2. **All ships switch.** Drones switch. Blasters switch.
3. **Vexor neuts:** If cap allows, start neuts on the NEXT target before the current one dies.
4. **Arbitrator:** TD the next target, continue neuts.
5. **Second Kikimora dies in 3-5 seconds.**

**20-40 seconds:**
1. **Kikimoras panic.** Their spool hasn't reached lethal levels yet.
2. Some try to MWD away. Moa + Griffin scram holds them.
3. Some try to shoot the Moa. Moa has 20k EHP. Survives 15-20 seconds.
4. In that time, your squad kills 4-6 Kikimoras.
5. Incoming DPS drops by 4-6x ~120 DPS (early spool) = ~500-700 DPS less.
6. Your fleet wins the war of attrition.

**40+ seconds:**
1. If Kikimoras have remote repper in cargo and coordinate reps, fight extends.
2. Solution: Focus fire STILL works. 3,650 DPS overwhelms 1-2 small remote reps (~100 HP/s each).
3. Kill the repped target anyway. Move to next.

---

## Target Calling Rules

1. **Moa calls primary** — always the nearest Kikimora that Moa has scrammed
2. **ALL DPS switches immediately** — no exceptions. Focus fire wins.
3. **Vexors apply neuts to primary** (or next target if cap allows)
4. **Arbitrator TDs primary** (range script)
5. **Griffin jams any Kikimora shooting the Moa**
6. **Next primary called the instant current dies**

**Focus fire is non-negotiable.** A Kikimora at 50% hull does full spooled DPS. Only dead Kikimoras do 0 DPS.

---

## Critical Mechanics

### Why Buffer Tank (Not Active Tank)

Kikimora small neut = ~50 GJ/s drain. Their neuts reach 6-8km.

**Active tank (bad):**
- Shield Booster II = ~100 GJ per cycle. Neut drains 50 GJ/s. Cap dies. Booster stops. You die.
- Armor Repairer II = ~80 GJ per cycle. Same problem.

**Buffer tank (good):**
- 1600mm Steel Plate = passive. Uses ZERO cap. Neuts do NOTHING to your tank.
- Trimark rigs = passive. Zero cap.
- DC II = passive. Zero cap.

**Verdict:** Buffer tank is MANDATORY against this Kikimora fit. Active tank = dead to neuts.

### Why Web on Every Ship

Kikimora has NO web fitted. Their standard config = MWD + AB + damp.

**If you web them (60% reduction):**
- Kikimora AB speed: 400m/s → 160m/s
- With Moa dual web: 400m/s → ~80m/s
- They cannot create transversal. Your blasters track perfectly.
- They cannot escape. Scram + web = they're stuck.

**If you DON'T web them:**
- Kikimora AB at 400m/s creates transversal.
- Heavy blasters have poor tracking.
- You miss. They spool. You die.

**Verdict:** Web is MANDATORY on every ship. No exceptions.

### Why Neuts on Vexors + Arbitrator

Kikimora dual prop = cap hungry:
- MWD: ~40 GJ/s
- AB: ~5 GJ/s (when MWD is off)
- Hardener: ~10 GJ/s
- Disintegrator: ~5 GJ/s
- Neut: ~20 GJ/s (when they use it)
- Total: ~40-80 GJ/s depending on what's active

**Vexor neuts (2x small):** ~100 GJ/s drain
**Arbitrator neuts (3x small):** ~150 GJ/s drain

Combined: ~250 GJ/s drain on one Kikimora if multiple ships neut it.

**Result:** Their cap goes NEGATIVE in 3-5 seconds.
- MWD dies → they can't chase or escape
- Hardener cycles off → resists drop by 30-40% → you kill them faster
- Disintegrator might cycle off if cap hits zero → spool resets

**Verdict:** Neuts are CRITICAL. Kill their cap, kill their mobility, kill their tank.

### Why the Moa Uses MWD (Not AB)

In v1, I said Moa should use MWD. Here's why that's correct for this specific threat:

**Kikimoras have MWD.** If your Moa uses AB (~450m/s) and their Kikimora uses MWD (~2,000m/s), they DICTATE range. They can:
- Keep at 15km (outside your scram) and shoot you
- Burn away if losing
- Choose engagement range

**Moa with MWD (~1,300m/s):**
- Can close on MWDing Kikimoras
- Once scram is on, their MWD dies
- Your MWD also dies (scrammed), but you're already in tackle range
- Both sides on AB, but you have web → you win

**Verdict:** MWD on Moa is mandatory. AB Moa cannot catch MWD Kikimoras.

### The Dampener Problem

Kikimoras fit sensor damps. This reduces your lock range.

**Effect on our fleet:**
- Cruiser base lock range: ~70km
- After 1x damp (range script): ~45km
- After 2x damps: ~30km
- After 3x damps: ~20km

**Impact on brawling:**
- At 8km scram range: damps are irrelevant. You're well inside dampened lock range.
- Damps only matter if you're trying to kite at 30km+.
- Since we're brawling at 5-10km, damps do NOTHING to us.

**Verdict:** Their damps are a non-issue in a brawl. They should swap to scram if they're smart.

### The Cargo Scram Problem

Kikimoras carry scram in cargo. They might swap damper for scram.

**If they swap to scram:**
- They can hold you down
- They lose damps
- Straight brawl → our doctrine wins

**If they keep damps:**
- They can't hold you down
- You can always overheat MWD/AB and escape if losing
- They might try to reduce your lock range and MWD away

**Counter:** If you see them MWDing away without scramming you, they're in damp config. Just chase and scram. They can't escape if you have web.

---

## Variants

### Budget Version (T1 modules)
Replace T2 modules with meta equivalents:
- `Heavy Ion Blaster I` instead of II (lose ~15% DPS)
- `10MN Monopropellant Enduring Afterburner`
- `Fleeting Compact Stasis Webifier` (keep this — webs are cheap)
- `Warp Scrambler I`
- `1600mm Rolled Tungsten Compact Plates`
- `Magnetic Field Stabilizer I`
- `Drone Damage Amplifier I`

**Cost drops to ~10M per Vexor/Thorax. DPS drops by ~20%. Still viable.**

### "Iron Fist" — Moa-Heavy Variant
If you need more tackle:

Swap 1 Vexor for a second Moa:
- 3x Vexor, 3x Thorax, 2x Moa, 1x Arbitrator, 1x Griffin
- 2 Moas = 4 webs total. Nothing escapes.
- Less DPS but more tackle security.

### "Ghost Hand" — Celestis Variant
If you want to counter their damps:

Replace Arbitrator with Celestis:
```
[Celestis, Abyssal Grasp v2 - Ghost Hand]

Light Missile Launcher II, Caldari Navy Scourge Light Missile x3

50MN MWD II
Remote Sensor Dampener II, Targeting Range Dampening Script x3

Damage Control II
Drone Damage Amplifier II

Medium Ionic Field Projector I x3

Warrior II x3
```

**Role:** Damp THEIR lock range. If both sides can't lock past 20km, the fight happens at brawling range. Which is where we win.

---

## Skill Requirements

**Vexor pilots:**
- Gallente Cruiser IV+ (drone bonuses)
- Drones V, Drone Interfacing IV+, Medium/Heavy Drone Operation IV+
- Hybrid Turrets IV+ (for blasters)
- Energy Grid Upgrades IV (for neuts)

**Thorax pilots:**
- Gallente Cruiser IV+ (hybrid bonuses)
- Medium Hybrid Turret V (for T2 guns)
- Gunnery support: Motion Prediction, Surgical Strike, Rapid Firing IV+

**Moa pilots:**
- Caldari Cruiser IV+ (shield resist bonuses)
- Hybrid Turrets IV+
- Navigation IV, Evasive Maneuvering IV (for MWD tackle)

**Arbitrator pilots:**
- Amarr Cruiser IV+ (drone bonus)
- Weapon Disruption IV+ (TD strength)
- Energy Grid Upgrades IV (for neuts)
- Drone Interfacing IV+

**Griffin pilots:**
- Electronic Warfare IV+ (jam strength)
- Caldari Frigate IV+ (shield bonuses)

---

## Why This Doctrine Wins

1. **Buffer = neut immune.** Their small neut does nothing to plates + DC. Active tank dies.
2. **Web = transversal destroyed.** Kikimora has no web. If we web them, they can't create transversal. Blasters track perfectly.
3. **Neuts = cap warfare wins.** 250 GJ/s drain on one Kikimora = MWD dies, hardener dies, spool resets.
4. **DPS race won.** 3,650 focused DPS kills 13k EHP in 4 seconds. Spool irrelevant.
5. **MWD Moa catches MWD Kikimoras.** Dictates engagement. Scram shuts down their prop.
6. **Dual web Moa = escape impossible.** 80m/s Kikimora is a stationary target.
7. **Griffin jam = free removal.** 40-50% chance to take one Kikimora offline for 20s.
8. **Cost:** 10 T1 cruisers (~160M) vs. 20 T2 destroyers with faction mods (~600M+). Trade 1:1 = you win ISK.

---

## Why It Might Fail

1. **No focus fire:** 8 ships shooting 8 targets = nobody dies. Kikimoras spool to 90s = 400 DPS each. 20 Kikimoras = 8,000 DPS. You die in 2 seconds.
   - **Solution:** DRILL focus fire. Call primary. Switch together. No exceptions.

2. **Moa dies before tackle:** If enemy shoots Moa first, you lose anchor.
   - **Solution:** Backup tackle: Thorax #1 should be ready to scram. Call it on comms.

3. **They have 40+ Kikimoras:** Numbers matter.
   - **Solution:** Don't engage 40 with 10. Doctrine assumes 10-25 enemy.

4. **Remote rep coordination:** If 2 Kikimoras rep each other effectively, fight extends.
   - **Solution:** Still focus fire. 3,650 DPS overwhelms 2x small remote reps. Kill repped target anyway.

5. **They all swap to scram config:** No damps, all scrams. More tackle pressure.
   - **Solution:** Straight brawl. Our web + scram beats their scram + no web. We hold transversal advantage.

6. **You let them spool past 30s:** At 30s spool, ~250 DPS per Kikimora. 15 Kikimoras = 3,750 DPS. Your buffer breaks.
   - **Solution:** Kill in 4s. Focus fire. No exceptions.

7. **Bad piloting:** Thorax orbits at 15km instead of 500m. In blaster falloff. Misses. Dies.
   - **Solution:** Approach to 500m. Keep at range 500m. Don't orbit at default (which might be 5-10km).

---

## Quick Reference — The Brawl Flow

```
0s:  Land → Overheat prop → Burn at them
5s:  Moa scrams + webs nearest Kikimora → Calls primary
8s:  All ships scram + web primary → Vexors neuts → Thoraxes overheat blasters
10s: Primary dies (4s of 3,650 DPS into 13k EHP)
12s: Moa calls next primary
15s: Second primary dies
20s: Kikimoras panic. Some try to MWD away. Griffin/Thorax catches them.
30s: 5-6 Kikimoras dead. Incoming DPS halved. You win.
60s: Loot field → Extract
```

**Time to victory:** 30-60 seconds against 20 Kikimoras.

**Kybernauts call it:** "Neut their cap. Web their speed. Scram their hope."

---

*Doctrine designed by Nova for Kybernauts Clade. Updated 2026-06-01 based on actual enemy fit intel. Test in Pyfa. Fly what you can afford to lose.*
