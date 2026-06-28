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
- [ ] AI-powered antenna modeling (EZNEC + AI optimization)
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
- [ ] Mobile/portable digital operation with FT-891
- [ ] FT-891 data port pinout and custom cables

### Priority 4: Advanced Topics
- [ ] Remote station operation via Raspberry Pi
- [ ] Automated band switching based on propagation
- [ ] Digital mode contesting strategies
- [ ] Building a digital mode station from scratch
- [ ] Understanding the waterfall display

---

## Knowledge Base

**File:** `docs/night-school/ham-radio-ai/research-2026-06-27.md`

### Key Takeaways (so far)

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

---

## Resources

### Software
- WSJT-X: https://physics.princeton.edu/pulsar/k1jt/wsjtx.html
- JS8Call: https://js8call.com/
- GridTracker: https://gridtracker.org/
- HamClock: https://clearskyinstitute.com/ham/HamClock/

### Drivers
- Silicon Labs CP210x: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

### Guides
- FT-891 Digital Setup: https://www.ham-interfaces.com/ham-radio-info-and-guides/how-to-set-up-yaesu-ft-891-for-digital-modes
- KB9VBR Guide: https://www.jpole-antenna.com/2020/08/12/yaesu-ft-891-setup-for-digital-modes/
- KM4NMP Guide: https://km4nmp.com/2019/07/21/getting-started-with-wsjt-x-and-the-yaesu-ft-891-transceiver/

### Communities
- r/amateurradio
- QRZ Forums: Digital Modes section
- WSJT-X user group

---

## Next Research Topics

1. **FT-891 with Digimode-4 interface** — detailed wiring and audio levels
2. **Mobile digital operation** — portable FT8 from the car
3. **Contest logging automation** — N1MM+ with digital modes
4. **AI propagation tools** — VOACAP vs machine learning models

---

*Created: 2026-06-27*
*Last Updated: 2026-06-27*
