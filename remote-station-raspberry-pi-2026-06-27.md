# Remote Ham Radio Station via Raspberry Pi

> Research date: 2026-06-27
> Researcher: Nova (for OpusMagnum / WR4MG)

---

## 🎯 Concept

Control your HF station remotely from anywhere using a Raspberry Pi as the on-site controller. Access your home station while traveling, operate from work, or share your station with friends.

---

## 📋 Network Architecture

### Port Requirements

| Port | Protocol | Purpose |
|------|----------|---------|
| 22 | TCP | SSH remote console |
| 5900 | TCP | VNC remote screen |
| 5209 | TCP | CRX-COM (radio control) |
| 5210 | TCP | FLRIG (radio control alt) |
| 64538 | TCP+UDP | MUMBLE (remote audio VOIP) |
| 8110 | UDP | SEREN (audio alt) |

### Connection Options

**Option A: Direct Internet (port forwarding)**
- Open ports on router/firewall
- Exposes station to internet (security risk)
- Use strong passwords + key auth

**Option B: VPN (recommended)**
- OpenVPN or WireGuard tunnel
- All traffic encrypted
- Only VPN port exposed
- Much more secure

---

## 🖥️ Raspberry Pi Setup

### Hardware Requirements

- Raspberry Pi 4 (4GB+ RAM recommended)
- Micro SD card (32GB+, high endurance)
- USB sound card (CM108 chipset ~$10)
- Network cable (ethernet preferred over WiFi)
- Optional: USB hub if multiple devices

### Software Stack

**Base OS:** Raspberry Pi OS with Desktop (Bookworm/Debian 12)

**Core Applications:**
- WSJT-X (FT8/FT4 operation)
- FLRIG (radio control)
- FLdigi (digital modes)
- CRX-COM (remote CAT control)
- MUMBLE (remote audio)
- VNC server (remote desktop)

### Installation Steps

**1. OS Setup**
```bash
# Burn Raspberry Pi OS to SD card
# Enable SSH: create empty 'ssh' file in boot partition
# Boot Pi, note IP address
```

**2. Initial Config**
```bash
sudo raspi-config
# Enable SSH (Interface Options > SSH)
# Set hostname
# Configure network (static IP recommended)
```

**3. Create Secure User**
```bash
sudo useradd -m -G adm,dialout,sudo,audio,video,netdev ham
sudo passwd ham
# Add SSH key auth
mkdir /home/ham/.ssh
chmod 700 /home/ham/.ssh
```

**4. Remove Default User**
```bash
sudo pkill -u pi
sudo deluser --remove-home pi
```

**5. Sound Card Config**
```bash
# Disable built-in audio
sudo vim /etc/modprobe.d/raspi-blacklist.conf
# Add: blacklist snd_bcm2835

# Configure USB sound card
# Find card number: aplay -l
# Set in /usr/share/alsa/alsa.conf:
defaults.ctl.card 2
defaults.pcm.card 2
```

**6. Install Ham Software**
```bash
# WSJT-X
sudo apt install wsjtx

# FLRIG/FLdigi
sudo apt install fldigi flrig

# MUMBLE
sudo apt install mumble-server mumble

# VNC
sudo apt install tightvncserver
```

**7. Firewall (UFW)**
```bash
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.1.0/24 to any port 22
sudo ufw allow from 192.168.1.0/24 to any port 5900
sudo ufw enable
```

---

## 🔌 Radio Interface

### CAT Control Options

**Option 1: FLRIG**
- Runs on Pi
- Controls radio via USB CAT cable
- Remote client connects over network
- Port 5210/tcp

**Option 2: CRX-COM**
- Custom remote control protocol
- Port 5209/tcp
- Integrates with various loggers

**Option 3: Direct USB Passthrough**
- If using VPN, some setups can pass USB over IP
- More complex, less reliable

### Audio Routing

**MUMBLE VOIP Setup:**
- Mumble server on Pi (or cloud)
- Radio audio → Pi mic input → Mumble
- Remote operator hears audio via Mumble client
- Two-way audio for SSB, not needed for digital modes

**For Digital Modes (FT8):**
- WSJT-X runs on Pi
- Audio stays local (Pi → radio via USB soundcard)
- Remote operator uses VNC to control WSJT-X GUI
- No audio streaming needed — just screen + CAT

---

## 🖥️ Remote Client Setup

### Access Methods

**1. VNC (full desktop)**
- TightVNC / RealVNC client
- Connect to Pi desktop
- Run WSJT-X, FLdigi natively on Pi
- Best for digital modes

**2. SSH (command line)**
- Terminal access for maintenance
- Script automation
- Not for GUI applications

**3. Web Interface (optional)**
- Some ham software has web UIs
- RigPi Station Server provides web control
- Simpler but less flexible

### WSJT-X Specific Remote Operation

**Running on Pi via VNC:**
1. VNC into Pi desktop
2. Launch WSJT-X
3. Configure radio (FT-891 via CAT)
4. Operate as if sitting at station
5. Log QSOs to local database or sync via cloud

**Performance notes:**
- Pi 4 handles WSJT-X + VNC fine for FT8
- Audio sync not critical (digital modes handle timing)
- Screen refresh over VNC is usable for FT8 cadence

---

## 🔒 Security Considerations

### Essential Hardening

```bash
# Disable root login
sudo vim /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no  # Use keys only

# Fail2ban (block brute force)
sudo apt install fail2ban

# Keep software updated
sudo apt update && sudo apt upgrade -y
```

### VPN Setup (Recommended)

**OpenVPN Server on Pi:**
```bash
sudo apt install openvpn easy-rsa
# Generate certificates
# Configure server.conf
# Forward UDP 1194 on router
```

**Client connects via VPN, then accesses Pi as if on LAN:**
```
# No exposed ports except VPN
# All traffic encrypted
# Access VNC/SSH via internal VPN IP
```

---

## 📊 Power & Reliability

### Power Management

- Pi consumes ~5-7W continuous
- Use quality 5V/3A PSU
- Consider UPS (PiSugar or similar)
- SD card will fail eventually → use RAMdisk for logs

### RAMdisk for Logs

```bash
# Install log2ram to reduce SD card writes
sudo git clone https://github.com/azlux/log2ram.git
sudo ./log2ram/install.sh
# Reboot
```

### Monitoring

- Install uptime monitoring (optional)
- Temperature monitoring (Pi can throttle if hot)
- Consider watchdog timer for auto-reboot

---

## 🎯 Use Cases

### 1. Remote FT8 Operation
- Pi at home, connected to FT-891
- VNC from work/hotel to operate
- Especially useful for POTA activations from nearby parks

### 2. Shared Station
- Multiple club members access same station
- Schedule time slots
- Centralized logging

### 3. Unattended Operation
- WSJT-X runs continuously
- Remote monitoring via VNC
- Receive rare DX while away

### 4. Digital Mode Gateway
- Pi handles all digital modes
- Remote operator just needs VNC client
- No audio streaming complexity

---

## 🔗 Resources

**Guides:**
- CRX Remote Station Guide: https://project.crx.cloud/Remote_ham_radio_station_setup_guide
- F6CZV Pi Setup: https://f6czv.fr/remote-station-raspberry-pi/
- KK5JY WSJT-X on Pi: https://www.kk5jy.net/wsjtx-build/
- W3YJ NoMachine Setup: https://www.w1hkj.org/W3YJ/Configuring%20Remote%20Operation%20with%20NoMachine%20on%20Bookworm%20on%20Raspberry%20PI.pdf

**Software:**
- WSJT-X: https://physics.princeton.edu/pulsar/k1jt/wsjtx.html
- FLRIG/FLdigi: https://www.w1hkj.org/
- RigPi: https://rigpi.net/
- MUMBLE: https://www.mumble.info/

**Hardware:**
- Raspberry Pi 4: https://www.raspberrypi.com/products/raspberry-pi-4-model-b/
- USB Sound Cards (CM108): Amazon/AliExpress

---

## ⚡ Quick Start Checklist

- [ ] Raspberry Pi 4 with Pi OS installed
- [ ] SSH enabled, default user removed
- [ ] Static IP or DDNS configured
- [ ] USB sound card working (aplay -l shows it)
- [ ] WSJT-X installed and tested locally
- [ ] FLRIG controlling radio via CAT
- [ ] VNC server running
- [ ] Firewall configured (UFW)
- [ ] VPN or port forwarding set up
- [ ] Test remote VNC connection from outside network
- [ ] Test FT8 QSO remotely

---

*Saved to Night School: docs/night-school/ham-radio-ai/*
