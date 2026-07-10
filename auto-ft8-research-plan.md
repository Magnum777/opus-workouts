# Auto FT8 Research & Implementation Plan

> Research date: 2026-06-27
> Researcher: Nova (for OpusMagnum / WR4MG)

---

## 🎯 Goal

Build an auto-FT8 system that automates the repetitive parts of FT8 operating while staying within legal bounds (control operator present, not truly unattended).

---

## 📊 Research Findings: What Exists

### Commercial/Closed Source

**1. Hamilton Auto FT8 (autoft8.com)**
- **Status:** Active, Windows only, ~$33MB installer
- **How it works:** Auto-clicks WSJT-X UI, intercepts decodes, auto-responds
- **Features:** Filters by signal strength, continent, CQ zone, LoTW status, award needs
- **Legal disclaimer:** "Automation is allowed. Unattended operation is not."
- **Limitation:** Windows only, closed source, requires WSJT-X 2.5+
- **Risk:** Auto-clicker approach is fragile, can break with WSJT-X updates

**2. WSJT-Z (sq9fve/wsjt-z)**
- **Status:** Modified WSJT-X with extended automation
- **How it works:** Fork of WSJT-X with built-in automation features
- **Features:** Enhanced decoder pipeline, advanced filtering, automation hooks
- **Limitation:** Must replace your WSJT-X install, may not keep up with official updates

### Open Source Projects

**3. FT8Commander (0x9900/FT8Commander)**
- **Status:** ARCHIVED (2021), 7 stars
- **Language:** Python
- **How it works:** Reads WSJT-X UDP packets, sends CAT commands back
- **Approach:** Intercepts decode messages, decides which to answer, sends CAT PTT/freq
- **Limitation:** ARCHIVED, no longer maintained

**4. FT8Commander Fork (roamingryan/FT8Commander)**
- **Status:** Fork of above, minimal activity
- **Same approach:** UDP packet interception + CAT control

**5. AutoFT8 (0x9900/AutoFT8)**
- **Status:** ARCHIVED (2021), BSD license
- **Language:** Python
- **Approach:** Similar UDP-based automation

**6. Ultron (egislev/ultron)**
- **Status:** Active (2023), 4 stars
- **Language:** PHP
- **Approach:** Automatic control of JTDX/WSJT-X/MSHV
- **Limitation:** PHP-based, unusual choice for radio automation

**7. Otto (avantol/Otto)**
- **Status:** Active (2024), 25 stars
- **Language:** C#
- **Approach:** "Assistant for WSJT-X" — helps with repetitive tasks
- **Features:** Likely macro-based automation, not full auto-QSO

**8. WSJTX-Controller (avantol/WSJTX-Controller)**
- **Status:** Active (2020), 19 stars
- **Language:** C#
- **Approach:** "Automation for repetitive manual tasks"
- **Likely scope:** Macros, logging, not full QSO automation

**9. JI1FGX/DU9 Auto Operation**
- **Status:** Active (2026), Japanese developer
- **Approach:** Custom software for WSJT-X auto-operation
- **Limitation:** Japanese language primarily, may be JTDX-focused

### Libraries & Protocols

**10. py-wsjtx (MeadeRobert/py-wsjtx)**
- **Status:** Active, Python library
- **Purpose:** Interpret/generate UDP packets for WSJT-X communication
- **Use:** Foundation for building custom automation

**11. wsjtx-mcp (PyPI)**
- **Status:** Active, v0.1.2
- **Purpose:** MCP server that controls WSJT-X over UDP
- **Use:** Integration with Claude Desktop / MCP ecosystem

**12. wsjtx-udp-bridge (vincois/wsjtx-udp-bridge)**
- **Status:** Minimal, 1 star
- **Purpose:** UDP bridge between WSJT-X and other applications
- **Note:** "Vibe coded with Claude"

**13. ft8decoder (PyPI)**
- **Status:** Alpha, v1.0.0
- **Purpose:** FT8 message logger — tracks CQs, QSOs, misc messages
- **Use:** Monitoring/logging, not automation

**14. FT8 Band Opening Detector (HA2ZB)**
- **Status:** New (2026), Orange Pi based
- **Purpose:** Detect propagation changes by monitoring FT8 decodes
- **Use:** Propagation analysis, not QSO automation

---

## 🔬 Technical Analysis

### WSJT-X UDP Protocol

WSJT-X broadcasts UDP packets on port 2237 (default) containing:
- **Decode messages:** Callsign, grid, signal report, frequency
- **Status messages:** Current frequency, mode, TX state
- **QSO logged:** ADIF data when QSO completes

**Inbound commands (to WSJT-X):**
- `Replay`: Reopen CQ window
- `Halt TX`: Stop transmission
- `Free Text`: Set free text message
- `Highlight Callsign`: Mark station in band display
- `Switch Mode`: Change mode (FT8/FT4/etc.)

**What you CAN'T do over UDP:**
- Directly trigger TX (no "start transmitting" command)
- Set frequency directly
- Click "Enable Tx" button

**Workarounds for TX control:**
1. **CAT commands** via serial port (set frequency, PTT)
2. **UI automation** (AutoHotkey, pyautogui) to click buttons
3. **Modified WSJT-X** (compile from source with automation hooks)

### Two Architectures

**Architecture A: UDP + CAT (Recommended)**
```
WSJT-X → UDP packets → Our script (reads decodes)
Our script → CAT commands → Radio (PTT, freq change)
Our script → UI automation → WSJT-X (click Enable Tx)
```

**Architecture B: Modified WSJT-X**
```
Fork WSJT-X source → Add automation hooks → Compile custom version
More reliable but maintenance burden
```

---

## ⚖️ Legal Analysis (FCC Part 97)

### What's Allowed

- **Automation of repetitive tasks** (macro-style)
- **Auto-logging** after manual QSO
- **Decode monitoring** and alerting
- **Band hopping** with manual initiation

### What's Gray Area

- **Auto-responding to CQs** with control operator present
- **Auto-completing QSO sequences** after you initiate
- **Filtering and queuing** contacts for manual approval

### What's Prohibited

- **Fully unattended operation** (no control operator present)
- **Automatic beaconing** without identifying
- **Botting** for contests/awards without disclosure
- **POTA/SOTA** fully automated QSOs (explicitly banned by those programs)

**Key distinction:** Automation vs unattended. You can automate tasks, but you must be present at the station and able to intervene immediately.

---

## 🏗️ Implementation Plan

### Phase 1: Monitor & Alert (Legal, Useful)

**What it does:**
- Listen to WSJT-X UDP decodes
- Alert you when specific stations appear (DXCC needs, rare grids, buddies)
- Show filtered contact list (hide worked stations, show only new multipliers)
- Log QSOs automatically (after manual completion)

**Tech stack:**
- Python + `py-wsjtx` library
- Simple GUI (tkinter or web)
- Audio alerts (beep or TTS)

**Value:** Helps you focus on operating, not scanning waterfall manually.

### Phase 2: Semi-Auto Assistant (Macro Mode)

**What it does:**
- You click "Want this contact" → script handles the exchange
- Script sends CAT commands to set freq, triggers TX via UI automation
- Auto-fills standard exchanges (your call, grid, report)
- Auto-clicks "Log QSO" after 73 exchange

**Control:**
- Big "STOP" button — kills all automation instantly
- Requires your click to initiate each QSO
- You supervise, it executes

**Tech additions:**
- `pyserial` for CAT control
- `pyautogui` or AutoHotkey for WSJT-X UI clicks
- Configurable macros for different exchange types

### Phase 3: Smart Pounce Mode (Advanced)

**What it does:**
- Scans waterfall for CQs
- Prioritizes based on your needs (new DXCC, grid, state, country)
- Auto-tunes to station, answers CQ
- You watch and can override at any time

**Safety:**
- Requires "ARM" button to be pressed each session
- Auto-disarms after N minutes of inactivity
- All TX logged with timestamp for compliance

### Phase 4: Contest Mode (Optional)

**What it does:**
- Optimized for rate during contests
- Auto-calls CQ, answers callers
- Tracks multipliers, suggests band changes
- Generates contest score summary

**Important:** Only use in contests that explicitly allow automation. Many don't.

---

## 🛠️ Technical Requirements

### Hardware
- Your existing setup: FT-891 + DigiRig + Windows PC
- No additional hardware needed

### Software Dependencies
```
Python 3.10+
py-wsjtx (UDP communication)
pyserial (CAT control)
pyautogui (UI automation - optional)
tkinter (GUI)
```

### CAT Commands for FT-891
```
Set frequency: FA014074000; (14.074 MHz)
PTT ON: TX1;
PTT OFF: TX0;
Get frequency: FA;
```

### UI Automation Points
- Click "Enable Tx" button (coordinates on screen)
- Click "Log QSO" button
- Double-click on callsign in decode list

**Challenge:** WSJT-X UI changes between versions. Coordinate-based automation breaks.
**Mitigation:** Use window titles, relative positions, or WSJT-X's built-in keyboard shortcuts where possible.

---

## 📋 Development Roadmap

### Week 1: Proof of Concept
- [ ] Install py-wsjtx, verify UDP decode reading
- [ ] Build simple decoder monitor (print callsigns to console)
- [ ] Add filtering (show only CQ calls, or only new DXCC)

### Week 2: CAT Control
- [ ] Test CAT commands with FT-891 via serial port
- [ ] Build frequency setter, PTT controller
- [ ] Integrate with UDP decode reader

### Week 3: Macro Assistant
- [ ] Build "Answer this CQ" button
- [ ] Script handles exchange sequence
- [ ] Add STOP button for emergency

### Week 4: GUI & Polish
- [ ] Build tkinter GUI with waterfall-like contact list
- [ ] Add configuration (callsign, grid, awards tracking)
- [ ] Test with real QSOs on air

### Week 5: Advanced Features
- [ ] Smart filtering (LoTW users, specific continents)
- [ ] Grid/DXCC tracking integration
- [ ] Contest mode prototype

---

## 🚨 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| WSJT-X UI changes | High | High | Use CAT + UDP, minimize UI automation |
| Legal issues (unattended) | Medium | High | Require operator presence, STOP button |
| Contest disqualification | Low | Medium | Only use in allowed contests, disclose |
| Broken QSOs (missed decodes) | Medium | Low | Fallback to manual, log attempts |
| RFI/interference | Low | High | Auto-PTT timeout, audio alert on long TX |

---

## 🔗 Resources

**Existing Tools:**
- Hamilton Auto FT8: https://autoft8.com/
- FT8Commander: https://github.com/0x9900/FT8Commander (archived)
- Otto: https://github.com/avantol/Otto
- WSJTX-Controller: https://github.com/avantol/WSJTX-Controller

**Libraries:**
- py-wsjtx: https://github.com/MeadeRobert/py-wsjtx
- wsjtx-mcp: https://pypi.org/project/wsjtx-mcp/

**Protocol Docs:**
- WSJT-X UDP Protocol: https://physics.princeton.edu/pulsar/k1jt/wsjtx-doc/wsjtx-main-2.6.1.html

---

## 🎯 Recommended Approach

**Start with Phase 1 (Monitor & Alert).** It's immediately useful, zero legal risk, and teaches you the UDP protocol. Then decide if you want to go further.

**Phase 2 (Semi-Auto Assistant)** is the sweet spot: you still operate, but the computer handles the button-mashing. Think of it like a CNC machine — you set it up and supervise, it does the repetitive work.

**Phases 3-4** are for after you've proven Phase 2 works and you're comfortable with the legal implications.

---

*Saved to Night School: docs/night-school/ham-radio-ai/*
*Synced to NAS: \\MND\web\night-school\ham-radio-ai/*
