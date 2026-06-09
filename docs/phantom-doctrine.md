# Phantom Doctrine — Anti-Kikimora Counter-Plan
## Nova's Tactical Analysis

**Classification:** Internal Doctrine — Alpha Force
**Threat:** INIT Kikimora Packs with 5-6x Scimitar Support
**Principle:** Flight Dynamics Over Spreadsheet Math

---

## What I Got Wrong (Lessons Applied)

Splatterbug's critique exposed a fundamental flaw: I was treating EVE combat as a 0km stat comparison instead of a 3D flight problem. The lessons:

1. **Spool Is The Anchor** — Kikis reset to zero on every target swap. A Kiki that has to choose between targets is a Kiki that never reaches full damage.
2. **Logi Is The Wall** — 5-6 Scimitars isn't "some logi." It's a wall that only breaks via ECM or alpha that outpaces 10,000+ HP/s.
3. **No Scrams = No Range Control (For Them)** — INIT Kikis rely on webs and raw application, not hard tackle. If we have speed, we dictate when the fight happens.
4. **Flight Mechanics Beat Raw DPS** — A Kiki applying Mystic at 20km against a target burning perpendicular at 1,800 m/s is not the same Kiki applying at 0km to a stationary target. Transversal, sig bloom, falloff curves, and traversal angles matter more than EFT numbers.
5. **Attrition, Not Annihilation** — The goal isn't to win one glorious brawl. It's to make them bleed ISK across multiple micro-engagements until they stop forming.

---

## Core Insight: The Kiki Is a One-Trick Brawler

Kikimoras are optimized for a single scenario: they land, they web, they spool, and they delete things while 5 Scimitars keep them alive. 

Their weakness is everything else:
- **Outside 20km** (Mystic optimal): They're in falloff with degraded tracking
- **Against traverse**: Disintegrators track poorly against fast, angled targets
- **When forced to swap**: 90 seconds of spool evaporates
- **When logi is jammed**: Paper-thin destroyer hull pops to alpha
- **When chasing**: Their rear arc has minimal traverse, making them easy to hit

We don't beat them at their game. We don't brawl. We **haunt** them.

---

## Doctrine: "Phantom Wing"

### Primary: Stabber Fleet Issue (6-8)
**Role:** Fast kiting DPS + tackle + range control

Why SFI over Rupture? 
- **Speed**: SFI base is faster; with nano it hits ~1,800 m/s vs Rupture's ~1,400 m/s
- **Tracking**: 6 turrets with better base tracking = better falloff application
- **Mids**: Enough for scram + web while maintaining shield buffer
- **Sig**: Lower than Rupture even with MWD

```
[Stabber Fleet Issue, Phantom — Anti-Kiki]

220mm Vulcan AutoCannon II, Republic Fleet Phased Plasma M
220mm Vulcan AutoCannon II, Republic Fleet Phased Plasma M
220mm Vulcan AutoCannon II, Republic Fleet Phased Plasma M
220mm Vulcan AutoCannon II, Republic Fleet Phased Plasma M
220mm Vulcan AutoCannon II, Republic Fleet Phased Plasma M
220mm Vulcan AutoCannon II, Republic Fleet Phased Plasma M

50MN Quad LiF Restrained Microwarpdrive
Large Azeotropic Restrained Shield Extender
Faint Epsilon Warp Scrambler I
Fleeting Propulsion Inhibitor I

Gyrostabilizer II
Gyrostabilizer II
Tracking Enhancer II
Nanofiber Internal Structure II
Nanofiber Internal Structure II

Medium Projectile Ambit Extension I
Medium Projectile Metastasis Adjuster I
Medium Polycarbon Engine Housing I

Warrior II x5
```

**Key Stats (approximate — pyfa with decent skills):**
- Speed: ~1,750-1,850 m/s with MWD
- Falloff: ~20-22km with RF Phased Plasma
- Alpha: ~2,200-2,500 per volley per ship
- 8 SFIs = ~18,000-20,000 alpha volley
- EHP: ~18,000 shield (enough to not instantly pop)

**Tactical Role:**
- Orbit at **22-25km** from Kiki blob — inside our falloff, outside their optimal comfort
- **Perpendicular approach on land** — never burn straight at them. Burn across their bow at 90° to maximize transversal while closing.
- **Spread fire across 2 targets** — force their FC to choose who gets spool. Either way, someone is dying without full DPS.
- **Tail runners**: When a Kiki burns, 2 SFIs chase with scram. Falloff fire into their MWDing rear (zero transversal from behind) while the rest stay on the blob.

---

### Secondary: ECM Screen (2-3 Blackbirds)
**Role:** Scimitar suppression — the linchpin of the entire doctrine

This is non-negotiable. Without jams, 5-6 Scimitars laugh at our alpha. With jams, Kikis evaporate.

```
[Blackbird, Phantom Screen — Anti-Scimi]

Rocket Launcher II, Caldari Navy Scourge Rocket

Large Azeotropic Restrained Shield Extender
Large Azeotropic Restrained Shield Extender
50MN Quad LiF Restrained Microwarpdrive
Initiated Compact Warp Disruptor
Enfeebling Scoped Ladar ECM
Enfeebling Scoped Ladar ECM
Enfeebling Scoped Ladar ECM
Enfeebling Scoped Ladar ECM

Signal Distortion Amplifier II
Signal Distortion Amplifier II

Medium Particle Dispersion Augmentor I
Medium Particle Dispersion Augmentor I
Medium Particle Dispersion Augmentor I

Hornet EC-300 x5
```

**Tactical Role:**
- Land at **80-100km**, aligned out
- Cycle jams on **Scimitars only** — ignore Kikis, let DPS handle them
- Coordinate jams: Blackbird 1 takes Scimi 1-2, Blackbird 2 takes Scimi 3-4, Blackbird 3 takes Scimi 5-6
- If a jam breaks, immediate secondary call
- **Survival priority**: If Kikis burn toward Blackbirds, warp out. They're cheap. Replacing them is faster than losing them.

**Math Check Needed:**
- Scimitar sensor strength (Ladar): ~20-24 points
- Blackbird with 4x Ladar jammers + SDAs: ~7-9 jam strength per module
- Jam probability per cycle: ~30-45% per module
- With 3 Blackbirds x 4 jams = 12 attempts on 6 Scimitars = statistically we keep 3-4 jammed continuously
- That's enough to break their rep chain.

---

### Interdiction: Hyena Wing (2)
**Role:** Web net + long tackle + target isolation

This is the piece most analyses miss. Kikis don't scram, but they web. What if **we** web **them** from outside their web range?

```
[Hyena, Phantom Net]

125mm Gatling AutoCannon II

5MN Quad LiF Restrained Microwarpdrive
Faint Epsilon Warp Scrambler I (or Fed Navy Disruptor for 24km)
Fleeting Propulsion Inhibitor I (or Fed Navy Web for 20km)
Medium Azeotropic Restrained Shield Extender

Nanofiber Internal Structure II
Nanofiber Internal Structure II

Small Polycarbon Engine Housing I
Small Polycarbon Engine Housing I
Small Auxiliary Thrusters I

Warrior II x3
```

**Why Hyena:**
- **60% web range bonus** — a faction web reaches ~20-24km
- **Bonused disruptor range** — can point from 30km+
- Fast enough to keep up with SFI fleet
- Cheap as dirt for an EAF

**Tactical Role:**
- Burn to edge of Kiki blob (20km out)
- Web the edge Kikis — this does two things:
  1. Slows them so our SFI projectiles apply better
  2. Forces them to either accept the fight at a disadvantage or burn (resetting spool)
- If a Kiki burns, Hyena point + web + SFI tail = dead Kiki
- **Priority target**: If they bring their own Hyena/Rapier/Huggin, kill it first. Web ships are the counter to our doctrine.

---

### Optional: Command Destroyer (1 Bifrost or Stork)
**Role:** Separation boosh

If the Kikis cluster tight with Scimitars, a well-timed micro jump field separates the Kiki DPS from their logi. This is high-skill, high-reward.

**Only use if FC is confident with boosh timing.** A bad boosh saves the Kikis.

---

## Engagement Sequence: "The Haunt"

### Phase 1: The Ghost Approach (0:00-0:30)
1. **Fleet lands 50km off** their blob
2. **SFIs burn perpendicular** (90° to their facing) at max speed
3. **Blackbirds land 80km out** and start cycling jams immediately
4. **Hyenas close to 20km** and web edge targets
5. **Goal**: Establish traverse-heavy positioning before they get clean locks

### Phase 2: The Pinprick (0:30-1:30)
1. SFIs orbit at **22-25km**, firing into falloff
2. **Spread damage**: 4 SFIs on Primary Kiki, 4 SFIs on Secondary Kiki
3. Kiki FC faces a choice:
   - Stay on Primary → Secondary dies to 4-ship alpha
   - Swap to Secondary → Primary escapes, spool resets on both
4. **Blackbirds keep Scimitars jammed** — any unjammed Scimi gets called for secondary ECM
5. **Hyena webs** the Kiki trying to pull range

### Phase 3: The Kill Window (1:30-2:00)
1. Once a Kiki is webbed + jammed, **all SFIs switch** to it for 1-2 volleys
2. 8 SFIs x ~2,200 alpha = ~17,600 volley
3. Kikimora hull (~8-10k EHP + minimal buffer) dies in 1 volley, maybe 2
4. **Immediate target swap** — don't admire the explosion. Call new primary before they adapt.

### Phase 4: The Break or Press (2:00+)
**Option A — We killed 2+ Kikis and they're breaking:**
- SFIs with scrams tail runners
- Hyenas web + point runners
- Reform at 60km, prep for re-engagement on stragglers
- **Re-engage before they regroup** — wounded Kikis are out of position

**Option B — They adapted (booshed us, brought ECM, or we're taking too much fire):**
- FC calls "break break break"
- All SFIs burn perpendicular to Kiki line (not straight away — perpendicular maintains traverse)
- MWD to 40km, assess
- If Blackbirds are being chased, they warp to ping and back
- **Live to re-engage** — a living Phantom fleet is scarier than a dead brawler fleet

---

## The Flight Mechanics (Why This Works)

### Range Band Analysis
| Range | Kiki (Mystic) | SFI (220mm RF Plasma) |
|-------|--------------|----------------------|
| 0-10km | Full tracking, full damage | Tracking issues (too close), scram range |
| 10-15km | Good tracking, good damage | Optimal + early falloff, comfortable |
| **15-25km** | **Falloff starts, tracking degrades** | **Prime falloff zone, good application** |
| 25-30km | Heavy falloff, poor tracking | Still decent falloff |
| 30km+ | Barely scratching | Still applying in falloff |

**Sweet spot: 22-25km.** They're uncomfortable. We're comfortable. That's the whole fight.

### Transversal Geometry
- **Head-on approach (0°)**: Minimal transversal. Kiki tracking is best. We die.
- **Perpendicular approach (90°)**: Maximum transversal. Kiki misses. We win.
- **Tailing a runner (180°, chasing)**: Minimal transversal FOR THEM. Our projectiles hit their rear perfectly while their disintegrator can't track backwards well.

**Perpendicular burns are the default maneuver.** Never fly straight at them unless you're a tackle ship landing a scram.

### Spool Asymmetry
- Kiki spool: ~90 seconds to max DPS. Resets on target swap.
- SFI projectiles: Full alpha on every volley. No spool. Target swap costs us nothing.
- **This means:** Every target swap WE force is free value. Every target swap THEY force costs them 90 seconds of ramp.

---

## Counter-Counter: Adapting to Their Adaptation

**If they bring Keres (damped tackle):**
- Keres has no DPS. Ignore it.
- If Keres points an SFI, that SFI MWDs away (perpendicular burn). Keres can't keep up.
- If Keres damps Blackbirds, Blackbirds warp to ping and come back from a different angle.

**If they bring their own ECM:**
- This actually helps us. Every Falcon/Kitsune jamming an SFI is a jam not on our Blackbirds.
- SFI has enough buffer to survive 1-2 volleys of unjammed Kiki fire. Blackbirds have zero.
- Trade: let them jam DPS, keep our jams on their logi.

**If they switch to Baryon (short range, better tracking):**
- Baryon optimal is ~8-12km. If they're chasing us with Baryon, they're not hitting us at 22km.
- If they close to Baryon range, we kite harder. Their speed is ~900 m/s. Ours is ~1,800 m/s.
- They can't force the range. We can.

**If they bring Rapier/Huggin (webs):**
- **This is the real counter.** A Rapier webbing our SFIs from 30km undoes our speed advantage.
- **Primary target shifts to the web ship immediately.** Kill it before engaging Kikis.
- Hyenas should prioritize web ships with their own webs.

**If they blob (more than 12 Kikis):**
- Phantom Wing doesn't fight blobs. We warp.
- Attrition only works if we're ISK-positive. Fighting a blob isn't.
- Re-engage when they're split.

---

## Key FC Callouts

1. **"Perpendicular burn"** — Default approach. Never charge head-on.
2. **"Jam logi"** — First call after landing. Blackbirds cycle immediately.
3. **"Web edge"** — Hyenas pick off-edge Kikis.
4. **"Two targets"** — Spread fire. Force the spool choice.
5. **"Volley and switch"** — All on one target for 1-2 cycles, then new primary.
6. **"Break and reform"** — Disengage at 50% shields. We're not brawlers.
7. **"Re-engage"** — Hunt stragglers before they regroup.

---

## Economic Reality

| Ship | Approx Cost |
|------|-------------|
| Stabber Fleet Issue | ~35-40M ISK |
| Blackbird | ~15-20M ISK |
| Hyena | ~20-25M ISK |
| **Total Wing (8+3+2)** | **~400-450M ISK** |
| Kikimora (fit) | ~80-100M ISK |
| Scimitar (fit) | ~250-300M ISK |

**Math:** Kill 3 Kikis = 240-300M. Kill 1 Scimitar = 250-300M. 
We need to kill **2 Scimitars or 4-5 Kikis** to be ISK-positive for the fleet. In practice, if we kill 1 Scimitar and 2 Kikis, we're roughly even — but they lost logi, which means their doctrine is broken for the rest of the op.

Attrition math favors us because we're cheaper and faster to replace.

---

## Validation Checklist

Before fielding this:
- [ ] Pyfa SFI at 22km vs Kiki Mystic tracking — confirm we take minimal damage at traverse
- [ ] Test perpendicular burn vs head-on in Pyfa/simulator
- [ ] Confirm Blackbird jam probability vs Scimitar sensor strength (Ladar)
- [ ] Practice "volley and switch" timing with fleet
- [ ] Confirm Hyena web range with faction web (target: 20km+)
- [ ] Establish bookmark patterns for Pochven/wherever Kikis roam
- [ ] Test SFI speed with MWD vs Kiki speed (should be 2:1 ratio)

---

## Summary: The Phantom Philosophy

Don't fight the Kiki. **Haunt** it.

Appear at range. Force bad choices. Vanish before they can respond. Reappear where they aren't. Make every engagement a losing proposition for them until they stop undocking.

Kikis are built to win brawls. We're built to make brawls impossible.

---

*Written by Nova, 2026-06-01*
*Flight dynamics, not raw numbers.*
*Splatterbug was right.*
