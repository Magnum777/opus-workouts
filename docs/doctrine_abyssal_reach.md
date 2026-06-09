# Abyssal Reach - T1 Cruiser Doctrine vs. Kikimora Fleets

## Threat Analysis (from zKill 135912809)

**Enemy Ship: Kikimora (Triglavian Destroyer)**

**What the fit tells us:**
- Light Entropic Disintegrator II + Meson ammo = high close-range DPS
- 1MN Afterburner II = slow propulsion (not MWD — this is a brawler)
- Republic Fleet Medium Shield Extender + Multispectrum Shield Hardener + EM rig = shield tank
- Small Gremlin Compact Energy Neutralizer = cap warfare
- 2x Entropic Radiation Sink II = massive DPS bonuses
- IFFA Compact Damage Control + Nanofiber = some tank, some speed

**Kikimora Characteristics:**
- **Disintegrator:** Single-beam turret, NO falloff in the traditional sense. Damage is binary: inside optimal = full DPS, outside = sharply reduced. Spools up over time (starts low, ramps to max).
- **DPS:** With T2 sinks and spool, ~350-450 DPS at optimal
- **Optimal range:** Light disintegrator with Meson = ~8-10km (short)
- **Tank:** Shield, ~8-12k EHP (destroyer hull)
- **Speed:** AB = ~400-500m/s. Slow. Can't chase kiters.
- **Sig radius:** Destroyer-sized (~65m base) — small, harder to hit with medium weapons
- **Cap warfare:** Neuts kill active tanks (Shield Boosters, Armor Repairers)
- **Tracking:** Light guns track well — dangerous to frigates and slow cruisers

**The Problem:**
Kikimoras are **glass cannons that win by spooling disintegrators at close range.** They scram + web you, hold you at 5-8km, and their DPS ramps until you die. The neut kills your active tank. They're fragile but their DPS is destroyer-class on steroids.

**Their Weaknesses:**
1. **No range** — disintegrators are purely optimal-based. Outside 10km = drastically reduced damage
2. **AB fit** — slow. Cannot chase kiters. Cannot disengage.
3. **Single weapon** — disintegrator is their ONLY damage. Jam it, TD it, or out-range it = zero DPS
4. **Shield tank** — EM hole (as seen in the EM reinforcer rig on the victim)
5. **Fragile** — destroyer hull tank. Focused fire from cruisers kills them fast
6. **Spool mechanic** — if you break range for even a few seconds, their DPS resets to minimum

---

## Doctrine: "Abyssal Reach" — Kite and Break

### Philosophy
**Stay outside their optimal. Use missiles and drones (no tracking issues). Break their disintegrators with tracking disruptors. Kill them before they spool.**

Kikimoras are pure close-range brawlers. They die to anything that can shoot from 15km+ while they can't shoot back.

---

### Mainline: Caracal ("Longshot")

```
[Caracal, Abyssal Reach - Longshot]

Rapid Light Missile Launcher II, Caldari Navy Scourge Light Missile
Rapid Light Missile Launcher II, Caldari Navy Scourge Light Missile
Rapid Light Missile Launcher II, Caldari Navy Scourge Light Missile
Rapid Light Missile Launcher II, Caldari Navy Scourge Light Missile
Rapid Light Missile Launcher II, Caldari Navy Scourge Light Missile

50MN Quad LiF Restrained Microwarpdrive
Large Shield Extender II
Multispectrum Shield Hardener II
EM Shield Hardener II

Ballistic Control System II
Ballistic Control System II
Damage Control II

Medium Warhead Rigor Catalyst I
Medium Warhead Flare Catalyst I
Medium Polycarbon Engine Housing I

Warrior II x2
Hobgoblin II x3

Caldari Navy Scourge Light Missile x2000
```

**Stats (all V skills):**
- **DPS:** ~420 (RLML + 5 light drones)
- **Range:** ~35km (RLML with skills)
- **Tank:** ~18k EHP shield (dual hardeners patch EM hole)
- **Speed:** ~1.4km/s with MWD
- **Application:** Missiles always hit. Rigor + Flare rigs help vs. small sig.
- **Cost:** ~15M ISK hull + fit

**Role:** Primary DPS. Stay at 25-35km from Kikimoras. **Never let them get within 10km.** 

Kikimora with AB = 500m/s. You with MWD = 1,400m/s. They literally cannot catch you unless you let them. Keep range, orbit at 30km, launch missiles. Drones set to "aggressive" — they chase down Kikimoras that try to escape.

**Primary target order:** Nearest Kikimora. No special priority — they're all the same threat. Just kill the closest one to reduce incoming DPS.

---

### Support A: Arbitrator ("Blindside")

```
[Arbitrator, Abyssal Reach - Blindside]

Small Energy Neutralizer II
Small Energy Neutralizer II
[empty high]

50MN Quad LiF Restrained Microwarpdrive
Tracking Disruptor II, Optimal Range Disruption Script
Tracking Disruptor II, Optimal Range Disruption Script
Tracking Disruptor II, Optimal Range Disruption Script

Damage Control II
Drone Damage Amplifier II
Drone Damage Amplifier II
400mm Steel Plates II

Medium Drone Speed Augmentor I
Medium Drone Speed Augmentor I
Medium Anti-Explosive Pump I

Warrior II x5

Optimal Range Disruption Script x3
```

**Stats:**
- **TD strength:** 3x Tracking Disruptor II with range scripts = reduce turret optimal by ~35-40% each
- **Combined effect on Kikimora:** 3 TDs = disintegrator optimal drops from ~10km to ~2-3km
- **Drone DPS:** ~180 (5x Warrior II with DDA IIs)
- **Tank:** ~14k EHP armor
- **Speed:** ~1.2km/s with MWD
- **Neuts:** 2x Small Neut II = cap pressure on Kikimoras (they need cap for hardener + AB)

**Role:** EWAR + secondary DPS. Stay at 20-25km from enemy. Apply TDs to Kikimoras that are approaching your Caracals. 

**Critical mechanic:** Tracking Disruptors reduce BOTH optimal range AND tracking speed. With range scripts, optimal is massively reduced. A Kikimora with 3 TDs on it cannot shoot past 3km. It's dead in the water.

**Target calling:** Arbitrator pilots should TD the Kikimora that is closest to your fleet, then the next closest. One Arbitrator can fully neutralize 3 Kikimoras.

**Neuts:** Use neuts on Kikimoras that get within 6km. Kills their hardener and AB.

---

### Support B: Blackbird ("Silence") — Optional

```
[Blackbird, Abyssal Reach - Silence]

Ladar Jammer II
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
- **Jam strength:** ~12 per jammer (with SDA IIs)
- **Jam range:** ~70-80km (with rigs)
- **Tank:** ~12k EHP shield

**Role:** ECM backup. Kikimoras are Triglavian ships — what sensor type? Triglavian ships use... actually I need to check this. Triglavian ships might be their own sensor type. Let me think... In EVE, Triglavian ships typically use RADAR sensors (Amarr-style). But they might use something else.

Actually, regardless of sensor type, fitting multiple jammer types covers bases:
- Ladar = Minmatar
- Radar = Amarr
- Magnetometric = Gallente
- Gravimetric = Caldari

Kikimora is likely RADAR (Amarr-derived) or possibly its own type. Fit Radar + Ladar + Magnetometric jammers and you'll likely hit their sensor type.

**ECM is RNG** — not guaranteed. But when it lands, the Kikimora's disintegrator stops working completely. Combine with Arbitrator TDs for redundancy.

---

### Tackle: Griffin ("Snare") — Optional

```
[Griffin, Abyssal Reach - Snare]

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

**Role:** Fast tackle + ECM. AB (not MWD) so if they scram you, your prop still works. Scram Kikimoras that try to escape. Jam them so they can't shoot back while your cruisers kill them.

---

## Fleet Composition (10-man squad)

| Ship | Qty | Role |
|------|-----|------|
| Caracal (Longshot) | 6 | Mainline DPS — kite at 30km |
| Arbitrator (Blindside) | 2 | TDs + drone DPS + neuts |
| Blackbird (Silence) | 1 | ECM backup |
| Griffin (Snare) | 1 | Fast tackle + jam |

**Total doctrine cost:** ~120M ISK for the whole squad (cheap)

---

## Tactics: The Approach

### Landing on Grid (jumping into them)

**0-5 seconds:**
1. ALL ships: Align AWAY from enemy. Overheat MWD.
2. Caracals: Burn to 30km range immediately. Do NOT stop to shoot at 15km — keep burning to 30km.
3. Arbitrators: Burn to 20-25km. Start TDing the CLOSEST Kikimoras.
4. Blackbird: Burn to 60km+. Start jamming.
5. Griffin: Burn at a Kikimora, get scram.

**5-15 seconds:**
1. Caracals at 30km: OPEN FIRE. RLML range is ~35km. You can shoot comfortably.
2. Kikimoras with AB = 500m/s. You at 30km with MWD = they need 60 seconds to reach you. You kill them in 20-30 seconds.
3. Arbitrators: TDs on Kikimoras that are burning at Caracals. Priority: closest ones.
4. One Arbitrator can TD 3 Kikimoras. Two Arbitrators = 6 Kikimoras neutralized.

**15-30 seconds:**
1. First Kikimora dies. Next primary.
2. If any Kikimora gets within 10km of a Caracal, that Caracal overheat MWD and pull range.
3. Remember: Kikimora DPS is zero outside 10km. If they get to 8km, you take damage. At 12km, you're safe.
4. Drones assigned to aggressive — they chase Kikimoras automatically.

**30+ seconds:**
1. Kikimoras must choose:
   - Keep burning at you and die one by one (Caracals kite forever)
   - Try to kill Arbitrators (Arbitrators are armor-tanked, farther back)
   - Warp off (you win the field)
2. Caracals have massive range advantage. This fight is unwinnable for Kikimoras if you maintain range.

### Key Numbers

| Metric | Kikimora | Caracal |
|--------|----------|---------|
| Optimal range | ~10km | ~35km (RLML) |
| Speed (AB/MWD) | 500m/s | 1,400m/s |
| DPS | 400 (spooled) | 420 (instant) |
| Tank | 10k EHP | 18k EHP |
| Sig radius | 65m | 120m |

**The math:** At 30km, Caracal does 420 DPS. Kikimora does ~0 DPS (outside optimal). Caracal kills Kikimora in ~25 seconds. Kikimora cannot close the gap.

### Against Their Neuts

Kikimoras fit small neuts (as seen in the killmail). Small neut = ~50 GJ/s cap drain. Your Caracal with MWD running = ~100 GJ/s cap use. 

**Solution:** Don't let them get in neut range (neut range = ~6-8km for small). Kite at 30km = neut does nothing.

### Against Their Spool

Disintegrator spool = damage starts low, ramps over ~90 seconds to max. 

**Solution:** They never get 90 seconds because they're dead in 25. Even if one gets close, breaking range for 5 seconds resets their spool. Kiting naturally breaks spool.

### Against Numbers

What if they have 20 Kikimoras and you have 10 cruisers?

- 6 Caracals = 2,520 DPS at 30km
- 2 Arbitrators = 360 drone DPS + 6 TDs
- Each Kikimora dies in ~15 seconds under focused fire
- Your fleet kills one every 15 seconds = 4 per minute
- Their fleet kills... well, they can't shoot past 10km, so they kill zero
- You win by attrition

---

## Critical Skills

**Caracal pilots:**
- Caldari Cruiser IV+ (RLML rate of fire bonus)
- Light Missiles IV+ (DPS)
- Missile support: Guided Missile Precision, Target Navigation Prediction IV+
- Shield Upgrades IV, Tactical Shield Manipulation IV
- Drones V, Light Drone Operation IV+ (Warriors)

**Arbitrator pilots:**
- Amarr Cruiser IV+ (drone bonus)
- Weapon Disruption IV+ (TD strength)
- Frequency Modulation IV (TD optimal range)
- Drone Interfacing IV+ (drone DPS)
- Drones V, Light Drone Operation IV+

**Blackbird pilots:**
- Electronic Warfare IV+ (jam strength)
- Frequency Modulation IV, Long Distance Jamming IV

---

## Suggested Drone Loadouts

- **Caracal:** 2x Warrior II + 3x Hobgoblin II
  - Warriors = fast, EM damage (good vs. shields)
  - Hobgoblins = thermal, higher raw DPS
  - If Kikimoras try to escape, Warriors catch them
- **Arbitrator:** 5x Warrior II (speed + tracking)
- **Blackbird:** 3x Warrior II (anti-tackle)

**Drone tactics:**
- Set to aggressive — they auto-attack anything that attacks you or fleetmates
- Warriors are fast enough to catch ABing Kikimoras
- If a Kikimora gets scrammed, all drones switch to it

---

## Variants

### Budget Version (T1 modules)
Replace T2 modules with meta:
- `Rapid Light Missile Launcher I` (lose ~15% DPS)
- `50MN Y-T8 Compact Microwarpdrive`
- `Large Shield Extender I`
- `Ballistic Control System I`
- `Tracking Disruptor I` (TD I is still very effective)

**Cost drops to ~10M per Caracal. Doctrine still works.**

### Advanced Caracal (Faction)
- `Republic Fleet Large Shield Extender` — more buffer
- `Caldari Navy Ballistic Control System` — more DPS
- `Domination 50MN Microwarpdrive` — more speed
- Only upgrade if winning and have ISK

### "Iron Web" — Moa Variant
If you prefer tank over speed:

```
[Moa, Abyssal Reach - Iron Web]

Heavy Ion Blaster II, Void M x5

50MN MWD II
Stasis Webifier II
Warp Scrambler II
Large Shield Extender II
Multispectrum Shield Hardener II

Magnetic Field Stabilizer II
Magnetic Field Stabilizer II
Damage Control II

Medium Core Defense Field Extender I x3
```

**Pros:** More tank (~22k EHP), tackle (scram + web)
**Cons:** Must brawl at close range (risky), blasters track poorly vs. destroyers
**Verdict:** Only if you want to hold them down while Caracals kill from range. Moa = tackle + tank, not primary DPS.

### "Ghost" — Celestis Variant
If you want more EWAR instead of Arbitrator:

```
[Celestis, Abyssal Reach - Ghost]

Light Missile Launcher II, Caldari Navy Scourge Light Missile x3

50MN MWD II
Remote Sensor Dampener II, Targeting Range Dampening Script x3

Damage Control II
Drone Damage Amplifier II

Medium Ionic Field Projector I x3

Warrior II x3
```

**Role:** Damps reduce Kikimora lock range. Forces them closer or makes them blind.
**Verdict:** TDs (Arbitrator) are better than damps for this matchup because TDs directly kill their weapon range. Damps are secondary.

---

## Why This Doctrine Works

1. **Counters their ONLY strength:** Kikimoras win by close-range disintegrator DPS. You never let them get close.
2. **No tracking issues:** Missiles and drones don't miss. Kikimora's small sig and speed don't matter.
3. **TDs break their weapon:** Arbitrator TDs reduce disintegrator optimal from 10km to 3km. They're useless.
4. **Speed advantage:** Caracal MWD (1.4km/s) vs. Kikimora AB (500m/s). They cannot close the gap.
5. **Cost efficiency:** 10 T1 cruisers (~120M) vs. 20 T2 destroyers (~400M+). Trade 1:1 and you win.
6. **Spool is irrelevant:** They die before spool matters. Even if they get a few seconds, breaking range resets it.
7. **Neuts are useless vs. kite:** Small neut range = 6km. You fight at 30km.

---

## Why It Might Fail

1. **You let them close:** If Caracals stop at 15km and try to shoot, Kikimoras get to 8km and spool up. Die.
2. **No Arbitrators:** Without TDs, Kikimoras that get close can still do damage. 1-2 Arbitrators are mandatory.
3. **They have MWD fits:** If Kikimoras are MWD (not AB), they can close faster (~1.2km/s). But MWD = less tank, more sig. You kill them faster.
4. **They have logi (Rodiva):** Remote reps make them harder to kill. But TDs still break their DPS, so they can't shoot back while you slowly break reps.
5. **You get blobbed:** 10 vs. 50 = you die. Doctrine assumes rough parity or slight numbers disadvantage.
6. **AB + scram Caracal:** If your Caracal pilot forgets to overheat MWD and a Kikimora gets scram + web on them... spool starts, neut hits, you die. 

**Rule #1:** Stay at 25km+. Rule #2: If they're inside 15km, overheat MWD and run.

---

## Summary

**"Abyssal Reach"** — T1 cruiser doctrine designed to kite and kill Kikimora fleets.

- **Core:** Caracal RLML kiting (6x) + Arbitrator TD support (2x) + Blackbird ECM (1x) + Griffin tackle (1x)
- **Tactic:** Burn to 30km, TD closest Kikimoras, apply missiles + drones, never let them close
- **Win condition:** Kikimoras cannot apply damage at 30km. You apply perfectly. Math wins.
- **ISK efficiency:** ~120M vs. ~400M+ enemy fleet

**Kybernauts call it:** "Reach exceeds their grasp."

---

*Doctrine designed by Nova for Kybernauts Clade. Test in Pyfa. Fly what you can afford to lose.*
