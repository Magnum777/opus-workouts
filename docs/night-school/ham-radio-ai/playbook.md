# Ham Radio + AI — Night School Playbook

> Learn how AI interfaces with amateur radio and get your station on digital modes.

---

## Goal

Build practical knowledge about AI-assisted ham radio operating and digital mode setup — specifically for the Yaesu FT-891, but applicable to most modern HF rigs.

---

## Research Queue — COMPLETE ✅

### Priority 1: AI in Ham Radio
- [x] AI applications in amateur radio (propagation, decoding, logging)
- [x] AI tools for the shack (PSK Reporter, HamClock, GridTracker)
- [x] Automated propagation prediction vs manual methods
- [x] AI-powered antenna modeling (EZNEC + AI optimization)
- [x] Machine learning for QSL card recognition
- [x] AI chatbots for ham radio education (Elmer AI)

### Priority 2: Digital Modes Deep Dive
- [x] FT8 setup and configuration
- [x] JS8Call for emergency communications
- [x] PSK31 for keyboard-to-keyboard ragchewing
- [x] FT4 vs FT8: when to use which
- [x] Digital mode etiquette and DXing strategies

### Priority 3: FT-891 Specific
- [x] FT-891 CAT control via USB
- [x] Menu settings for digital modes
- [x] WSJT-X configuration for FT-891
- [x] Using Digimode-4 interface with FT-891
- [x] Mobile/portable digital operation with FT-891
- [x] FT-891 data port pinout and custom cables

### Priority 4: Advanced Topics
- [x] Remote station operation via Raspberry Pi
- [x] Automated band switching based on propagation
- [x] Digital mode contesting strategies
- [x] Building a digital mode station from scratch
- [x] Understanding the waterfall display

---

## Knowledge Base Files

| File | Size | Topic |
|------|------|-------|
| `research-2026-06-27.md` | 3.7KB | FT-891 digital setup |
| `mobile-portable-research-2026-06-27.md` | 6.2KB | Mobile/portable operation |
| `ai-antenna-modeling-2026-06-27.md` | 5.2KB | AI antenna design |
| `remote-station-raspberry-pi-2026-06-27.md` | 7.4KB | Remote station via Pi |
| `digital-mode-contesting-2026-06-27.md` | 6.7KB | FT8 contesting |
| `remaining-topics-2026-06-27.md` | 16.2KB | All remaining topics |

### Total: 45.4KB of research across 18 topics

---

## Key Takeaways

**AI in Ham Radio:**
- AI decodes weak signals humans miss (especially in FT8)
- Automated logging with GridTracker saves time
- Propagation prediction tools use ML on historical data
- QRZ API enables instant callsign lookups
- Antenna Forge shows promise for automated inverse design

**FT-891 Digital Setup:**
- Use USB A-to-B cable to back panel (not Mini-DIN for CAT)
- Install Silicon Labs CP210x drivers first
- Two COM ports appear: lower = RTS PTT, higher = CAT control
- Menu settings: DATA MODE = OTHERS, CAT RATE = 4800+
- WSJT-X: select FT-891 rig, CAT PTT, match baud rate
- 6-pin Mini-DIN: Pin 1 = TX audio, Pin 3 = PTT, Pin 4 = RX audio

**FT4 vs FT8:**
- FT8: 15s cycle, -21 dB sensitivity, better for weak signals/DX
- FT4: 7.5s cycle, -17 dB sensitivity, better for contesting/rate
- Use FT8 when propagation is marginal, FT4 when bands are strong

**PSK31:**
- Real keyboard-to-keyboard conversations (unlike FT8)
- 31 Hz bandwidth, very narrow
- Use RSQ reports instead of RST
- Common freqs: 7.070 MHz, 14.070 MHz
- Software: DigiPan, FLdigi, Ham Radio Deluxe

**Remote Station:**
- Raspberry Pi 4 handles WSJT-X + VNC fine for FT8
- VPN recommended over direct port forwarding
- RAMdisk for logs extends SD card life
- USB sound card required (CM108 ~$10)
- DigiRig Mobile reduces cable mess

**Digital Contesting:**
- N1MM+ is gold standard for contest logging
- Three-program stack: WSJT-X → JTAlert → N1MM+
- UDP packet flow is backbone of integration
- Separate INI files for different contest configs
- Clock sync critical for FT8 (<1 second accuracy)

**Waterfall Display:**
- Horizontal lines = carriers, vertical = impulse noise
- FT8 = 50 Hz stripes, FT4 = 90 Hz faster flickering
- PSK31 = narrow continuous trace
- Adjust bins/pixel for detail vs speed

---

## Resources

### Software
- WSJT-X: https://physics.princeton.edu/pulsar/k1jt/wsjtx.html
- JS8Call: https://js8call.com/
- GridTracker: https://gridtracker.org/
- HamClock: https://clearskyinstitute.com/ham/HamClock/
- N1MM Logger+: https://n1mmwp.hamdocs.com/
- JTAlert: https://hamapps.com/
- FLdigi: https://www.w1hkj.org/

### Hardware
- DigiRig Mobile: https://digirig.net/
- Bioenno Batteries: https://www.bioennopower.com/
- SignaLink USB: https://www.tigertronics.com/

### Drivers
- Silicon Labs CP210x: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

### Guides
- FT-891 Digital Setup: https://www.ham-interfaces.com/ham-radio-info-and-guides/how-to-set-up-yaesu-ft-891-for-digital-modes
- KB9VBR Guide: https://www.jpole-antenna.com/2020/08/12/yaesu-ft-891-setup-for-digital-modes/
- KM4NMP Guide: https://km4nmp.com/2019/07/21/getting-started-with-wsjt-x-and-the-yaesu-ft-891-transceiver/
- TheModernHam Menu Guide: https://themodernham.com/ft-891-the-ultimate-digital-settings-menu-guide-for-digital-modes/
- 6-Pin Mini-DIN: https://hamradiodx.net/yaesu-icom-kenwood-data-port/

### Communities
- r/amateurradio
- QRZ Forums: Digital Modes section
- WSJT-X user group

---

*Playbook complete: 2026-06-27*
*All 18 research topics finished*
*Synced to NAS: \\MND\web\night-school\ham-radio-ai/*
