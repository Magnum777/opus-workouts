# Sojourn Church — Full Network Audit
**Date:** 2026-06-14 (Sunday)
**Auditor:** Nova (admin console access)
**Status:** READ-ONLY — Change freeze active (Sunday)

---

## Executive Summary

**Overall Health:** Fair — functional but severely unoptimized
**Critical Issues:** 2 (channel overlap, AP overload)
**Warnings:** 4
**Optimization Opportunities:** 7

---

## Device Inventory

| Device | Model | IP | Firmware | Status | Clients |
|--------|-------|-----|----------|--------|---------|
| YAP | U7LR | 192.168.1.249 | 6.8.2 | Online | 5 |
| OAP | UAL6 | 192.168.1.6 | 6.7.41 | Online | 4 |
| CAP | U7PG2 | 192.168.1.7 | 6.8.2 | Online | 7 |
| SAP | UAP6MP | 192.168.1.173 | 6.8.2 | Online | **34** |
| FAP | U7PG2 | 192.168.1.10 | 6.8.2 | Online | 7 |
| Media Booth 1 | USMINI | — | — | Online | 1 |
| Media Booth 2 | USMINI | — | — | Online | 1 |
| Main 1 | USMINI | — | — | Online | 0 |
| Main 2 | USMINI | — | — | Online | 0 |
| USG 3P (Gateway) | UGW3 | — | — | Online | 40 |

**Total Clients:** 59 (55 WiFi + 2 wired guests + 2 unknown)

---

## 🔴 Critical Issue #1: SAP Severely Overloaded

**SAP (UAP6MP): 34 clients** — that's 58% of all clients on ONE access point.

**Why this matters:**
- Airtime saturation — one AP can only handle so many simultaneous transmissions
- Bufferbloat and lag on video streaming
- New clients struggle to associate when SAP is saturated
- Channel contention between clients on same AP

**Recommendation:** SAP is likely covering the sanctuary/main worship area. Need load balancing via:
1. Enable band steering (push clients to 5GHz)
2. Set minimum RSSI (force weak clients to roam to closer AP)
3. Consider adding a 6th AP in the sanctuary if budget allows

---

## 🔴 Critical Issue #2: Channel Overlap

### 5GHz Problems:
| AP | Channel | Width | Issue |
|----|---------|-------|-------|
| YAP | 161 | 40MHz | **OVERLAP with OAP** |
| OAP | 161 | 40MHz | **OVERLAP with YAP** |
| CAP | 36 | 40MHz | OK |
| SAP | **AUTO** | **80MHz** | **DYNAMIC + WIDE = interference** |
| FAP | 36 | 40MHz | **OVERLAP with CAP** |

**Problems:**
1. **YAP and OAP on same channel (161)** — They compete for airtime. Worse: if they're within range of each other, they create co-channel interference.
2. **CAP and FAP on same channel (36)** — Same problem.
3. **SAP on AUTO + 80MHz** — Auto means it changes channels, which breaks client associations. 80MHz width on 5GHz eats 4 channels, making interference worse.

**Fix:**
- SAP: Change to fixed channel 149, 40MHz width
- YAP: Change to channel 100, 40MHz
- OAP: Keep 161 or move to 116
- CAP: Change to channel 44, 40MHz
- FAP: Keep 36 or move to 48

### 2.4GHz Problems:
**ALL FOUR APs on Channel 11** — This is catastrophic for 2.4GHz.

2.4GHz only has 3 non-overlapping channels: 1, 6, 11. Having 4 APs on channel 11 means they're all competing on the same frequency.

**Fix:**
- YAP: Channel 1, 20MHz
- OAP: Channel 1, 20MHz (different area from YAP)
- CAP: Channel 6, 20MHz
- FAP: Channel 6, 20MHz (different area from CAP)
- SAP: Channel 11, 20MHz

---

## 🟡 Warning #1: No Band Steering

**Current:** All three SSIDs show `Band Steering: N/A`

**What this means:** Clients that support 5GHz may still connect to 2.4GHz if it has a stronger signal. 2.4GHz is crowded and slow.

**Fix:** Enable BSSiante (band steering) on all SSIDs. Push 5GHz-capable clients to the faster band.

---

## 🟡 Warning #2: No Minimum RSSI

**Current:** `Min RSSI: False` on all SSIDs

**What this means:** A client in the parking lot with -85 dBm signal stays connected to SAP instead of roaming to a closer AP. Weak signal = dropped packets = lag.

**Fix:** Set minimum RSSI to -70 dBm. Clients below this get kicked and reassociate to a closer AP.

---

## 🟡 Warning #3: No Guest Portal / Disclaimer

**Current:** `sojourn-guest` — Security: open, no captive portal

**Risk:** Anyone can connect. No bandwidth limits. No terms of use. Could be used for illegal activity that traces back to the church's IP.

**Fix (approved by Opus):** Enable UniFi Guest Portal with custom landing page — church logo, disclaimer, terms of use checkbox. Keep network OPEN but require acceptance before internet access.

---

## 🟡 Warning #4: No VLAN Isolation

**Current:** All SSIDs have `VLAN: False`

**Risk:** Guest devices can potentially access church computers, printers, media systems.

**Recommendation:**
- `sojourn-office`: Church staff VLAN (trusted)
- `sojourn`: **PRODUCTION/PRIVILEGED** VLAN — streaming, ProPresenter, band in-ears, laptops, iPads, printers
- `sojourn-guest`: Isolated VLAN (internet only)

---

## 🟢 Optimization Opportunities

### 1. Firmware Uniformity
- YAP, CAP, SAP, FAP: All on 6.8.2 ✅
- OAP: Still on 6.7.41 ⚠️ (one version behind)
- **Fix:** Upgrade OAP firmware

### 2. USG 3P Gateway
- This is legacy hardware. USG 3P is end-of-life.
- It handles 40 clients fine, but lacks modern features (IDS/IPS at speed, SFP+ for fiber, etc.)
- **Recommendation:** Budget for UDM Pro/SE upgrade when possible

### 3. Switch Utilization
- 4 USMINI switches, only 2 have clients (Media Booth 1 and 2)
- Main 1 and Main 2 have 0 clients
- **Question:** Are Main 1 and Main 2 serving other devices that aren't showing? Or are they redundant?

### 4. VPN Status: Unknown
- Health check shows VPN as "unknown"
- **Question:** Is VPN needed for remote management?

---

## Client Distribution Analysis

| AP | Clients | % Total | Load |
|----|---------|---------|------|
| SAP | 34 | 58% | **CRITICAL** |
| CAP | 7 | 12% | Normal |
| FAP | 7 | 12% | Normal |
| YAP | 5 | 8% | Light |
| OAP | 4 | 7% | Light |

**Ideal:** 10-12 clients per AP for smooth performance
**Current:** One AP handling 5x ideal load

---

## Recommended Change Plan

### Phase 1: Quick Wins (5 min each, low risk)
1. ✅ Enable band steering on all SSIDs
2. ✅ Set minimum RSSI to -70 dBm on all SSIDs
3. ✅ Change SAP from AUTO/80MHz to fixed channel + 40MHz

### Phase 2: Channel Optimization (10 min, brief disconnects)
4. ✅ Fix 5GHz channels (spread across non-overlapping)
5. ✅ Fix 2.4GHz channels (1, 6, 6, 11)
6. ✅ Upgrade OAP firmware

### Phase 3: Security + VLANs + Guest Portal (45 min)
7. ✅ **Configure VLANs for network isolation (approved by Opus):**
   - VLAN 10: `sojourn-office` — admin staff, full access
   - VLAN 20: `sojourn` — **PRODUCTION/PRIVILEGED** — streaming, ProPresenter, band in-ears, laptops, iPads, printers
   - VLAN 30: `sojourn-guest` — isolated visitors, internet only
8. ✅ **Guest Portal / Hotspot (OPEN network with disclaimer page — approved by Opus):**
   - Keep `sojourn-guest` OPEN (no password)
   - Enable UniFi Guest Portal / Hotspot
   - Create custom landing page with church logo + disclaimer/terms of use
   - Require checkbox acceptance before granting internet access
   - Set session timeout (12 hours) and bandwidth limits
9. ✅ Enable WPA3 if supported by all clients

### Phase 4: Guest Portal Content (needs your input)
**Drafted:** `docs/sojourn-guest-portal.md`

Guest portal includes:
- Welcome message + church branding
- Terms of Use (acceptable use, privacy, security warnings)
- Time limits (4 hours) + bandwidth notice
- Support contact info
- Checkbox acceptance requirement
- **HTML template** ready for UniFi portal customization
- **UniFi settings table** (VLAN 30, 10/5 Mbps limits, 4h timeout)

**Still needed from you:**
- Church logo (PNG/SVG for portal page)
- Brand colors (hex codes if you want custom styling)
- Any church-specific language you want added

### Phase 5: Hardware (budget decision)
10. Consider 6th AP for sanctuary area
11. Plan USG 3P → UDM Pro migration

---

## WHEN to Make Changes

**Current status:** Sunday 11:08 AM — services likely running

**Recommended window:**
- **Best:** Monday-Wednesday evening after 7 PM
- **Acceptable:** Saturday evening
- **NEVER:** Sunday, or Tue-Fri 7 AM - 7 PM

**Why:** Each AP channel change causes a ~30-60 second reboot. Band steering change causes brief reassociations. Don't do this when people are using the network.

---

## Summary Score

| Category | Score | Notes |
|----------|-------|-------|
| Hardware | B+ | Good UniFi gear, one legacy gateway |
| Firmware | A- | Mostly current, OAP one behind |
| Channel Planning | D | Severe overlap, auto channel, wide widths |
| Client Load | D | One AP severely overloaded |
| Security | C | Open guest network, no VLANs |
| Configuration | C- | No band steering, no RSSI threshold |
| Overall | C+ | Works but unoptimized |

---

*Report generated with direct console access. Changes NOT made — awaiting approval and correct time window.*
