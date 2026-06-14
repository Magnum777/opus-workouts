# Sojourn Church — Network Optimization Execution Checklist
**Date:** Monday, June 15, 2026
**Execution Time:** 09:00 AM EST
**Reminder Set:** 08:45 AM EST
**Auditor/Operator:** Nova
**Approval:** OpusMagnum

---

## Pre-Execution Checklist (08:55 AM)

- [ ] Confirm no church services or events running
- [ ] Check current client count (baseline)
- [ ] Verify admin console access (MFA code ready)
- [ ] Confirm backup/rollback plan understood
- [ ] Have Opus available for go/no-go at 09:00

---

## Phase 1: Quick Wins (09:00–09:20 AM) — Instant, Low Risk

| # | Action | Setting | Current | Target | Risk |
|---|--------|---------|---------|--------|------|
| 1 | Enable band steering | All 3 SSIDs | disabled | enabled | Low — brief reassociations |
| 2 | Set minimum RSSI | All 3 SSIDs | False | -70 dBm | Low — weak clients roam |
| 3 | Fix SAP 5GHz | SAP Radio 1 | auto / 80MHz | Ch 149 / 40MHz | Low — 30s reboot |
| 4 | Enable DPI | Network-wide | disabled | enabled | None — monitoring only |
| 5 | Enable multicast enhancement | All 3 SSIDs | disabled | enabled | None — efficiency gain |

**Expected impact:** Clients may briefly disconnect/reconnect (~10–30s). Band steering pushes 5GHz-capable clients off 2.4GHz.

---

## Phase 2: Channel Optimization (09:20–09:45 AM) — Brief AP Reboots

### 5GHz Channels
| AP | Current | Target | Width | Notes |
|----|---------|--------|-------|-------|
| SAP | auto | Ch 149 | 40MHz | Sanctuary main — needs stability |
| YAP | Ch 161 | Ch 100 | 40MHz | DFS — likely cleaner |
| OAP | Ch 161 | Ch 116 | 40MHz | DFS — avoid overlap with YAP |
| CAP | Ch 36 | Ch 44 | 40MHz | Move away from FAP |
| FAP | Ch 36 | Ch 36 or 48 | 40MHz | Keep or shift if interference |

### 2.4GHz Channels
| AP | Current | Target | Width |
|----|---------|--------|-------|
| YAP | Ch 11 | Ch 1 | 20MHz |
| CAP | Ch 11 | Ch 6 | 20MHz |
| FAP | Ch 11 | Ch 6 | 20MHz |
| OAP | Ch 11 | Ch 11 | 20MHz |
| SAP | Ch 1 | Ch 1 | 20MHz |

**Note:** SAP 2.4GHz already on Ch 1 (from scan). Only need to move YAP, CAP, FAP, OAP.

### Firmware
| AP | Current | Target |
|----|---------|--------|
| OAP | 6.7.41 | 6.8.2 |

**Expected impact:** Each AP reboots for 30–60s during channel change. Clients auto-reconnect. Total disruption: ~5 minutes across all APs.

---

## Phase 3: Security + VLANs + Guest Portal (09:45–10:45 AM) — Planned Downtime

### VLAN Configuration
| VLAN | SSID | Purpose | Access |
|------|------|---------|--------|
| 10 | sojourn-office | Staff/admin | Full network |
| 20 | sojourn | PRODUCTION/PRIVILEGED | Streaming, ProPresenter, band, AV |
| 30 | sojourn-guest | Visitors | Internet only, isolated |

### Guest Portal Settings
| Setting | Value |
|---------|-------|
| Authentication | Hotspot (Terms of Use) |
| Landing Page | Custom with church logo |
| Session Timeout | 12 hours (720 min) |
| Bandwidth Limit | 10 Mbps down / 5 Mbps up |
| VLAN | 30 |
| Password | None (open) |

### Portal Content
- **Header:** Welcome to Sojourn Church / Free Guest WiFi
- **Logo:** `docs/media/sojourn-logo.png`
- **Terms:** Acceptable use, privacy/security warnings, 12h limit
- **Support:** sojournchurchtech@gmail.com
- **Action:** Checkbox + Connect button

### WPA3 + PMF
- Enable on `sojourn` (production) if all clients support
- Verify ProPresenter, streaming gear, iPads, laptops connect successfully

**Expected impact:** VLAN changes require network resegmentation. ~5 min planned downtime. All clients must reconnect to new VLANs. Guest network becomes portal-captive.

---

## Phase 4: Validation + Monitoring (10:45–11:00 AM)

- [ ] All APs online and reporting correct channels
- [ ] Client distribution improved (SAP ideally <25 clients)
- [ ] Band steering working (2.4GHz client count down)
- [ ] Guest portal loads and accepts terms
- [ ] Production VLAN devices (ProPresenter, streaming) functional
- [ ] DPI showing traffic categories
- [ ] Document final state — channels, client counts, any issues

---

## Rollback Plan

If anything breaks:
1. **Phase 1:** Reverse settings via UniFi console (instant)
2. **Phase 2:** Change channels back to original (AP reboots)
3. **Phase 3:** Disable VLANs, revert to flat network (requires re-adoption of some devices)
4. **Guest portal:** Disable hotspot, return to open guest

**Emergency contact:** sojournchurchtech@gmail.com

---

## Post-Execution (24h Later)

- [ ] Review client distribution
- [ ] Check channel utilization stats
- [ ] Verify no weak-signal clients stuck
- [ ] Monitor for any complaints or connectivity issues
- [ ] Adjust channels if interference detected

---

## Files / References

- Full audit: `tmp/sojourn-audit-fresh-20260614.md`
- Guest portal content: `docs/sojourn-guest-portal.md`
- Church logo: `docs/media/sojourn-logo.png`
- This checklist: `docs/sojourn-execution-checklist-20260615.md`

---

**STATUS: APPROVED — Execute Monday, June 15 at 09:00 AM EST**
