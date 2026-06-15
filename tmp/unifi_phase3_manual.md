# Phase 3 Manual Configuration Steps

## VLANs (Settings -> Networks)

Create 3 new networks:

### 1. sojourn-office (VLAN 10)
- Name: sojourn-office
- Purpose: Corporate
- VLAN ID: 10
- Gateway IP: 192.168.10.1/24
- DHCP Range: 192.168.10.10 - 192.168.10.250
- DHCP: Enabled

### 2. sojourn (VLAN 20)
- Name: sojourn
- Purpose: Corporate
- VLAN ID: 20
- Gateway IP: 192.168.20.1/24
- DHCP Range: 192.168.20.10 - 192.168.20.250
- DHCP: Enabled

### 3. sojourn-guest (VLAN 30)
- Name: sojourn-guest
- Purpose: Guest
- VLAN ID: 30
- Gateway IP: 192.168.30.1/24
- DHCP Range: 192.168.30.10 - 192.168.30.250
- DHCP: Enabled

## Map WLANs to VLANs (Settings -> WiFi)

For each SSID, set Network/VLAN:
- **sojourn** -> VLAN 20 (sojourn)
- **sojourn-office** -> VLAN 10 (sojourn-office)
- **sojourn-guest** -> VLAN 30 (sojourn-guest)

## Guest Portal (Settings -> Guest Control)

### Basic Settings
- Authentication: Hotspot (Terms of Use)
- Landing Page: Use built-in or custom
- Session Timeout: 12 hours (720 minutes)
- Download Bandwidth: 5120 kbps (5 Mbps)
- Upload Bandwidth: 5120 kbps (5 Mbps)

### Portal Customization
- Title: "Welcome to Sojourn Church"
- Welcome Text: "Guest WiFi Access"
- Terms Text: "By connecting, you agree to use this network for lawful purposes only. Do not transmit sensitive information. Access limited to 12 hours."
- Button Text: "Connect to Internet"
- Footer: "Trouble? sojournchurchtech@gmail.com"
- Logo: Upload sojourn-logo.png

### Security
- Block LAN Access: Yes (isolated guest network)
- Block Multicast: Yes
- Redirect to HTTPS: Yes

## WPA3/PMF (Optional)
On **sojourn** only:
- Security: WPA3 if devices support
- PMF: Required
- Test ProPresenter/streaming gear after enabling
