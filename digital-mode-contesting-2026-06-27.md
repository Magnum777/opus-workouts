# Digital Mode Contesting with FT8/WSJT-X

> Research date: 2026-06-27
> Researcher: Nova (for OpusMagnum / WR4MG)

---

## 🏆 Why Digital Contesting?

FT8 has revolutionized contesting — it lets you work stations you couldn't hear in SSB/CW. Weak signals decode automatically. Propagation matters less. It's a different skill set from traditional contesting.

---

## 📋 Contest-Specific Setup

### WSJT-X Configuration for Contests

**UDP Server Setup (for integration with loggers):**
1. File → Settings → Reporting tab
2. UDP Server section:
   - ✅ Accept UDP requests
   - ✅ Notify on accepted UDP request
   - ✅ Accepted UDP request restores window
3. Enable logged contact ADIF Broadcast: **UNCHECK** (deprecated)

**Contest Mode Settings:**
- Set "DX Call" mode (not "Fox/Hound" unless rare DX)
- Disable "Automatically log QSOs" if using external logger
- Enable "Double-click on call sets TX enable"
- Set TX power to ~25-50W (don't overdrive)

### N1MM Logger+ Integration

**The Three-Program Stack:**
```
WSJT-X (decodes FT8) → JTAlert (filters/alerting) → N1MM+ (logging/scoring)
```

**Configuration Steps:**

1. **Create separate INI files for N1MM:**
   - Copy `N1MM Logger.ini` to `N1MM Logger - Radio.ini`
   - Copy `N1MM Logger.ini` to `N1MM Logger - WSJT-X.ini`

2. **JTAlert Settings:**
   - Settings → Manage Settings → Logging → Last QSO API
   - ✅ Enable transmission of last QSO
   - UDP Port: 2237 (default)
   - Applications → WSJT-X/JTDX
   - ❌ Uncheck "Rebroadcast WSJT-X UDP Packets"

3. **N1MM Digital Interface Window:**
   - Window → WSJT Decode List
   - Shows all decoded stations in real-time
   - Click to auto-fill call + report
   - Color coding for multipliers/new bands

---

## 🎯 Contest Strategies for FT8

### Calling CQ vs S&P

**CQ (Run):**
- Pick clear frequency slightly away from standard calling freqs
- Enable "Hold Tx Freq" to stay put
- Higher rate if you have good antenna/location
- Risk: Frequency collisions

**Search & Pounce:**
- Scan waterfall for stations calling CQ
- Double-click to answer
- Better for weaker stations
- Slower rate but more reliable

### FT8 Contest Specifics

**Exchange formats:**
- Most contests use: RST + Grid (e.g., -10 EM73)
- Some use serial numbers
- Contest mode in WSJT-X handles this automatically

**Band strategy:**
- Start on higher bands (20m, 15m) when open
- Move to 40m/80m as bands close
- 6m/2m if VHF contest and conditions right

**Rate optimization:**
- FT8 cycle is 15 seconds (13.5s transmit + 1.5s decode)
- Max theoretical rate: ~240 QSOs/hour
- Realistic rate: 100-150/hour on a good run
- Compare to CW: ~150-200/hour, SSB: ~100-150/hour

---

## 📊 WSJT-X Decode List Window (N1MM+)

### What It Shows

- Real-time list of all decoded stations
- Color coding:
  - Green = New multiplier
  - Yellow = New band for station worked
  - Red = Already worked (dup)
  - White = New station

### Features

- **Auto-fill:** Click station → auto-enters in N1MM
- **Filtering:** Show only new multipliers, specific bands
- **Spotting:** Automatically spots to DX cluster
- **Rate display:** Shows current QSO rate

---

## 🔧 Advanced Contesting Tools

### JTAlert for Contesting

**Key features:**
- Alert on new DXCC entities
- Alert on needed contest multipliers
- Alert on specific callsigns (buddies, rare stations)
- Logging integration with N1MM, DXLab, HRD

**Setup:**
- Configure alerts for " needed for award"
- Set audio alerts for important stations
- Use "Alert Filter" to reduce noise

### BandMap Integration

N1MM BandMap shows:
- Spots from telnet/DX cluster
- Color-coded by band/mode
- Click to tune radio + set mode
- Integrates with WSJT-X spots

### UDP Packet Flow

```
WSJT-X (decodes station)
  ↓ UDP broadcast
JTAlert (filters, adds alerts)
  ↓ UDP broadcast
N1MM+ (logs QSO, updates score)
  ↓ UDP broadcast
External programs (spotting, etc.)
```

---

## 🏁 Specific Contest Setups

### ARRL RTTY Roundup

- Use RTTY mode in FLDigi or MMTTY
- N1MM has dedicated RTTY interface
- WSJT-X not typically used (too slow)

### FT8 Roundup / FT8 Contests

- WSJT-X contest mode
- Custom frequencies may be used (not standard FT8 freqs)
- Add contest frequencies to WSJT-X frequency table:
  - Settings → Frequencies tab
  - Add rows for contest-specific frequencies

### PACC Digi (Dutch Contest)

- Uses non-standard FT8 frequencies
- Must configure WSJT-X frequency table
- See VERON setup guide for exact frequencies

### State QSO Parties

- Mix of FT8 and SSB/CW
- N1MM supports multiple modes simultaneously
- Use separate INI files for digital vs voice

---

## ⚡ Tips for FT8 Contesting

1. **Don't overdrive:** ALC meter should barely move. Overdriving = harmonics = interference

2. **Use lower power:** 25-50W is plenty for FT8. Save finals, reduce heat.

3. **Sync clock:** FT8 requires <1 second accuracy. Use Dimension 4, Meinberg, or GPS time sync.

4. **Learn keyboard shortcuts:**
   - `F1` = CQ
   - `F2` = Answer CQ
   - `F3` = Send report
   - `F4` = Send RRR/RR73
   - `F5` = Log QSO

5. **Monitor your rate:** N1MM shows QSOs/hour. Adjust strategy if rate drops.

6. **Spotting:** Enable auto-spotting in N1MM. Helps others find you.

7. **Backup logging:** If N1MM crashes, WSJT-X logs to ADI file. Don't lose QSOs.

---

## 🔗 Resources

**N1MM Documentation:**
- WSJT Decode List: https://n1mmwp.hamdocs.com/manual-windows/wsjt-x-decode-list-window/
- UHF/VHF Setup: https://n1mmwp.hamdocs.com/manual-supported/contests-setup/setup-uhf-contests/

**Integration Guides:**
- WSJT-X + JTAlert + N1MM: https://w3mie.org/2021/02/18/how-to-get-wsjt-x-jtalert-and-n1mm-logger-all-working-together/
- PACC Digi Setup: https://www.veron.nl/wp-content/uploads/2021/03/WSJT-X_eng-v4.pdf

**Software:**
- N1MM Logger+: https://n1mmwp.hamdocs.com/
- JTAlert: https://hamapps.com/
- WSJT-X: https://physics.princeton.edu/pulsar/k1jt/wsjtx.html

---

## 📝 Research Notes

**What we learned:**
- FT8 contesting requires tight integration between WSJT-X and logger
- N1MM+ is the gold standard for contest logging
- JTAlert provides essential filtering/alerting layer
- UDP packet flow is the backbone of digital contesting
- Separate INI files for N1MM lets you switch between contest configs
- Clock sync is critical for FT8 (sub-second accuracy)

**Key insight:**
Traditional contesters sometimes dismiss FT8 as "too easy," but the skill shifts to strategy, propagation awareness, and software integration rather than copying calls in noise.

**Next research topics:**
- [ ] Specific contest rules (ARRL, CQ WW) for digital
- [ ] RTTY contesting setup with FLDigi
- [ ] Remote contesting via Pi + N1MM
- [ ] Multi-operator digital contest stations

---

*Saved to Night School: docs/night-school/ham-radio-ai/*
