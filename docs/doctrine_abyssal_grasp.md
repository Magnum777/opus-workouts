# Abyssal Grasp - T1 Cruiser Brawler Doctrine vs. Kikimora Fleets

## Threat Recap

**Kikimora (Triglavian Destroyer):**
- Light Entropic Disintegrator II — spooling beam, DPS ramps 0 → 400+ over 90s
- Optimal: ~8-10km. Inside = full DPS. Outside = sharply reduced.
- Shield tank with EM hole (victim had EM reinforcer rig)
- AB fit = 400-500m/s. Slow. Can't disengage.
- Small neut = cap pressure at 6-8km
- Glass cannon destroyer — ~10k EHP

**Their strength:** Close-range spool DPS. Win by holding you at 8km for 60+ seconds.
**Their weakness:** Fragile. One weapon system. Zero range. AB = no escape.

**Brawler strategy:** Get inside their face. Scram + web them. Alpha them off the field before spool matters. Use neuts to kill their hardener.

---

## Fleet Composition (10-man squad)

| Ship | Qty | Role |
|------|-----|------|
| Vexor "Grappler" | 5 | Mainline DPS — drones + blasters + neuts |
| Thorax "Fist" | 3 | Secondary DPS — pure blaster alpha |
| Moa "Anchor" | 1 | Heavy tackle — dual web + scram |
| Blackbird "Silence" | 1 | ECM — jam their single disintegrator |

**Total cost:** ~150M ISK for the squad (cheap)

---

## The Math (Why This Works)

**1 Vexor + 1 Thorax focused fire:**
- Vexor: ~500 DPS (drones + 2 blasters)
- Thorax: ~550 DPS (5 blasters + drones)
- Combined: ~1,050 DPS
- Kikimora EHP: ~10,000
- **Time to kill: ~10 seconds**

At 10 seconds, Kikimora disintegrator spool is at ~30% of max = ~120 DPS. They barely tickle you.

**8 DPS ships (5 Vexor + 3 Thorax):**
- Total squad DPS: ~4,000+
- Kill one Kikimora every 2-3 seconds under focus fire
- 20 Kikimora fleet = dead in 40-60 seconds
- Your cruisers have 15-20k EHP each. They can't kill you fast enough.

---

## Tactics

### Landing on Grid

**0-5 seconds:**
1. ALL ships: Overheat AB, burn at the enemy. Close to scram range immediately.
2. Moa (Anchor): Pick a Kikimora, burn directly at it. Get scram + dual web.
3. Vexor/Thorax: Follow the Moa. Scram nearest Kikimora.

**5-15 seconds:**
1. Moa has a Kikimora scrammed + dual webbed. It's moving at ~100m/s. Call primary.
2. All Vexors/Thoraxes switch to that Kikimora. Blasters + drones + neuts.
3. It dies in 5-8 seconds.
4. Neuts from Vexors kill the next Kikimora's hardener before you even shoot it.

**15-30 seconds:**
1. Kikimoras panic. Their spool hasn't reached meaningful DPS yet.
2. They try to kill one Thorax. 5-6 Kikimoras shooting one cruiser = ~600 DPS at 20s spool.
3. Thorax buffer = 18k EHP. Survives 30 seconds.
4. In those 30 seconds, your squad kills 6-8 Kikimoras.
5. They break and warp.

### Critical Rules

1. **Scram + Web first, shoot second.** A Kikimora without scram can burn away (AB still works under disruptor).
2. **Neuts before guns.** Vexor neuts kill their Multispectrum Hardener = their resists drop by 30-40%. Then guns finish them.
3. **Focus fire.** 8 ships shooting 1 target = dead in seconds. 8 ships shooting 8 targets = nobody dies.
4. **Kill order:** Nearest Kikimora → next nearest. No special priority. They're all the same threat.
5. **Blackbird jams closest Kikimoras.** If a jam lands, that Kikimora does 0 DPS for 20 seconds. Free kill.

### Against Their Neuts

Kikimoras fit small neuts (from the killmail). Small neut range = ~6km.

**Solution:** Your Vexors also have small neuts. Neut war at 6km. But more importantly:
- AB + hardener + scram + web = moderate cap use
- Cap booster 400 = 4-5 injections = 60+ seconds of cap
- By the time cap runs dry, the fight is over (one side is dead)

### Against Their Spool

Disintegrator spools over ~90s. At 10s = ~30% DPS. At 30s = ~60% DPS. At 90s = 100% DPS.

**Solution:** Kill them in 10 seconds. Spool is irrelevant if they're dead.

If a Kikimora somehow lives 30+ seconds:
- Break scram for 5 seconds (pull range, re-approach)
- Spool RESETS to 0%
- Re-scram, start over

---

## Fits (EVE Copy-Paste Format)

### Vexor — "Grappler" (Mainline DPS + Neuts)

```
[Vexor, Abyssal Grasp - Grappler]

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
- DPS: ~500 (drones + blasters)
- Tank: ~18k EHP armor
- Speed: ~450m/s with AB
- Neuts: 2x Small Neut II = ~100 GJ/s cap drain
- Role: Primary DPS. Get scram + web on a Kikimora, launch drones, overheat blasters, apply neuts.

**Budget swap:** T1 blasters, T1 neuts, meta AB/web/scram. Still works. DPS drops to ~400.

---

### Thorax — "Fist" (Pure Blaster Alpha)

```
[Thorax, Abyssal Grasp - Fist]

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
- Tank: ~17k EHP armor
- Speed: ~470m/s with AB
- Role: Secondary DPS. Follow the Vexors. Scram + web, overheat blasters, delete Kikimoras.

**Alternative — Shield Thorax (more DPS, less tank):**

```
[Thorax, Abyssal Grasp - Fist (Shield)]

Heavy Ion Blaster II
Heavy Ion Blaster II
Heavy Ion Blaster II
Heavy Ion Blaster II
Heavy Ion Blaster II

50MN Quad LiF Restrained Microwarpdrive
Warp Scrambler II
Fleeting Compact Stasis Webifier
Medium Shield Extender II
Multispectrum Shield Hardener II

Magnetic Field Stabilizer II
Magnetic Field Stabilizer II
Damage Control II

Medium Core Defense Field Extender I
Medium Core Defense Field Extender I
Medium Anti-EM Screen Reinforcer I

Warrior II x5

Navy Cap Booster 400 x10
```

**Shield variant stats:** ~600 DPS, ~15k EHP shield, 1.4km/s with MWD. Higher sig but faster. Use if you need to chase or disengage. Armor variant recommended for pure brawling.

---

### Moa — "Anchor" (Heavy Tackle)

```
[Moa, Abyssal Grasp - Anchor]

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
- Role: Tackle. Pick a Kikimora, burn at it, scram + dual web. It stops moving. Fleet kills it.

**Why Moa for tackle:** 5 mids = scram + 2x web + MWD + shield extender. Dual web = Kikimora goes from 500m/s to ~100m/s. It can't escape. It can't create transversal. Blasters apply perfectly.

**Note:** Moa uses MWD (not AB) because it needs to close distance fast to tackle. Once scram is on, MWD is shut down, but they're already held.

---

### Blackbird — "Silence" (ECM)

```
[Blackbird, Abyssal Grasp - Silence]

Ladar Jammer II
Magnetometric Jammer II
Radar Jammer II
Gravimetric Jammer II

50MN Quad LiF Restrained Microwarpdrive
Large Shield Extender II
Multispectrum Shield Hardener II
EM Shield Hardener II

Signal Distortion Amplifier II
Signal Distortion Amplifier II

Medium Particle Dispersion Projector I
Medium Particle Dispersion Projector I
Medium Particle Dispersion Projector I

Warrior II x3
```

**Stats:**
- Jam strength: ~12 per jammer
- Jam range: ~70-80km (with rigs)
- Tank: ~12k EHP shield
- Role: ECM backup. Stay at 50-70km. Jam closest Kikimoras.

**Sensor type note:** Triglavian ships likely use RADAR or their own sensor type. Fit all four jammer types and you'll hit the right one. ECM is RNG (~40-50% chance per cycle) but when it lands, that Kikimora does 0 DPS for 20 seconds.

---

## Target Calling Priority

1. **Moa calls primary** — nearest Kikimora that Moa has scrammed
2. **All DPS switches** — Vexors launch drones, Thoraxes overheat blasters
3. **Vexors apply neuts** to the same target (or next target if cap allows)
4. **Blackbird jams** any Kikimora shooting the Moa or a Thorax
5. **Next primary called** when current dies — always nearest, always scrammed

**Focus fire is mandatory.** A Kikimora at 50% hull still does full spooled DPS. Kill it to 0%.

---

## Skill Requirements

**Vexor pilots:**
- Gallente Cruiser IV+ (drone bonuses)
- Drones V, Drone Interfacing IV+, Light/Medium/Heavy Drone Operation IV+
- Hybrid Turrets IV+ (for blasters)
- Energy Grid Upgrades IV (for neuts)

**Thorax pilots:**
- Gallente Cruiser IV+ (hybrid bonuses)
- Hybrid Turrets IV+, Medium Hybrid Turret V (for T2 guns)
- Gunnery support: Motion Prediction, Surgical Strike, Rapid Firing IV+

**Moa pilots:**
- Caldari Cruiser IV+ (shield resist bonuses)
- Hybrid Turrets IV+
- Navigation IV, Evasive Maneuvering IV (for MWD tackle)

**Blackbird pilots:**
- Electronic Warfare IV+ (jam strength)
- Frequency Modulation IV, Long Distance Jamming IV

---

## Why This Doctrine Wins

1. **Race condition:** You kill them in 10s. Their spool needs 90s. You win the race.
2. **Neuts break their tank:** Vexor neuts kill Multispectrum Hardener = their shield resists collapse.
3. **Dual web holds them:** Moa with 2x webs = Kikimora is a stationary target. Can't escape. Can't kite.
4. **Drones don't miss:** Vexor drones apply perfectly to destroyer sig. No tracking issues.
5. **ECM is binary:** Blackbird jams = that Kikimora is removed from the fight for 20s. Free kill.
6. **Buffer survives spool:** 18k EHP buys 20-30 seconds. That's enough time to kill 4-6 Kikimoras.
7. **Cost:** 10 T1 cruisers (~150M) vs. 20 T2 destroyers (~400M+). Trade 1:1 and you win ISK.

---

## Why It Might Fail

1. **No focus fire:** 8 ships shooting 8 targets = nobody dies. Kikimoras spool up. You die.
2. **Moa dies first:** If enemy shoots Moa before it gets tackle, you lose your anchor. Have a backup Thorax ready to scram.
3. **They have MWD Kikimoras:** If some Kikimoras are MWD (not AB), they can create range and spool. Call MWD targets as priority.
4. **They have logi (Rodiva):** Remote reps make them harder to kill. Prioritize logi if visible, or accept longer fights.
5. **They have 40+ Kikimoras:** Numbers matter. 10 cruisers vs. 40 destroyers = you die. Doctrine assumes rough parity (10-20 enemy).
6. **You let them spool:** If a fight drags to 60+ seconds, spooled Kikimoras do 400+ DPS each. 10 Kikimoras = 4,000 DPS. Your tank breaks. **Kill fast.**

---

## Quick Reference — The Brawl Flow

```
1. Land → Overheat AB → Burn at them
2. Moa → Scram + dual web nearest Kikimora
3. Vexors → Scram + web + neuts + drones + blasters
4. Thoraxes → Scram + web + blasters (overheated)
5. Blackbird → Jam closest threats
6. Kill in 10 seconds → Next primary → Repeat
7. Loot field → Extract
```

**Time to victory:** 40-60 seconds for a 20-man Kikimora fleet.

**Kybernauts call it:** "Get close. Get personal. Get dead — them, not us."

---

*Doctrine designed by Nova for Kybernauts Clade. Test in Pyfa. Fly what you can afford to lose.*
