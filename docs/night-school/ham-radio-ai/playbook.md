# Ham Radio + AI — Night School Playbook

> Learn how AI interfaces with amateur radio and get your station on digital modes.

---

## Goal

Build practical knowledge about AI-assisted ham radio operating and digital mode setup — specifically for the Yaesu FT-891, but applicable to most modern HF rigs.

---

## Research Queue

### Priority 1: AI in Ham Radio
- [x] AI applications in amateur radio (propagation, decoding, logging)
- [x] AI tools for the shack (PSK Reporter, HamClock, GridTracker)
- [x] Automated propagation prediction vs manual methods
- [x] AI-powered antenna modeling (EZNEC + AI optimization)
- [ ] Machine learning for QSL card recognition
- [ ] AI chatbots for ham radio education (Elmer AI)

### Priority 2: Digital Modes Deep Dive
- [x] FT8 setup and configuration
- [x] JS8Call for emergency communications
- [ ] PSK31 for keyboard-to-keyboard ragchewing
- [ ] FT4 vs FT8: when to use which
- [ ] Digital mode etiquette and DXing strategies

### Priority 3: FT-891 Specific
- [x] FT-891 CAT control via USB
- [x] Menu settings for digital modes
- [x] WSJT-X configuration for FT-891
- [ ] Using Digimode-4 interface with FT-891
- [x] Mobile/portable digital operation with FT-891
- [x] FT-891 data port pinout and custom cables

### Priority 4: Advanced Topics
- [x] Remote station operation via Raspberry Pi
- [ ] Automated band switching based on propagation
- [x] Digital mode contesting strategies
- [ ] Building a digital mode station from scratch
- [ ] Understanding the waterfall display

---

## Knowledge Base

### Research Files
- `research-2026-06-27.md` — Base FT-891 digital setup
- `mobile-portable-research-2026-06-27.md` — Mobile/portable operation with DigiRig
- `ai-antenna-modeling-2026-06-27.md` — AI-powered antenna design with NEC2
- `remote-station-raspberry-pi-2026-06-27.md` — Remote station via Raspberry Pi
- `digital-mode-contesting-2026-06-27.md` — Contesting with WSJT-X + N1MM

### Key Takeaways

**AI in Ham Radio:**
- AI decodes weak signals humans miss (especially in FT8)
- Automated logging with GridTracker saves time
- Propagation prediction tools use machine learning on historical data
- QRZ API enables instant callsign lookups

**FT-891 Digital Setup:**
- Use USB A-to-B cable to back panel (not Mini-DIN for CAT)
- Install Silicon Labs CP210x drivers first
- Two COM ports appear: lower = RTS PTT, higher = CAT control
- Menu settings: DATA MODE = OTHERS, CAT RATE = 4800+
- WSJT-X: select FT-891 rig, CAT PTT, match baud rate

**Mobile/Portable:**
- DigiRig Mobile reduces cable mess
- Bioenno 12AH LiFePO4 battery sufficient for most activations
- FT-891 pulls 14.6A at 100W on 160m CW
- Powerpole connectors recommended

**AI Antenna Modeling:**
- Antenna Forge uses NEC2 + openEMS with AI optimization
- Neural network surrogate models predict performance instantly
- Genetic algorithms + ML mutation operators show promise
- No ham-specific AI antenna tools exist yet — development opportunity

**Remote Station:**
- Raspberry Pi 4 handles WSJT-X + VNC fine for FT8
- VPN recommended over direct port forwarding
- RAMdisk for logs extends SD card life
- USB sound card required (CM108 ~$10)

**Digital Contesting:**
- N1MM+ is gold standard for contest logging
- Three-program stack: WSJT-X → JTAlert → N1MM+
- UDP packet flow is backbone of integration
- Separate INI files for different contest configs
- Clock sync critical for FT8 (<1 second accuracy)

---

## Resources

### Software
- WSJT-X: https://physics.princeton.edu/pulsar/k1jt/wsjtx.html
- JS8Call: https://js8call.com/
- GridTracker: https://gridtracker.org/
- HamClock: https://clearskyinstitute.com/ham/HamClock/
- N1MM Logger+: https://n1mmwp.hamdocs.com/
- JTAlert: https://hamapps.com/

### Hardware
- DigiRig Mobile: https://digirig.net/
- Bioenno Batteries: https://www.bioennopower.com/

### Drivers
- Silicon Labs CP210x: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

### Guides
- FT-891 Digital Setup: https://www.ham-interfaces.com/ham-radio-info-and-guides/how-to-set-up-yaesu-ft-891-for-digital-modes
- KB9VBR Guide: https://www.jpole-antenna.com/2020/08/12/yaesu-ft-891-setup-for-digital-modes/
- KM4NMP Guide: https://km4nmp.com/2019/07/21/getting-started-with-wsjt-x-and-the-yaesu-ft-891-transceiver/
- TheModernHam Menu Guide: https://themodernham.com/ft-891-the-ultimate-digital-settings-menu-guide-for-digital-modes/

### Communities
- r/amateurradio
- QRZ Forums: Digital Modes section
- WSJT-X user group

---

## Next Research Topics

1. **PSK31 for ragchewing** — keyboard-to-keyboard conversation mode
2. **FT4 vs FT8 comparison** — speed vs sensitivity tradeoffs
3. **Automated band switching** — propagation-based antenna switching
4. **Waterfall display deep dive** — interpreting what you see

---

*Created: 2026-06-27*
*Last Updated: 2026-06-27*
