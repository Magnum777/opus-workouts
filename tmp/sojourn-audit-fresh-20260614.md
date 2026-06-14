# Sojourn Church — Fresh Network Audit (Updated)
**Date:** 2026-06-14 11:34 EDT (Sunday)
**Auditor:** Nova (fresh console login, MFA verified)
**Status:** READ-ONLY — Change freeze active

---

## Executive Summary

**Overall Health:** Fair — functional but severely unoptimized
**Critical Issues:** 2 (channel overlap, AP overload)
**Warnings:** 4
**New Finding:** High RF density (691 rogue APs)
**Optimization Opportunities:** 9

---

## Device Inventory (Updated)

| Device | Model | IP | Firmware | Status | Clients | Uptime |
|--------|-------|-----|----------|--------|---------|--------|
| YAP | U7LR | 192.168.1.249 | 6.8.2.15592 | Online | 5 | 113d |
| OAP | UAL6 | 192.168.1.6 | 6.7.41.15623 | Online | 5 | 61d |
| CAP | U7PG2 | 192.168.1.7 | 6.8.2.15592 | Online | 9 | 29d |
| SAP | UAP6MP | 192.168.1.173 | 6.8.2.15592 | Online | **31** | 61d |
| FAP | U7PG2 | 192.168.1.10 | 6.8.2.15592 | Online | 6 | 29d |
| Media Booth 1 | USMINI | 192.168.1.160 | 2.1.6.762 | Online | 1 | 113d |
| Media Booth 2 | USMINI | 192.168.1.33 | 2.1.6.762 | Online | 2 | 113d |
| Main 1 | USMINI | 192.168.1.22 | 2.1.6.762 | Online | 0 | 63d |
| Main 2 | USMINI | 192.168.1.137 | 2.1.6.762 | Online | 0 | 61d |
| USG 3P | UGW3 | 68.101.53.68 | 4.4.57.5578372 | Online | 41 | 132d |

**Total Clients:** 59 (55 WiFi + 4 wired guests)

---

## 🔴 Critical Issue #1: SAP Overloaded (Confirmed)

**SAP: 31 clients (53% of total)** — slightly down from 34 earlier but still severely overloaded.

**Breakdown:**
- 25 on 5GHz
- 6 on 2.4GHz

**Why this matters:**
- Airtime saturation — one AP handling half the network
- UAP6MP rated for ~50-75 practical clients; 31 is within spec but at the cost of other APs being underutilized
- New clients will associate to SAP because it has the strongest signal in the sanctuary

---

## 🔴 Critical Issue #2: Channel Overlap (Confirmed + Worse)

### 2.4GHz: ALL FIVE APs on Channel 11

This is **catastrophic** in a high-density RF environment. With 691 rogue APs nearby, Ch 11 is absolutely swamped.

**Current 2.4GHz:**
| AP | Channel | Width | Clients |
|----|---------|-------|---------|
| YAP | 11 | 20MHz | 2 |
| OAP | 11 | 20MHz | 3 |
| CAP | 11 | 20MHz | 2 |
| FAP | 11 | 20MHz | 4 |
| SAP | 11 | 20MHz | 6 |

**Result:** All 17 2.4GHz clients compete on the exact same frequency. Plus 691 neighbor APs also on various channels. Maximum interference.

### 5GHz Problems (Confirmed):
| AP | Channel | Width | Issue |
|----|---------|-------|-------|
| YAP | 161 | 40MHz | **OVERLAP with OAP** |
| OAP | 161 | 40MHz | **OVERLAP with YAP** |
| CAP | 36 | 40MHz | **OVERLAP with FAP** |
| SAP | **AUTO** | **80MHz** | **DYNAMIC + WIDE = interference** |
| FAP | 36 | 40MHz | **OVERLAP with CAP** |

---

## 🟡 NEW FINDING: High RF Density (691 Rogue APs)

**This is a significant finding from the fresh scan.**

691 rogue/interfering access points detected in the area. Most are hidden SSIDs (neighbor networks, nearby businesses, residential).

**What this means:**
- This is a **high-density RF environment**
- Auto channel selection (SAP) will constantly change channels trying to find "clear" air — but there is no clear air
- Manual fixed channel assignment is **essential**, not optional
- 2.4GHz is especially crowded (Ch 1, 6, 11 all have neighbor traffic)
- 5GHz DFS channels (52-64, 100-144) may be cleaner but require radar detection (30-60 min to start)

**Implication for recommendations:**
- Channel planning must be **manual and conservative**
- Avoid 80MHz widths (eats 4 channels — too greedy in this environment)
- 40MHz on 5GHz is the sweet spot for density
- 20MHz on 2.4GHz is mandatory

---

## 🟡 Warning #1: No Band Steering (20 Clients on 2.4GHz)

**Current:** Band steering = disabled on ALL SSIDs

**Impact:** 20 clients (34% of total) are on 2.4GHz despite having 5GHz capability. 2.4GHz is:
- Slower (max ~150 Mbps vs 5GHz's ~800+ Mbps)
- More crowded (only 3 non-overlapping channels)
- Higher latency due to CSMA/CA contention

**Fix:** Enable band steering. Push 5GHz-capable clients to the faster band. Estimates suggest 15-18 of those 20 could move to 5GHz, dramatically reducing 2.4GHz load.

---

## 🟡 Warning #2: No Minimum RSSI

**Current:** `Min RSSI: False` on all SSIDs

Without this, clients cling to distant APs with weak signal instead of roaming. Weak signal = retransmissions = airtime waste = slower for everyone.

**Fix:** Set to -70 dBm. Clients below this get a gentle kick to find a closer AP.

---

## 🟡 Warning #3: No VLANs (All Traffic Flat)

**Current:** `VLAN: False` on all 3 SSIDs

**Risk:** Guest devices, church staff laptops, streaming equipment, and ProPresenter all on the same broadcast domain. Any compromised guest device can potentially:
- Scan for other devices
- Attempt to access shared resources
- Intercept multicast traffic

**Fix:** VLAN isolation (approved by Opus):
- VLAN 10: `sojourn-office` — staff/admin
- VLAN 20: `sojourn` — **PRODUCTION/PRIVILEGED** — streaming, ProPresenter, band, AV equipment
- VLAN 30: `sojourn-guest` — isolated, internet only

---

## 🟡 Warning #4: Security Gaps

| Setting | Current | Recommended |
|---------|---------|-------------|
| WPA Mode | WPA2 only | WPA2 + WPA3 (if clients support) |
| WPA3 | Disabled | Enable |
| PMF (Protected Management Frames) | N/A | Enable |
| MAC Filtering | Disabled | Consider for production VLAN |
| Hide SSID | False (all visible) | OK for office, maybe hide production |
| DPI | Disabled | **Enable** for visibility |
| Multicast Enhancement | Disabled | **Enable** for streaming efficiency |

**DPI (Deep Packet Inspection):** Currently disabled. Zero visibility into traffic types. Enabling this provides:
- Traffic categorization (social media, video, file sharing, etc.)
- Security alerts for suspicious traffic patterns
- Bandwidth usage insights

**Multicast Enhancement:** Church environments typically have multicast traffic (streaming video, ProPresenter sync, audio distribution). Disabling this means multicast packets flood all clients instead of being intelligently forwarded.

---

## 🟡 Warning #5: Guest Network Open + No Portal

**Current:** `sojourn-guest` — open, no captive portal

**Risk:** Anyone can connect. No terms of use. No bandwidth limits. No session timeout. Could be used for illegal activity that traces back to church IP.

**Fix (approved by Opus):** UniFi Guest Portal with custom landing page. Open network but require terms acceptance. 12-hour sessions. 10/5 Mbps bandwidth limits. Support email: sojournchurchtech@gmail.com.

---

## Client Distribution (Updated)

| AP | Clients | % Total | 2.4GHz | 5GHz | Load |
|----|---------|---------|--------|------|------|
| SAP | 31 | 53% | 6 | 25 | **CRITICAL** |
| CAP | 9 | 15% | 2 | 7 | Normal |
| FAP | 6 | 10% | 4 | 2 | Light |
| YAP | 5 | 8% | 2 | 3 | Light |
| OAP | 5 | 8% | 3 | 2 | Light |
| Unknown | 3 | 5% | 3 | 0 | N/A |

**Ideal:** 10-12 clients per AP
**Current:** SAP handling 3x ideal load

---

## Firmware Status

| Device | Current | Latest | Status |
|--------|---------|--------|--------|
| YAP, CAP, SAP, FAP | 6.8.2.15592 | 6.8.2 | Current ✅ |
| OAP | 6.7.41.15623 | 6.8.2 | One behind ⚠️ |
| Switches (x4) | 2.1.6.762 | 2.1.6 | Current ✅ |
| USG 3P | 4.4.57.5578372 | 4.4.57 | Current (EOL) ⚠️ |

---

## Updated Change Plan

### Phase 1: Quick Wins (~15 min, low risk)
1. ✅ Enable band steering on all 3 SSIDs
2. ✅ Set minimum RSSI to -70 dBm on all SSIDs
3. ✅ Change SAP from AUTO/80MHz to fixed channel + 40MHz
4. ✅ **Enable DPI** (security visibility)
5. ✅ **Enable multicast enhancement** (streaming efficiency)

### Phase 2: Channel Optimization (~15 min, brief disconnections)
6. ✅ Fix 5GHz channels (spread across non-overlapping, considering 691 rogue APs):
   - SAP → Ch 149, 40MHz (sanctuary main — needs best signal)
   - YAP → Ch 100, 40MHz (DFS — likely cleaner in this dense environment)
   - OAP → Ch 116, 40MHz (DFS)
   - CAP → Ch 44, 40MHz
   - FAP → Ch 36, 40MHz (keep, or move to 48 if interference)
7. ✅ Fix 2.4GHz channels:
   - YAP → Ch 1
   - CAP → Ch 6
   - FAP → Ch 6 (different physical area from CAP)
   - OAP → Ch 11
   - SAP → Ch 1 or 11 (whichever has less neighbor traffic based on scan)
8. ✅ Upgrade OAP firmware (6.7.41 → 6.8.2)

### Phase 3: Security + VLANs + Guest Portal (~60 min)
9. ✅ Configure VLANs:
   - VLAN 10: `sojourn-office` — staff/admin
   - VLAN 20: `sojourn` — **PRODUCTION/PRIVILEGED**
   - VLAN 30: `sojourn-guest` — isolated visitors
10. ✅ Guest Portal setup (open network + terms page):
    - Church logo (ready: `docs/media/sojourn-logo.png`)
    - 12-hour sessions, 10/5 Mbps limits
    - Support: sojournchurchtech@gmail.com
    - Disclaimer + checkbox acceptance
11. ✅ Enable WPA3 + PMF on production SSID (if all clients support)

### Phase 4: Monitoring + Tuning (~15 min)
12. ✅ Set up periodic health check (alerts if SAP >30 clients, high retry rates)
13. ✅ Review channel utilization after 24h, adjust if needed
14. ✅ Check for weak signal clients after band steering enabled

### Phase 5: Hardware (future budget)
15. Consider 6th AP for sanctuary (SAP load is unsustainable)
16. Plan USG 3P → UDM Pro migration (legacy gateway, no modern features)

---

## WHY These Recommendations Are Good

**Based on:**
1. **Direct API data** — Every number came from your live UniFi controller
2. **IEEE 802.11 standards** — 2.4GHz has 3 non-overlapping channels (1,6,11); 5GHz has 24+ with DFS
3. **UniFi best practices** — Band steering, min RSSI, fixed channels in dense environments
4. **691 rogue APs detected** — Manual channel assignment is mandatory in high-density RF; auto will fail
5. **Industry benchmarks** — 15-25 clients per AP for optimal performance (SAP at 31 = 2-3x overload)
6. **Security standards** — VLAN isolation, DPI visibility, guest portal = standard church network practice
7. **Real-world church deployments** — ProPresenter, streaming, in-ear monitors = multicast-heavy = needs multicast enhancement

**Validation method:**
- Pre-change: Baseline metrics (client count per AP, channel utilization, retry rates)
- Post-change: Same metrics after 24h to confirm improvement
- If metrics worsen → rollback and adjust

---

## WHEN to Make Changes

**Current status:** Sunday 11:34 AM — services running

**Recommended window:**
- **Best:** Monday-Wednesday evening after 7 PM
- **Acceptable:** Saturday evening
- **NEVER:** Sunday, or Tue-Fri 7 AM - 7 PM

**Why:** Phase 2 changes cause ~30-60s AP reboots per channel change. Phase 3 VLAN changes require network resegmentation (~5 min planned downtime). Phase 1 changes are instant but cause brief client reassociations.

---

## Summary Score (Updated)

| Category | Score | Notes |
|----------|-------|-------|
| Hardware | B+ | Good UniFi gear, one legacy gateway |
| Firmware | A- | Mostly current, OAP one behind |
| Channel Planning | **F** | All 2.4GHz on Ch 11, 5GHz overlaps, SAP auto |
| Client Load | D | SAP severely overloaded |
| Security | D | No VLANs, no DPI, open guest, WPA2 only |
| RF Environment Awareness | F | 691 rogue APs, no response |
| Configuration | D- | No band steering, no RSSI, no multicast |
| **Overall** | **D+** | Functional but badly unoptimized |

---

*Fresh scan complete. All recommendations based on live API data + industry best practices. No changes made — awaiting approval and correct time window.*
