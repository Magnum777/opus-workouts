# Nova AI Cofounder V3 — Setup Script
# Run as Administrator (recommended but not required)
# This script installs OpenClaw Gateway, core skills, templates, and launches intake

param(
    [switch]$Docker,
    [switch]$SkipIntake,
    [string]$Model = "ollama"  # or "api" for cloud model
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$NovaVersion = "3.0.0"
$InstallDir = "$env:USERPROFILE\.openclaw"
$WorkspaceDir = "$InstallDir\workspace"
$TempDir = "$env:TEMP\nova-setup"

# ── COLORS ──
function Write-Header($text) { Write-Host "`n=== $text ===" -ForegroundColor Cyan }
function Write-Ok($text) { Write-Host "  ✓ $text" -ForegroundColor Green }
function Write-Warn($text) { Write-Host "  ⚠ $text" -ForegroundColor Yellow }
function Write-Error($text) { Write-Host "  ✗ $text" -ForegroundColor Red }

# ── PREREQ CHECK ──
Write-Header "Checking Prerequisites"

# Python
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Warn "Python not found. Installing via winget..."
    winget install Python.Python.3.11 -e --source winget --accept-package-agreements --accept-source-agreements
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) { Write-Error "Python install failed. Install manually from python.org"; exit 1 }
}
Write-Ok "Python: $($py.Source)"

# Git
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Warn "Git not found. Installing via winget..."
    winget install Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}
Write-Ok "Git: available"

# Node.js (for Gateway)
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Warn "Node.js not found. Installing via winget..."
    winget install OpenJS.NodeJS -e --source winget --accept-package-agreements --accept-source-agreements
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}
Write-Ok "Node.js: available"

# Ollama (for local model)
if ($Model -eq "ollama") {
    $ollama = Get-Command ollama -ErrorAction SilentlyContinue
    if (-not $ollama) {
        Write-Warn "Ollama not found. Installing..."
        Invoke-WebRequest -Uri "https://ollama.com/download/OllamaSetup.exe" -OutFile "$env:TEMP\OllamaSetup.exe"
        Start-Process "$env:TEMP\OllamaSetup.exe" -Wait
        Write-Ok "Ollama installed. Pulling default model (kimi-k2.6)..."
        ollama pull kimi-k2.6:cloud
    } else {
        Write-Ok "Ollama: available"
    }
}

# ── INSTALL OPENCLAW GATEWAY ──
Write-Header "Installing OpenClaw Gateway"

if (Test-Path "$InstallDir\gateway") {
    Write-Warn "Gateway already exists. Updating..."
    cd "$InstallDir\gateway"
    git pull
} else {
    Write-Ok "Downloading OpenClaw Gateway..."
    git clone https://github.com/openclaw/openclaw.git "$InstallDir\gateway"
    cd "$InstallDir\gateway"
    npm install
    npm run build
}
Write-Ok "Gateway installed at $InstallDir\gateway"

# ── CREATE WORKSPACE ──
Write-Header "Setting Up Workspace"

if (-not (Test-Path $WorkspaceDir)) {
    New-Item -ItemType Directory -Path $WorkspaceDir -Force | Out-Null
}

# Copy templates
$TemplateSource = "$PSScriptRoot\..\config\templates"
$templates = @("SOUL.md", "AGENTS.md", "USER.md", "TOOLS.md", "MEMORY.md")
foreach ($t in $templates) {
    $src = "$TemplateSource\$t"
    $dst = "$WorkspaceDir\$t"
    if (Test-Path $src) {
        if (-not (Test-Path $dst)) {
            Copy-Item $src $dst
            Write-Ok "Copied template: $t"
        } else {
            Write-Warn "$t already exists, skipping"
        }
    }
}

# Create directory structure
$dirs = @("memory", "scripts", "skills", "output", "media", "ops")
foreach ($d in $dirs) {
    $path = "$WorkspaceDir\$d"
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}
Write-Ok "Workspace structure created"

# ── INSTALL CORE SKILLS ──
Write-Header "Installing Core Skills"

$CoreSkills = @(
    "clawhub",
    "browser-automation",
    "memory-hygiene",
    "self-improving-agent",
    "duckdb-en",
    "taskflow"
)

foreach ($skill in $CoreSkills) {
    try {
        openclaw clawhub install $skill
        Write-Ok "Installed skill: $skill"
    } catch {
        Write-Warn "Failed to install $skill (will try again later)"
    }
}

# ── OPTIONAL SKILLS ──
Write-Header "Optional Skills"
Write-Host "These skills add specific capabilities. Install now or add later." -ForegroundColor DarkGray

$OptionalSkills = @(
    @{ Name="gmail-cleanup"; Desc="Gmail spam sweep + inbox triage" },
    @{ Name="wordpress-pro"; Desc="WordPress publishing automation" },
    @{ Name="ai-social-media-content"; Desc="Generate social media posts" },
    @{ Name="upload-post"; Desc="Post to TikTok, IG, X, etc." }
)

foreach ($skill in $OptionalSkills) {
    $response = Read-Host "Install $($skill.Name) ($($skill.Desc))? [y/N]"
    if ($response -eq "y" -or $response -eq "Y") {
        try {
            openclaw clawhub install $skill.Name
            Write-Ok "Installed: $($skill.Name)"
        } catch {
            Write-Warn "Failed: $($skill.Name)"
        }
    }
}

# ── DOCKER SETUP (if requested) ──
if ($Docker) {
    Write-Header "Docker Setup"
    $docker = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $docker) {
        Write-Warn "Docker not found. Install Docker Desktop first: https://docker.com/products/docker-desktop"
        Write-Warn "Then re-run with -Docker flag"
    } else {
        Write-Ok "Docker available"
        Copy-Item "$PSScriptRoot\..\setup\docker-compose.yml" "$WorkspaceDir\docker-compose.yml" -Force
        Write-Ok "Docker compose file copied. Run 'docker-compose up' to start isolated services."
    }
}

# ── GATEWAY CONFIG ──
Write-Header "Gateway Configuration"

$ConfigPath = "$InstallDir\gateway\config.yaml"
if (-not (Test-Path $ConfigPath)) {
    Write-Warn "Gateway config not found. Running init..."
    openclaw gateway init
}

# ── API MODEL SETUP (if requested) ──
if ($Model -eq "api") {
    Write-Header "API Model Configuration"
    Write-Host "You chose API model. You'll need to add your API keys." -ForegroundColor Cyan
    Write-Host "Supported providers: OpenAI, Anthropic, Google, Ollama Cloud" -ForegroundColor DarkGray
    $apiKey = Read-Host "Enter your API key (or press Enter to skip and configure later)"
    if ($apiKey) {
        $EnvPath = "$WorkspaceDir\.env"
        "API_KEY=$apiKey" | Out-File $EnvPath -Append
        Write-Ok "API key saved to .env"
    }
}

# ── CHANNEL SETUP ──
Write-Header "Channel Configuration"
Write-Host "How do you want to talk to Nova?" -ForegroundColor Cyan

$discord = Read-Host "Discord bot token (or press Enter to skip)"
if ($discord) {
    $EnvPath = "$WorkspaceDir\.env"
    if (-not (Test-Path $EnvPath)) { New-Item $EnvPath | Out-Null }
    "DISCORD_BOT_TOKEN=$discord" | Out-File $EnvPath -Append
    Write-Ok "Discord token saved"
    Write-Host "  → Invite bot: https://discord.com/developers/applications" -ForegroundColor DarkGray
}

$telegram = Read-Host "Telegram bot token (or press Enter to skip)"
if ($telegram) {
    $EnvPath = "$WorkspaceDir\.env"
    "TELEGRAM_BOT_TOKEN=$telegram" | Out-File $EnvPath -Append
    Write-Ok "Telegram token saved"
}

# ── FINALIZE ──
Write-Header "Setup Complete!"

Write-Host "`nNova AI Cofounder V$NovaVersion is installed." -ForegroundColor Green
Write-Host "Workspace: $WorkspaceDir" -ForegroundColor DarkGray
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Run: openclaw nova-intake" -ForegroundColor White
Write-Host "     (Starts 7-day onboarding sequence)" -ForegroundColor DarkGray
Write-Host "  2. Or start manually: openclaw chat" -ForegroundColor White
Write-Host "`nDocumentation:" -ForegroundColor Cyan
Write-Host "  - Setup guide: $PSScriptRoot\..\docs\PDF\setup-guide.pdf" -ForegroundColor White
Write-Host "  - Prompt reference: $PSScriptRoot\..\docs\PDF\prompt-reference.pdf" -ForegroundColor White
Write-Host "  - Discord: https://discord.gg/clawd" -ForegroundColor White
Write-Host "`nNeed help? Post in #nova-help on Discord." -ForegroundColor DarkGray

# Launch intake unless skipped
if (-not $SkipIntake) {
    Write-Host "`nLaunching intake in 3 seconds... (Ctrl+C to skip)" -ForegroundColor Yellow
    Start-Sleep 3
    openclaw nova-intake
}
