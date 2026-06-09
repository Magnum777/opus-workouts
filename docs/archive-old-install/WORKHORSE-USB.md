# WORKHORSE USB — Tethered Portable AI Workstation

**Purpose:** Plug into any PC → Auto-installs tools → Secure tunnel back to your home AI workstation  
**Architecture:** Installs on target → Remote execution (AI runs on YOUR machine, target just displays)  
**Created:** 2026-02-18  
**Updated:** 2026-02-18 (Added auto-install + heartbeat)

---

## 🎯 CONCEPT

### The "Tethered" Model

```
[Target PC] ←——Secure Tunnel——→ [Your Home PC with OpenClaw/Ollama]
   (display only)                      (all AI runs here)
```

**You plug in the USB, it connects back to YOU, and you control everything from your machine.**

---

## 🏗️ ARCHITECTURE

### How It Works

1. **USB contains:**
   - Portable browser (Firefox/Chrome)
   - Tailscale VPN client
   - Minimal config

2. **When plugged in:**
   - Tailscale auto-starts
   - Connects to your private network
   - Opens browser to your OpenClaw gateway

3. **You control YOUR machine:**
   - All AI runs on YOUR GPU
   - Target PC just displays the interface
   - Nothing installed on target

---

## 🧰 WHAT'S ON THE USB

### Core Components

| Item | Purpose | Portable? |
|------|---------|-----------|
| **Tailscale** | VPN tunnel back to home | ⚠️ Installs on target |
| **Node.js** | Runtime for OpenClaw | ⚠️ Installs on target |
| **Ollama** | Local AI (optional) | ⚠️ Installs on target |
| **Firefox/Chrome** | Browser to access OpenClaw | ✅ Portable |
| **OpenClaw** | Your AI agent | ⚠️ Installs on target |
| **Heartbeat script** | Checks in with Nova | Custom |

### Auto-Install Approach

The USB triggers an elevated (admin) command prompt that:
1. Installs Node.js, Tailscale, Ollama on target
2. Starts the services
3. Connects back to your home via Tailscale
4. Runs heartbeat to check in with Nova

### Folder Structure

```
WorkhorseUSB/
├── 📁 installer/           # Auto-install scripts
│   ├── install.ps1         # PowerShell installer (Windows)
│   ├── install.sh          # Bash installer (Mac)
│   └── admin-run.bat       # Triggers elevated prompt
├── 📁 talscale/            # Tailscale config
│   ├── tailscale.conf      # Auth key + settings
│   └── auth-key.txt       # Your Tailscale key
├── 📁 browser/             # Portable browser (optional)
├── 📁 openclaw/           # OpenClaw config
├── 📁 heartbeat/           # Nova heartbeat script
│   ├── heartbeat.ps1      # Windows heartbeat
│   └── heartbeat.sh        # Mac heartbeat
├── 📁 configs/
│   └── settings.json       # Your home IP, ports
├── 📁 docs/                # Setup instructions
├── 📁 payloads/            # Optional: local Ollama models
└── 📄 README.txt           # Quick start (displayed on plug-in)

---

## 🚀 SETUP STEPS

### Part 1: Your Home Machine (Already Done)

1. **Install Tailscale** on your PC
2. **Enable subnet router** or expose OpenClaw port
3. **Firewall:** Allow port 18789 for Tailscale network
4. **Get your Tailscale IP:** `100.x.x.x`
5. **Set up heartbeat listener** on OpenClaw

### Part 4: Mac Auto-Install Script

```bash
#!/bin/bash
# install.sh - Mac auto-install

echo "🧩 Workhorse USB Installer - Mac Edition"

# Check for admin
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️ Please run as sudo"
    sudo "$0"
    exit
fi

# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js
brew install node

# Install Tailscale
brew install tailscale

# Install Ollama (optional)
brew install ollama

# Start Tailscale
tailscale up --authkey-file ./tailscale/auth-key.txt --hostname workhorse-usb

# Start heartbeat
./heartbeat/heartbeat.sh

echo "✅ Installation complete!"
```

```powershell
# Download Tailscale portable
# Get auth key from: https://login.tailscale.com/admin/settings/keys

# Create config file (tailscale.conf):
{
  "AuthKey": "tskey-auth-xxxxx",
  "Hostname": "workhorse-usb",
  "AdvertiseRoutes": ["192.168.1.0/24"],
  "ExitNode": "your-home-pc"
}
```

### Part 3: Auto-Install Script (Runs on Target)

```powershell
# Workhorse USB - Auto-Install Script
# Run as: .\install.ps1

param(
    [string]$TailscaleAuthKey = Get-Content "$PSScriptRoot\..\tailscale\auth-key.txt",
    [string]$HomeTailscaleIP = "100.x.x.x",
    [string]$OpenClawPort = "18789"
)

Write-Host "🧩 Workhorse USB Installer" -ForegroundColor Cyan
Write-Host "Installing required tools..."

# Check for admin
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "⚠️ Please run as Administrator" -ForegroundColor Red
    Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSScriptRoot\$($MyInvocation.MyCommand.Name)`""
    exit
}

# Install Chocolatey
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
}

# Install Node.js
Write-Host "📦 Installing Node.js..."
choco install nodejs-lts -y

# Install Tailscale
Write-Host "📦 Installing Tailscale..."
choco install tailscale -y

# Install Ollama (optional - for local AI)
Write-Host "📦 Installing Ollama..."
choco install ollama -y

# Start Tailscale
Write-Host "🔐 Starting Tailscale..."
Start-Service Tailscale
tailscale login --operator $env:USERNAME
tailscale up --authkey $TailscaleAuthKey --hostname workhorse-usb

# Connect to OpenClaw on home machine
Write-Host "🏠 Connecting to home OpenClaw..."
Write-Host "Access at: http://$HomeTailscaleIP`:$OpenClawPort"

# Start heartbeat
Write-Host "💓 Starting heartbeat..."
& "$PSScriptRoot\heartbeat\heartbeat.ps1"

Write-Host "✅ Installation complete!" -ForegroundColor Green
```

### Part 3: Auto-Start Script

```batch
@echo off
cd %~dp0tailscale
start /wait tailscaled.exe --config=..\configs\tailscale.conf
start msedge http://100.x.x.x:18789
```

---

## 💓 HEARTBEAT SYSTEM

### Purpose

The USB target checks in with Nova periodically to:
- Confirm it's online
- Report status (IP, uptime, services running)
- Receive commands/instructions

### Heartbeat Script (On Target)

```powershell
# heartbeat.ps1
param(
    [string]$NovaEndpoint = "http://100.x.x.x:18789/api/heartbeat",
    [int]$IntervalSeconds = 300  # 5 minutes
)

$hostname = $env:COMPUTERNAME
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"}).IPAddress

while ($true) {
    $payload = @{
        hostname = $hostname
        ip = $ip
        status = "online"
        timestamp = (Get-Date -Format "o")
        services = @{
            tailscale = (Get-Service -Name "Tailscale" -ErrorAction SilentlyContinue).Status
            node = (Get-Command node -ErrorAction SilentlyContinue).Source
            ollama = (Get-Command ollama -ErrorAction SilentlyContinue).Source
        }
    } | ConvertTo-Json
    
    try {
        Invoke-RestMethod -Uri $NovaEndpoint -Method Post -Body $payload -ContentType "application/json" -TimeoutSec 10
        Write-Host "💓 Heartbeat sent: $(Get-Date)"
    } catch {
        Write-Host "⚠️ Heartbeat failed: $_"
    }
    
    Start-Sleep -Seconds $IntervalSeconds
}
```

### On Your Home Machine (Nova)

Add a cron job or endpoint to receive heartbeats:

```
Cron job: Every 5 minutes
- Check for heartbeat from workhorse-usb
- If no heartbeat for 15 min → Alert
- Log status to memory
```

---

## 🔐 SECURITY

### What Stays on Your Home Machine

- All API keys
- All credentials
- All AI models (Ollama)
- OpenClaw gateway

### What's on USB (Safe to Lose)

- Tailscale config (auth key can be rotated)
- Browser
- No API keys

### Firewall Settings

| Port | Service | Allow From |
|------|---------|------------|
| 18789 | OpenClaw | Tailscale network (100.x.x.x) |
| 443 | Tailscale | Outbound only |
| 11434 | Ollama | Tailscale network |

---

## 🔧 CONFIGURATION

### Tailscale Setup

1. Go to https://login.tailscale.com/admin/settings/keys
2. Create reusable auth key (or one-time)
3. Add to USB config
4. Enable "Serve" on your home machine

### Expose OpenClaw to Tailscale

In OpenClaw config, bind to `0.0.0.0` instead of `127.0.0.1`:
```json
{
  "gateway": {
    "host": "0.0.0.0",
    "port": 18789
  }
}
```

---

## 📋 FILES TO COPY FROM YOUR MACHINE

| File | Why |
|------|-----|
| OpenClaw config | Gateway settings |
| Tailscale auth key | Connection |
| Any shortcuts/bookmarks | Quick access |

---

## 🆘 TROUBLESHOOTING

### Can't connect

1. Check Tailscale is running on YOUR machine
2. Verify firewall allows port 18789
3. Check you're on same Tailscale network

### Browser won't load

1. Verify your OpenClaw gateway is running
2. Check Tailscale IP: `tailscale ip -4`
3. Try: `http://YOUR_TAILSCALE_IP:18789`

### Slow performance

- All AI runs over network
- Latency depends on internet speed
- Consider local Ollama for offline

---

## 📞 SUPPORT

- Tailscale docs: https://tailscale.com/kb
- OpenClaw docs: docs.openclaw.ai

---

*Last updated: 2026-02-18*
