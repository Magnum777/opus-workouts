# Abyssal Edge - T1 Cruiser Doctrine vs. Omen Navy Issue Kiting Fleet

## Threat Analysis (from zKill 135912809)

**Enemy Composition:**
- **14x Omen Navy Issue** (mainline DPS) — Amarr cruiser with 25% laser damage + 10% tracking bonuses per level
  - Heavy Beam Laser II + Scorch = ~400 DPS at 35+20km optimal+falloff
  - Fast (MWD ~2km/s), strong application, good range
- **2x Hyena** (tackle/EWAR) — Minmatar EWAR frigate with 90% web strength bonus
  - Target Painter II + Warp Disruptor + Stasis Webifier
  - One web = you're dead in the water for lasers
- **1x Stork + 1x Bifrost** (Command Destroyers) — Fleet boosts (skirmish/armor/shield)
- **Warrior II drones** — anti-frigate/destroyer
- **Light Missile Launchers** on support

**The Problem:**
Omen NIs kite at 35-50km with heavy beam lasers. Hyenas web you to 10% speed and paint you, making lasers apply perfectly. This is a **range-dictation + application** doctrine. If they control range, they win.

---

## Doctrine: "Abyssal Edge" — Thorax Brawler + Celestis Support

### Philosophy
**Get inside their optimal. Kill their tackle. Brawl.**

Lasers have terrible tracking at close range. Beam lasers are long-range weapons — inside 10km their tracking collapses. The Hyena is the linchpin — kill it and their web/paint support vanishes.

**Core principle:** Shield-tank for speed + sig, not armor. We need to close distance FAST.

---

### Mainline: Thorax ("Edgebreaker")

```
[Thorax, Abyssal Edge - Edgebreaker]

Heavy Ion Blaster II, Void M
Heavy Ion Blaster II, Void M
Heavy Ion Blaster II, Void M
Heavy Ion Blaster II, Void M
Heavy Ion Blaster II, Void M

50MN Quad LiF Restrained Microwarpdrive
Fleeting Compact Stasis Webifier
Warp Scrambler II
Medium Shield Extender II

Magnetic Field Stabilizer II
Magnetic Field Stabilizer II
Magnetic Field Stabilizer II
Damage Control II

Medium Anti-EM Screen Reinforcer I
Medium Core Defense Field Extender I
Medium Polycarbon Engine Housing I

Warrior II x5

Navy Cap Booster 400 x10
```

**Stats (all V skills, with pyfa):**
- **DPS:** ~520 (Void M, 5 guns + 5 Warriors)
- **Tank:** ~14k EHP shield (EM hole patched)
- **Speed:** ~1.5km/s with MWD
- **Cap:** ~2min with MWD, cap booster for tackle/neuts
- **Range:** 4.5km optimal (Void), 8km falloff — must be SCRAM range
- **Cost:** ~12M ISK hull + fit

**Role:** Primary DPS. Overheat MWD on landing, burn directly at enemy fleet. Primary targets: **Hyenas first**, then Omen NIs that get scrammed. Do NOT shoot Storks/Bifrosts unless they're the only thing in range.

---

### Support A: Celestis ("Blindfold")

```
[Celestis, Abyssal Edge - Blindfold]

Light Missile Launcher II, Caldari Navy Scourge Light Missile
Light Missile Launcher II, Caldari Navy Scourge Light Missile
Light Missile Launcher II, Caldari Navy Scourge Light Missile

50MN Quad LiF Restrained Microwarpdrive
Remote Sensor Dampener II, Scan Resolution Dampening Script
Remote Sensor Dampener II, Targeting Range Dampening Script
Remote Sensor Dampener II, Targeting Range Dampening Script
Warp Disruptor II

Mark I Compact Reactor Control Unit
Damage Control II

Medium Ionic Field Projector I
Medium Ionic Field Projector I
Medium Ionic Field Projector I

Warrior II x3

Targeting Range Dampening Script x2
Scan Resolution Dampening Script x2
```

**Stats:**
- **Damps:** 3x dampeners with range scripts = reduce Omen NI lock range from ~70km to ~25km
- **Speed:** ~1.4km/s with MWD
- **Tank:** ~8k EHP
- **DPS:** ~100 (light missiles — kills Warrior drones, finishes Hyenas)

**Role:** EWAR support. Stay at 30-40km from enemy. Damp the Omen NIs so they can't lock past 25km. This forces them to either:
1. Burn closer (into Thorax blaster range — good)
2. Sit blind and wait (good)
3. Try to kill Celestises (they're fragile but fast)

**Critical:** Damps are NOT jams. They always work (no RNG). Three range damps on one Omen NI = lock range ~20km. They literally cannot shoot at range.

---

### Support B: Blackbird ("Shadow")

```
[Blackbird, Abyssal Edge - Shadow]

EM Jammer II
Ladar Jammer II
Magnetometric Jammer II
Radar Jammer II

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
- **Jam strength:** ~12 per jammer (with SDA IIs and skills)
- **Jam range:** ~75km (with rigs)
- **Tank:** ~10k EHP
- **Speed:** ~1.2km/s

**Role:** ECM backup. If damps aren't enough, jam Hyenas and Storks. Storks/Bifrosts are Caldari (Gravimetric = Magnetometric jammer). Hyenas are Minmatar (Ladar jammer). Omen NIs are Amarr (Radar jammer).

**ECM is RNG** — not reliable, but when it hits it completely removes a target from the fight.

---

### Tackle: Griffin ("Snare") — Optional

If you have frigate pilots:

```
[Griffin, Abyssal Edge - Snare]

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

**Role:** Fast tackle + ECM. AB (not MWD) so scrams shut down enemy MWD but yours keeps running. Jam Hyenas, scram Omen NIs that get separated. Die gloriously so Thoraxes live.

---

## Fleet Composition (10-man squad example)

| Ship | Qty | Role |
|------|-----|------|
| Thorax (Edgebreaker) | 6 | Mainline DPS |
| Celestis (Blindfold) | 2 | Sensor Damps |
| Blackbird (Shadow) | 1 | ECM backup |
| Griffin (Snare) | 1 | Fast tackle + jam |

**Total doctrine cost:** ~100M ISK for the whole squad (cheap as dirt)

---

## Tactics: The Approach

### Landing on Grid (e.g., jumping into them on a gate)

**0-5 seconds:**
1. ALL ships: Overheat MWD immediately on decloak
2. Thoraxes: Burn DIRECTLY at the enemy fleet. Do NOT orbit. Straight line. Close distance.
3. Celestises: Burn perpendicular/slightly angled. Stay 30-40km from enemy, 20-30km from Thoraxes.
4. Blackbird: Burn to max jam range (~60-70km), start jamming Hyenas.
5. Griffin: Burn at a Hyena, overheat AB, get scram.

**5-15 seconds:**
1. Thoraxes: First Thorax that gets in scram range (8-9km) calls primary on NEAREST Hyena. All Thoraxes switch.
2. Blasters + drones = Hyena dies in 5-8 seconds.
3. Celestises: Damps on the CLOSEST Omen NIs. Priority: any Omen NI shooting a Thorax.
4. Hyenas are fragile (~3k EHP). Focus fire = dead.

**15-30 seconds:**
1. First Hyena dead. Second Hyena primary if alive.
2. Thoraxes now have 90% of their speed back (no web).
3. Continue closing on Omen NIs.
4. Any Omen NI inside scram range (8km) gets scrammed + webbed by a Thorax.
5. That Omen NI is now inside blaster optimal (4.5km). It dies in 10-15 seconds.

**30+ seconds:**
1. Omen NIs must choose:
   - Stay and fight at range they can't track (Thoraxes orbit at 500m, transversal is high) — they miss, they die
   - Warp off — Thoraxes win the field
   - Try to kill Celestises — Celestises are fast, damps continue
2. Thoraxes do NOT chase deep. If Omen NIs warp, loot field, extract.

### Against Their Tackle (Hyena)

The Hyena is the key. One Hyena web = Thorax speed drops from 1.5km/s to ~150m/s. At that speed:
- Thorax transversal collapses
- Beam lasers track perfectly
- You die in 10 seconds

**Solution:** Kill Hyenas in <10 seconds. 6 Thoraxes shooting one Hyena = ~3,000 DPS. Hyena has ~3k EHP. Dead in 1 second of focused fire.

But they have TWO Hyenas. With good target calling, you kill first Hyena in 5 seconds, second in another 5 seconds. During that time, 2-3 Thoraxes might die (acceptable trade).

### Against Their DPS (Omen NI)

At 35-50km (their optimal):
- Omen NI DPS: ~400 per ship
- 14 Omen NIs shooting one Thorax: ~5,600 DPS
- Thorax shield tank: 14k EHP
- Time to die: ~3 seconds

At 10km (inside their falloff, high transversal):
- Omen NI applied DPS: ~100-150 per ship (tracking fails)
- 14 Omen NIs: ~1,400-2,100 DPS
- Thorax dies in ~7-10 seconds

At 5km (scrammed, webbed, orbiting):
- Omen NI applied DPS: ~50-80 per ship (terrible tracking)
- 14 Omen NIs: ~700-1,100 DPS
- Thorax dies in ~15-20 seconds
- But ONE Thorax at 5km does 520 DPS. Six Thoraxes = 3,120 DPS.
- One Omen NI dies in ~5 seconds.
- Trade: 1 Thorax for 1 Omen NI = you win (T1 cruiser trades into Navy cruiser)

### Range Dictation

The Celestis is the secret weapon. Three range damps on one Omen NI:
- Base Omen NI lock range: ~70km (with skills + modules)
- After 3x range damps: ~20-25km
- That Omen NI cannot lock anything past 25km
- It must burn closer or sit useless

If ALL 14 Omen NIs get damped (2 Celestises, 3 damps each = 6 Omen NIs fully damped), half their fleet is blind.

---

## Critical Skills

**Thorax pilots:**
- Gallente Cruiser IV+ (tracking + damage)
- Hybrid Turrets IV+ (DPS)
- Gunnery support skills: Motion Prediction, Surgical Strike, Rapid Firing IV+
- Shield Upgrades IV (for Shield Extender)
- Navigation IV, Evasive Maneuvering IV (speed)

**Celestis pilots:**
- Sensor Linking IV+ (damp strength)
- Long Range Targeting IV (for lock range to apply damps)
- Target Management IV (more targets)

**Blackbird pilots:**
- Electronic Warfare IV+ (jam strength)
- Frequency Modulation IV (jam range)
- Long Distance Jamming IV (jam range)

---

## Suggested Drone Loadouts

- **Thorax:** Warrior II x5 (fast, EM damage — good vs shields)
- **Celestis/Blackbird:** Warrior II x3 (anti-tackle, finish Hyenas)
- If you have drone bandwidth issues: Hobgoblin II (thermal) works too

**Drone tactics:**
- Launch ALL drones on primary (Hyena)
- If Omen NI gets scrammed, half drones switch to it
- Warriors are FAST. They catch MWDing Hyenas.

---

## Variants

### Budget Version (T1 modules)
Replace all T2 modules with meta equivalents:
- `Heavy Ion Blaster I` instead of II (lose ~15% DPS)
- `50MN Y-T8 Compact Microwarpdrive`
- `Fleeting Compact Stasis Webifier`
- `Medium Shield Extender I`
- `Magnetic Field Stabilizer I`

**Cost drops to ~8M per Thorax. DPS drops to ~420. Still viable.**

### Advanced Version (Faction/Deadspace)
- `Cormack's Modified Magnetic Field Stabilizer` — overkill, don't do this for T1 doctrine
- `True Sansha Warp Scrambler` — more range (9.5km vs 8km)
- `Republic Fleet Shield Extender` — more buffer

Only upgrade if you're winning and have ISK to burn.

### "Iron Wall" — Armor Thorax Variant
If you prefer armor over shield:

```
[Thorax, Abyssal Edge - Iron Wall]

Heavy Ion Blaster II, Void M x5

50MN MWD II
Fleeting Web
Warp Scrambler II

1600mm Steel Plates II
Damage Control II
Multispectrum Energized Membrane II
Magnetic Field Stabilizer II
Magnetic Field Stabilizer II

Medium Trimark Armor Pump I x3

Warrior II x5
```

**Pros:** More EHP (~20k), smaller sig, better vs lasers
**Cons:** Slower (no nanos), harder to close distance
**Verdict:** Use only if your pilots are bad at manual piloting. Shield Thorax is better for this matchup because speed = survival.

---

## Why This Doctrine Works

1. **Counters their strength:** Their strength is range + tracking. We close to <10km where both fail.
2. **Kills their linchpin:** Hyenas die first. Without webs, their damage application collapses.
3. **EWAR multiplies effect:** Damps don't just help — they win. An Omen NI that can't lock is a 50M ISK paperweight.
4. **Cost efficiency:** 10 T1 cruisers (~100M) vs. 14 Navy cruisers + T2 support (~1B+). Trade 2:1 and you win ISK-wise.
5. **Skill accessibility:** T1 cruisers, mostly T2 modules. Newbies can fly this in 2-3 weeks.

---

## Why It Might Fail

1. **Bad target calling:** If Thoraxes shoot Omen NIs instead of Hyenas, the Hyenas web everyone and you die.
2. **Bad piloting:** If Thoraxes orbit at 15km instead of 500m, they're in beam laser sweet spot. Die.
3. **Not enough Celestises:** With 0-1 Celestis, 14 Omen NIs shoot freely. You need at least 2.
4. **They have logistics:** If they bring Augorors/Exequrors, you can't break tank. But the zKill shows no logi.
5. **Blob:** If they have 40 Omen NIs and you have 10 Thoraxes, you die. Doctrine assumes rough numbers parity.

---

## Summary

**"Abyssal Edge"** — T1 cruiser doctrine designed to brawl kiting Omen Navy Issues.

- **Core:** Shield Thorax with blasters (6x)
- **Support:** Celestis sensor damps (2x) + Blackbird ECM (1x) + Griffin tackle (1x)
- **Tactic:** Overheat MWD, burn at them, kill Hyenas in <10 seconds, damp Omen NIs, brawl inside blaster optimal
- **Win condition:** Trade T1 cruisers into Navy cruisers at 1:1 or better
- **ISK efficiency:** ~100M vs. ~1B+ enemy fleet

**Kybernauts call it:** "Get close or die trying."

---

*Doctrine designed by Nova for Kybernauts Clade. Test in Pyfa before undocking. Fly what you can afford to lose.*
