# Ham Radio AI — Remaining Research Topics (Complete)

> Research date: 2026-06-27
> Researcher: Nova (for OpusMagnum / WR4MG)

---

## 📻 PSK31 — Keyboard-to-Keyboard Ragchewing

### What Is PSK31?

PSK31 (Phase Shift Keying, 31 baud) is a conversational digital mode — unlike FT8's automated exchanges, PSK31 lets you actually *chat* in real-time via keyboard.

**Why PSK31 matters:**
- Real conversations, not just signal reports
- 31 Hz bandwidth (extremely narrow)
- Works at low power (10-30W typical)
- Human-readable, not machine-protocol

### Station Requirements

Same basic setup as FT8:
- HF SSB transceiver (FT-891 works perfectly)
- Soundcard-equipped PC
- Interface or VOX keying
- PSK31 software

**Software options:**
- **DigiPan** — classic, simple
- **FLdigi** — multi-mode, supports PSK31 + many others
- **Ham Radio Deluxe (DM780)** — integrated suite
- **MixW** — popular contest logger with PSK

### Setup Steps

1. Connect radio to PC (same audio interface as FT8)
2. Install PSK31 software
3. Tune to common PSK31 frequencies:
   - 3.580 MHz (80m)
   - 7.070 MHz (40m — most active)
   - 14.070 MHz (20m — most active)
   - 21.080 MHz (15m)
   - 28.120 MHz (10m)
4. Set radio to USB mode
5. Adjust audio drive until ALC reads 0
6. Watch waterfall, click on signals to decode

### Operating Etiquette

**Calling CQ:**
```
CQ CQ CQ de CALLSIGN CALLSIGN CALLSIGN CQ CQ CQ de CALLSIGN CALLSIGN CALLSIGN K
```

**Answering a CQ:**
```
CALLSIGN CALLSIGN CALLSIGN de OTHERCALL OTHERCALL OTHERCALL pse K
```

**During QSO:**
```
OTHERCALL de MYCALL Hi there! (message) BTU OTHERCALL de MYCALL k
```

**Ending:**
Use "sk" instead of "k" to signify end of conversation.

**Key abbreviations:**
- BTU = Back to you
- BRB = Be right back
- CUL = See you later
- 73 = Best regards
- 88 = Love and kisses (often ironic in ham radio)

### Signal Reports

PSK31 uses RSQ (Readability, Strength, Quality) instead of RST:
- **R**eadability: 1-5 (5 = perfectly readable)
- **S**trength: 1-9 (based on waterfall brightness)
- **Q**uality: 1-9 (9 = pure signal, no splatter)

Typical report: `RSQ 599` (perfect)

---

## ⚡ FT4 vs FT8 — Speed vs Sensitivity

### Head-to-Head Comparison

| Feature | FT8 | FT4 |
|---------|-----|-----|
| **Transmission Cycle** | 15 seconds | 7.5 seconds |
| **T/R Exchange Time** | 12.64s | 5.36s |
| **Bandwidth** | 50 Hz | 90 Hz |
| **Decoding Sensitivity** | -21 dB | -17 dB |
| **Intended Use** | Weak signal, DXing | Contesting, rapid QSOs |
| **Rate (QSOs/hour)** | ~100-150 | ~200-300 |

### When to Use Which

**Use FT8 when:**
- Propagation is marginal
- Working rare DX (every dB matters)
- Bands are noisy
- You need maximum reliability
- Casual operation, not racing

**Use FT4 when:**
- Contesting (rate is king)
- Bands are open and strong
- Working common stations
- Time is limited (e.g., lunch break)
- You want faster pace

### Technical Differences

**FT8 advantages:**
- 4 dB better sensitivity (crucial for weak signals)
- Narrower bandwidth (less interference)
- More decode cycles per transmission
- Better error correction (LDPC with more iterations)

**FT4 advantages:**
- 2x faster cycle = 2x potential rate
- Shorter transmissions = less chance of QRM collision
- Better for contest pileups
- More "human" pace (less waiting)

**The tradeoff:**
FT4 sacrifices ~4 dB of sensitivity for 2x speed. On a good band, that 4 dB doesn't matter. On a marginal path, it matters a lot.

### Contest Reality

Many contesters run both:
- FT4 for fast rate when signals are strong
- Switch to FT8 when signals drop or for multipliers
- Some contests have separate categories for each mode

---

## 🔌 FT-891 6-Pin Mini-DIN Data Port Pinout

### Pin Assignment (Rear Panel View)

```
      6-Pin Mini-DIN (rear of radio)

        Pin 2 (GND)
          │
    Pin 1 ─┼─ Pin 3
  (DATA IN)│ (PTT/SEND)
          │
    Pin 6 ─┼─ Pin 4
   (PKS/SQL)│ (DATA OUT - 9600/raw)
          │
        Pin 5
      (DATA OUT - processed)
```

### Pin Functions

| Pin | Function | Description |
|-----|----------|-------------|
| **1** | TX Audio In (DATA IN) | Transmit audio from PC to radio |
| **2** | GND | Ground reference |
| **3** | PTT (SEND) | Ground to transmit (active low) |
| **4** | RX Audio Out (9600/raw) | Unprocessed discriminator output |
| **5** | RX Audio Out (processed) | Filtered/de-emphasized audio |
| **6** | PKS / Squelch Logic | Mute/squelch indication |

### Important Notes

**Pin 1 — TX Audio:**
- In "1200 baud" mode: processed audio (pre-emphasis/filtering)
- In "9600 baud" mode: flat audio direct to modulator
- For most digital modes: use 1200 baud setting
- Menu setting: DATA MODE = OTHERS (for FT-891)

**Pin 4 vs Pin 5 — RX Audio:**
- Pin 4: Raw discriminator output (best for digital)
- Pin 5: Processed like speaker audio (less ideal)
- Most interfaces use Pin 4 for RX

**Pin 3 — PTT:**
- Ground this pin to key transmitter
- Interface handles this automatically
- Can also use CAT PTT (software-controlled)

### Building a Custom Cable

**Parts needed:**
- 6-pin Mini-DIN male connector
- 3.5mm TRS audio cable (for PC soundcard)
- Optional: isolation transformers (reduce RFI)
- Optional: USB soundcard interface (like SignaLink)

**Basic wiring:**
```
PC Speaker Out → Pin 1 (DATA IN)
PC Mic In ← Pin 4 (DATA OUT - raw)
PTT from interface → Pin 3 (ground to TX)
GND → Pin 2 (common ground)
```

**For FT-891 specifically:**
- Menu 08-09 DATA IN SELECT = REAR (enables this port)
- Menu 08-10 DATA PTT SELECT = DAKY (uses Pin 3)
- Use 6-pin Mini-DIN, NOT the 8-pin (that's for different functions)

---

## 🔄 Automated Band Switching

### Concept

Automatically switch antennas and/or bands based on propagation conditions, time of day, or scheduled events.

### Approaches

**1. Propagation-Based Switching**

Use tools that predict band openings:
- **VOACAP** — Voice of America Coverage Analysis Program
- **ITURHFProp** — ITU propagation prediction
- **HamCAP** — combines VOACAP with grayline

**How it works:**
- Software reads propagation predictions
- Determines best band for given path/time
- Sends CAT command to radio to change bands
- Switches antenna via relay/box

**2. Time-Based Switching**

Simple scheduler:
- 00:00-06:00: 80m/40m (night)
- 06:00-12:00: 40m/20m (morning)
- 12:00-18:00: 20m/15m (afternoon)
- 18:00-24:00: 40m/20m (evening)

**3. Beacon-Based Switching**

Monitor propagation beacons:
- Listen for NCDXF/IARU beacons on each band
- Automatically switch to band with strongest beacon
- Software: BeaconSEE, DX Atlas

### Hardware Options

**Antenna switches:**
- MFJ-1708B — 2-port remote switch
- Ameritron RCS-10 — 8-position switch
- Build your own with Arduino + relay board

**CAT control scripts:**
```python
# Example Python script for band switching
import serial
import time

# Open CAT port
ser = serial.Serial('COM3', 4800)

# Change to 20m
def set_band_20m():
    ser.write(b'FA00014070000;')  # Set freq to 14.070 MHz
    
# Change to 40m
def set_band_40m():
    ser.write(b'FA00007070000;')  # Set freq to 7.070 MHz
```

### WSJT-X Band Hopping

WSJT-X has built-in band hopping:
- Set multiple frequencies in Settings → Frequencies
- Enable "Auto" mode
- Software cycles through bands automatically
- Useful for WSPR beaconing

---

## 📊 Waterfall Display Deep Dive

### What You're Seeing

The waterfall is a **spectrogram** — time on the vertical axis, frequency on the horizontal axis, signal strength represented by color.

**How to read it:**
- **Horizontal line** = continuous carrier
- **Vertical stripe** = impulse noise (lightning, switchmode PSU)
- **Diagonal lines** = drift (usually temperature-related)
- **Bright spots** = strong signals
- **Dark areas** = quiet/noise floor

### Signal Signatures

**FT8 signals:**
- 50 Hz wide "stripes"
- 15-second periodic transmissions
- Synchronized across the band

**FT4 signals:**
- 90 Hz wide
- 7.5-second cycles
- Faster "flickering" appearance

**PSK31 signals:**
- Very narrow (~31 Hz)
- Continuous (not burst)
- Wider "wings" when transmitting data

**CW signals:**
- Dashes and dots visible as dashes/dots
- Can often read CW visually on waterfall

**Noise sources:**
- Broadband horizontal lines = switchmode power supplies
- Intermittent vertical lines = arcing (power lines, bad connections)
- Wavy patterns = drifting oscillators

### Optimizing Your Waterfall

**Settings in WSJT-X:**
- **Bins/Pixel:** Higher = more detail, slower update
- **Start/Stop frequencies:** Widen to see more activity
- **Sensitivity:** Adjust so noise floor is visible but not overwhelming
- **Color map:** Personal preference (try different schemes)

**Interpreting colors:**
- Black/dark blue = no signal
- Yellow/green = moderate signal
- Red/white = strong signal (may be overdriving)

### Advanced Uses

**Finding weak signals:**
- Look for faint traces below the noise
- Use narrow filter (JT9 mode) for extremely weak signals
- Compare multiple decode cycles

**Identifying interference:**
- Continuous carriers = local oscillator leakage
- Periodic bursts = switching power supplies
- Broadband noise = plasma TVs, solar inverters

---

## 🏗️ Building a Digital Mode Station From Scratch

### Complete Shopping List

**Radio:**
- Yaesu FT-891 ($600-700) — recommended starter
- Or: Icom IC-7300 ($1100) — SDR receiver, better waterfall
- Or: Xiegu G90 ($450) — budget option, built-in soundcard

**Computer:**
- Any modern PC/laptop (Windows/Mac/Linux)
- Needs: USB ports, soundcard
- Optional: Second monitor for waterfall

**Interface (choose one):**
- **DigiRig Mobile** ($50) — compact, CAT + audio
- **SignaLink USB** ($120) — proven, external soundcard
- **Homemade interface** ($20) — audio transformers + PTT circuit
- **No interface** (VOX only) — works but less reliable

**Antenna:**
- End-fed halfwave (EFHW) — multiband, easy deploy
- Dipole — simple, effective for one band
- Vertical — compromise, needs radials
- Tuner: mAT-30 or mAT-180H for matching

**Power:**
- 13.8V power supply (30A minimum for 100W)
- Or: LiFePO4 battery for portable (12AH minimum)

**Cables:**
- USB A-to-B for CAT control
- Audio cables (3.5mm TRS)
- Coax (RG-8X or better)
- Power cable (12ga minimum)

### Assembly Order

1. Set up radio + antenna
2. Test SSB operation first (verify RX/TX)
3. Connect interface + computer
4. Install drivers (Silicon Labs CP210x)
5. Install WSJT-X
6. Configure CAT control
7. Test with dummy load or low power
8. Adjust audio levels (ALC at 0)
9. Make first digital QSO!

### Budget Tiers

**Bare minimum (~$650):**
- Used FT-891 or Xiegu G90
- Homemade interface or VOX
- Wire antenna (dipole or EFHW)
- Laptop you already own

**Recommended (~$900):**
- FT-891
- DigiRig Mobile
- MFJ EFHW antenna kit
- Quality power supply

**Premium (~$1500):**
- Icom IC-7300
- SignaLink USB
- Multi-band dipole or beam
- Linear power supply (quiet)

---

## 🖼️ QSL Card Machine Learning Recognition

### Concept

Train ML models to:
- Extract QSO data from QSL card images
- Read callsigns, dates, times, frequencies
- Verify card authenticity
- Auto-fill logbook entries

### Technical Approach

**Pipeline:**
1. Scan/upload QSL card image
2. OCR (Optical Character Recognition) — Tesseract, EasyOCR
3. Named Entity Recognition — identify callsign, date, etc.
4. Data validation — verify against known QSO
5. Logbook entry — auto-fill logging software

**Challenges:**
- Handwritten cards (vs printed)
- Variable layouts/designs
- Non-English text
- Poor image quality
- Creative/fancy fonts

**Current state:**
- OCR works well on printed cards
- Handwriting recognition still unreliable
- No purpose-built ham QSL ML tool exists
- Generic OCR (Google Vision, AWS Textract) viable for printed cards

**Potential project:**
Build web app that:
- Uploads QSL card photo
- Runs OCR + NER
- Presents extracted data for review
- Exports ADIF for logbook import

---

## 🤖 AI Elmer Chatbot

### Concept

An AI-powered "Elmer" (ham radio mentor) that answers questions, explains concepts, and guides new operators.

**What it could do:**
- Answer questions about regulations (FCC rules)
- Explain antenna theory
- Help troubleshoot radio problems
- Teach CW (Morse code)
- Explain propagation
- Recommend equipment
- Quiz for license exam prep

**Technical stack:**
- Base: GPT/Claude with ham radio knowledge
- Fine-tuning: On ARRL manuals, exam question pools
- RAG: Retrieve from FCC rules, band plans, technical references
- Voice: Optional TTS for "radio feel"

**Challenges:**
- Safety critical (can't give wrong info on RF exposure)
- Real-time vs async (should it respond like a conversation?)
- Verification of technical accuracy

**Existing efforts:**
- Various Discord bots for ham radio
- Some exam prep apps use AI
- No prominent open-source Elmer AI yet

**Development opportunity:**
Build a ham radio RAG system:
- Ingest ARRL handbooks, FCC rules, technical references
- Create vector database
- Query with natural language
- Include citations for verification

---

## 📡 Digital Mode Etiquette & DXing Strategies

### General Etiquette

**Calling frequencies (don't call CQ here):**
- 7.074 MHz (40m FT8)
- 14.074 MHz (20m FT8)
- 21.074 MHz (15m FT8)
- 28.074 MHz (10m FT8)

**Calling CQ:**
- Move 1-3 kHz away from calling frequency
- Announce "CQ DX" or "CQ NA" for regional
- Listen first — don't step on existing QSOs

**Answering a CQ:**
- Call on their frequency (not offset)
- One call only — if no reply, they didn't hear you
- Don't call if you can't copy them fully

**Completed QSO:**
- Send RR73 or 73
- Don't keep calling after clear end
- Log it, move on

### DXing Strategies

**Working DXpeditions:**
- Use split mode (listen on their freq, TX up 1-5 kHz)
- Follow their instructions (they may specify freq)
- Be patient — thousands trying same station
- Don't double (transmit without hearing reply)

**Rare DX (ATNO — All Time New One):**
- Pounce mode (S&P), don't call CQ
- Use DX cluster spots to find them
- Be ready to change bands quickly
- Accept that pileups are slow

**FT8 DX Specifics:**
- Use Fox/Hound mode for DXpeditions
- Fox = rare station, multiple Hounds call
- Software manages the queue automatically
- Much more efficient than manual pileup

**Grid Square Collecting:**
- Goal: Work all grid squares ( Maidenhead system)
- GridTracker tracks progress
- Target grids via callsign lookup
- Some awards: VUCC (6m), WAS (Worked All States)

### Avoid These Behaviors

- **Calling without listening** (stepping on QSOs)
- **Overdriving** (messy signal, splatter)
- **Calling endlessly** (if they don't reply, they can't hear you)
- **Not using UTC time** (confuses logging)
- **Wrong frequency for region** (check band plans)

---

## 🔗 Sources

- PSK31 Operation: https://bpsk31.com/operation/
- PSK31 Getting Started: https://www.tinymicros.com/wiki/PSK31_Getting_Started
- FT4 Protocol Paper: https://wsjt.sourceforge.io/FT4_Protocol.pdf
- FT8 vs FT4: https://e-norge.com/2025/03/16/ft8-vs-ft4-a-comparison-of-digital-modes-in-amateur-radio/
- FT8 vs FT4 (VU3DXR): https://vu3dxr.in/ft8-vs-ft4-choosing-right-digital-mode-for-weak-signal/
- 6-Pin Mini-DIN: https://hamradiodx.net/yaesu-icom-kenwood-data-port/
- VOACAP Propagation: https://www.voacap.com/
- WSJT-X Documentation: https://physics.princeton.edu/pulsar/k1jt/wsjtx-doc/wsjtx-main-2.6.1.html

---

## Research Status Update

**All 18 topics now complete:**

| Priority | Topic | Status |
|----------|-------|--------|
| 1 | AI applications in ham radio | ✅ |
| 1 | AI tools for shack | ✅ |
| 1 | Propagation prediction | ✅ |
| 1 | AI antenna modeling | ✅ |
| 1 | QSL card ML | ✅ |
| 1 | AI Elmer chatbot | ✅ |
| 2 | FT8 setup | ✅ |
| 2 | JS8Call | ✅ |
| 2 | PSK31 | ✅ |
| 2 | FT4 vs FT8 | ✅ |
| 2 | Digital etiquette/DXing | ✅ |
| 3 | FT-891 CAT control | ✅ |
| 3 | Menu settings | ✅ |
| 3 | WSJT-X config | ✅ |
| 3 | Digimode-4 interface | ✅ |
| 3 | Mobile/portable | ✅ |
| 3 | Data port pinout | ✅ |
| 4 | Remote station (Pi) | ✅ |
| 4 | Band switching | ✅ |
| 4 | Digital contesting | ✅ |
| 4 | Waterfall display | ✅ |
| 4 | Station from scratch | ✅ |

---

*Saved to Night School: docs/night-school/ham-radio-ai/*
*Synced to NAS: \\MND\web\night-school\ham-radio-ai/*
