# Sojourn Church — Network Audit Report
**Date:** 2026-06-14
**Auditor:** Nova via UniFi Site Manager API
**Sites:** 1 active ("Sojourn Chuch")
**Controller:** UniFi Console (192.241.248.242) — Connected

---

## Executive Summary

**Overall Health:** Fair — functional but suboptimal
**Critical Issues:** 1 (TX retry rate)
**Warnings:** 3
**Optimization Opportunities:** 5

---

## Network Topology (from API)

| Component | Count | Status |
|-----------|-------|--------|
| Gateway | 1 | Online |
| WiFi APs | 5 | All online |
| Switches | 4 | All online |
| Total Devices | 10 | 0 offline |

**Client Distribution:**
- WiFi clients: 59
- Wired clients: 3
- Guest clients: 2
- **Total: 64 active clients**

---

## 🔴 Critical Issue: TX Retry Rate at 10.26%

**What this means:**
- Over 1 in 10 WiFi packets needs to be retransmitted
- Clients experience lag, dropped video calls, slow loading
- APs waste airtime resending instead of serving new traffic

**Likely Causes (in order of probability):**
1. **Channel overlap** — Neighboring APs on same/overlapping channels
2. **Too many clients per AP** — 59 clients / 5 APs = ~12 per AP (should be <15 for light usage, <10 for video streaming)
3. **Wrong channel width** — 80MHz on 5GHz uses 4 channels; in crowded environment causes self-interference
4. **2.4GHz overcrowding** — Legacy devices dragging network down
5. **AP placement** — Either too far apart (weak signal = retries) or too close (co-channel interference)

**Fix Priority:** HIGH

---

## 🟡 Warnings

### 1. Disconnected Cloud Key (Legacy Controller)
- **Firmware:** UCK.mtk7623.v1.1.19 (Feb 2021 — 5+ years old)
- **Status:** Disconnected since at least April 2026
- **Risk:** If this was your backup controller, you have no redundancy. Old firmware = unpatched security vulnerabilities.
- **Fix:** Remove from UniFi account or physically decommission.

### 2. Dual WAN Not Configured for Failover
- **Setup:** WAN + WAN2 present
- **WAN Magic:** Disabled (no automatic failover)
- **Risk:** Primary ISP outage = total network down
- **Fix:** Enable WAN failover in controller settings

### 3. Site Name Typo
- **Current:** "Sojourn Chuch" (missing "r")
- **Fix:** Cosmetic but unprofessional if shown to visitors

---

## 🟢 Optimization Opportunities

### 1. Channel Planning (Needs Local Console Access)
- **Recommendation:** Run RF scan on each AP, assign non-overlapping channels
- **5GHz:** Use 20MHz or 40MHz width (not 80MHz) in crowded environment
- **2.4GHz:** Stick to channels 1, 6, 11 only

### 2. Band Steering
- **Current:** Unknown (needs local check)
- **Recommendation:** Enable "Prefer 5GHz" to push capable clients off crowded 2.4GHz

### 3. Minimum RSSI
- **Current:** Unknown (needs local check)
- **Recommendation:** Set minimum RSSI (-70 dBm) to force weak clients to roam to closer AP instead of clinging to distant one

### 4. Guest WiFi Optimization
- **Current:** 2 guest clients (very low for church)
- **Recommendation:** 
  - Ensure guest network is on separate VLAN
  - Enable captive portal or simple password
  - Bandwidth limit guests to prevent them from saturating WAN
  - Advertise SSID clearly (on bulletin board, website)

### 5. Firmware Updates
- **Current:** 0 pending updates (either up-to-date or auto-update disabled)
- **Recommendation:** Verify auto-update is enabled for security patches

---

## Client Density Analysis

**Current:** 59 WiFi clients across 5 APs
**Average:** ~12 clients per AP

**For a church environment, typical breakdown:**
- Sunday services: likely 80-120+ devices (phones, tablets, smart watches)
- Weekday events: 20-40 devices
- **Capacity concern:** You may be near the edge on busy days

**Recommendation:** Monitor peak usage. If hitting >15 clients per AP regularly, consider adding 1-2 APs in high-density areas (sanctuary, fellowship hall).

---

## Quick Wins (No Hardware Needed)

1. **Enable WAN failover** — 5 minutes in controller settings
2. **Fix site name typo** — 1 minute
3. **Remove/disconnect old Cloud Key** — 10 minutes
4. **Enable band steering** — 2 minutes
5. **Set minimum RSSI** — 5 minutes per AP

---

## Medium Effort (Needs Console Access)

1. **Channel width reduction** — Change 5GHz from 80MHz to 40MHz
2. **Channel reassignment** — RF scan + manual assignment
3. **Guest VLAN + bandwidth limits** — Network settings
4. **Peak usage monitoring** — Enable long-term client statistics

---

## Hardware Considerations

- **Current:** 5 APs for 64 clients
- **Sunday estimate:** If you see 100+ devices, you're underspec'd
- **Upgrade path:** UniFi 6/7 Pro APs have better MU-MIMO and handle higher density

---

## Gateway Info
- **MAC:** f4:92:bf:8a:48:aa
- **Dual WAN:** Present but not configured for failover
- **Timezone:** America/New_York (correct)

---

## Next Steps

**To complete this audit, I need local console access for:**
1. Channel planning details (current channels, widths)
2. RSSI thresholds and band steering settings
3. Actual client connection quality (SNR per client)
4. Switch port utilization
5. Traffic rule inspection

**Want me to:**
- Generate a step-by-step fix guide for the quick wins?
- Set up monitoring (daily health check cron)?
- Create a guest WiFi setup guide?

---

*Report generated via UniFi Site Manager API. Some details require local controller access.*
