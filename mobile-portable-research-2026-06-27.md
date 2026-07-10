# FT-891 Mobile & Portable Digital Operation Research

> Research date: 2026-06-27
> Researcher: Nova (for OpusMagnum / WR4MG)

---

## 🚗 Mobile Digital Setup (Operating from Vehicle)

### The Digirig Mobile Interface Approach

The **DigiRig Mobile** interface is the gold standard for mobile FT-891 digital operation. It's a combined USB soundcard + CAT control interface that replaces separate audio cables and serial adapters.

**Why DigiRig wins for mobile:**
- One USB cable from laptop → DigiRig
- Two cables from DigiRig → radio (CAT + audio)
- No festoon of cables = cleaner mobile setup
- Compact size fits in go-bag
- Costs less than separate interface + soundcard

**Specific DigiRig cables needed:**
- DigiRig DR-891 radio cable (6-pin Mini-DIN to DigiRig)
- USB-C cable (DigiRig to laptop)
- Quality USB-A to B for CAT control

### Mobile Power Considerations

**Battery options for mobile/portable:**
- **Bioenno 12AH LiFePO4** — most popular, sources 20A+ for 100W operation
- Bioenno BLF-1209WS (9AH) — sufficient for shorter activations
- Avoid smaller batteries — FT-891 pulls 14.6A at 100W on 160m CW

**Power connectors:**
- Convert FT-891's Molex power connector to **Anderson Powerpoles**
- Use 12ga wire minimum (10ga preferred) for short runs
- Always fuse the power line (inline fuse near battery)

### Antenna Solutions for Mobile FT8

**Portable antenna options:**
- BNC adapters on SO-239 (right-angle BNC for compactness)
- RG-316 coax (lightweight, 17' typical length)
- Ferrite choke on one end to prevent RFI
- Consider mAT-30 or mAT-180H tuner for matching

**Antenna types that work well portable:**
- End-fed half-wave (EFHW) with 9:1 unun
- Linked dipole for multi-band
- Vertical with radials (less efficient but fast deploy)
- Loaded whip for mobile (compromise antenna)

---

## 📦 Go-Box / Field Kit Setup

### Complete Checklist

Based on Shack-in-a-Rack FT-891 DigiRig go-box guide:

**Core Gear:**
- Yaesu FT-891 HF/6m transceiver
- Hand mic (MH-31)
- FT-891 power cable (factory or upgraded to Powerpoles)
- Spare fuses

**Enclosure:**
- 2U or 3U rack bag/case
- Rack shelf with proper depth + clearance
- Anti-vibration pads / Velcro

**Power System:**
- Powerpole fused distribution panel
- Inline main fuse at battery (critical)
- Master power switch (optional)
- Voltage meter (panel or inline)
- 10-12 AWG DC wire (red/black)
- Powerpole connectors + crimper
- LiFePO4 20-30Ah battery + charger

**RF:**
- SO-239 bulkhead connector (exterior)
- Short internal coax jumper (PL-259)
- Strain relief / cable gland
- RG-8X field coax

**Digital Modes:**
- DigiRig Mobile + FT-891 cable
- Laptop/mini PC
- WSJT-X installed
- Optional: JS8Call, Winlink

**RFI Mitigation (critical for FT8):**
- Ferrites on USB cable
- Ferrites on DC power leads
- Ferrites on audio cables
- Bonding strap/braid (optional)

**Final Check before Operating:**
- WSJT-X Test CAT = PASS
- WSJT-X Test PTT = PASS
- Time synced (critical for FT8)
- RX level ~30-60 dB in WSJT-X
- TX power ~25-50W to start
- ALC minimal (do not overdrive)
- Antenna tuned/matched + connections secure

---

## 🎒 POTA/Field Day Specific Tips

### POTA (Parks on the Air)

**Quick deploy strategy:**
1. Radio + DigiRig + laptop in LowePro camera bag (fits perfectly)
2. Bioenno 12AH battery + Powerpole cable
3. Bamatech TP-3 CW paddles + self-storing cable
4. Heil BM-17 headset with Yaesu RJ-45 adapter
5. 17' RG-316 coax with ferrite
6. Deploy antenna (EFHW preferred for multi-band)

**POTA digital best practices:**
- FT8 is most productive mode for POTA contacts
- Run ~30-50W to conserve battery
- Use spotting networks (POTA spots page)
- Self-spot via RBNhole or manual

### Field Day Setup

**Digital station configuration:**
- Dedicated laptop with WSJT-X + N1MM logger
- Separate antenna for digital (not shared with voice stations)
- Generator or large battery bank
- DigiRig interface + ferrites essential (RFI from other stations)
- Consider band-pass filters if multiple HF stations close together

---

## 🔧 Advanced Mobile Configuration

### Menu Settings for Mobile/Portable

All standard FT-891 digital settings apply (see research-2026-06-27.md), PLUS:

**Power management:**
- MENU 16-03 HF PWR: Set to 30-50W for battery conservation
- MENU 16-04 DATA GAIN: Monitor ALC — reduce if over-driving

**Quick WDH setting:**
- Press F function key → select WDH
- Rotate knob to max 3200Hz for widest digital bandwidth
- Re-check after software connects (rig control can reset it)

### RFI Troubleshooting in Mobile Setup

**Common symptoms:**
- WSJT-X freezes during TX
- Computer mouse/keyboard acts up on TX
- Audio feedback/echo

**Solutions:**
- Add ferrites on ALL cables (USB, power, audio)
- Keep antenna away from laptop
- Use shorter coax runs
- Bond radio chassis to battery negative
- Consider linear power supply instead of switching (if AC available)

---

## 📋 Paul Butzi's FT-891 Field Kit (Reference)

A practical example from a seasoned POTA operator:

**Bag:** LowePro camera bag (fits everything)

**Contents:**
- Yaesu FT-891 (Powerpole converted)
- 12ga Powerpole-to-Powerpole cable, 0.5m, with fuses
- Bioenno 12v 12AH LiFePO4 battery
- DigiRig DR-891 + USB-C 0.5m cable
- Bamatech TP-3 CW paddles + self-storing cable
- Heil Sound BM-17 headset + Yaesu RJ-45 adapter
- PTT trigger switch
- 17' RG-316 coax with ferrite choke

**Power consumption note:**
- FT-891 pulls 14.6A on 160m at 100W CW key-down
- 9AH battery sufficient for typical POTA activation
- 12AH provides comfortable margin

---

## 🔗 Sources

- KB9VBR Digirig Mobile Interface: https://www.jpole-antenna.com/2023/08/21/better-ft8-on-the-ft-891-digirig-mobile-interface/
- Shack-in-a-Rack Go Box Guide: https://shack-in-a-rack.com/pages/ft-891-digirig-go-box-checklist-complete-hf-ft8-portable-setup-guide
- Paul Butzi POTA Kit: https://paul.butzi.org/yaesu-ft-891-pota/field-kit
- Bioenno Batteries: https://www.bioennopower.com/
- DigiRig Store: https://digirig.net/

---

## Related Files

- `research-2026-06-27.md` — Base FT-891 digital setup
- `playbook.md` — Night School playbook with full queue

---

*Saved to Night School: docs/night-school/ham-radio-ai/*
