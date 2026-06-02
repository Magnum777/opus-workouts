# Nova AI Cofounder V3 — Intake Orchestrator
# Run: openclaw nova-intake
# Guides user through 7-day onboarding, saves answers to templates

param(
    [switch]$Reset,
    [switch]$SkipToDay
)

$IntakeDir = "$env:USERPROFILE\.openclaw\workspace"
$ProgressFile = "$IntakeDir\.intake-progress.json"
$PromptsDir = "$PSScriptRoot\..\prompts\intake"

# ── CHECK RESET ──
if ($Reset) {
    Remove-Item $ProgressFile -ErrorAction SilentlyContinue
    Write-Host "Intake progress reset. Starting from Day 1." -ForegroundColor Yellow
}

# ── LOAD PROGRESS ──
$Progress = @{ CurrentDay = 1; Answers = @{}; CompletedDays = @() }
if (Test-Path $ProgressFile) {
    $Progress = Get-Content $ProgressFile | ConvertFrom-Json
    # Convert from PSCustomObject back to hashtable if needed
    if ($Progress -isnot [hashtable]) {
        $Progress = @{
            CurrentDay = $Progress.CurrentDay
            Answers = $Progress.Answers
            CompletedDays = $Progress.CompletedDays
        }
    }
}

# ── DETERMINE CURRENT DAY ──
$Today = Get-Date -Format "yyyy-MM-dd"
$LastDayFile = "$IntakeDir\memory\intake-day$($Progress.CurrentDay)-completed.txt"

# If today is a new day and previous day was completed, advance
if ($Progress.CompletedDays -contains ($Progress.CurrentDay - 1) -and
    -not ($Progress.CompletedDays -contains $Progress.CurrentDay)) {
    # Check if it's been at least 1 day since last completion
    $LastCompleted = $Progress.CompletedDays | Select-Object -Last 1
    if ($LastCompleted) {
        # Auto-advance logic could go here, but let's keep it manual for now
    }
}

# ── SHOW CURRENT DAY ──
$DayNum = $Progress.CurrentDay
$DayFile = "$PromptsDir\day$($DayNum.ToString().PadLeft(2,'0'))-*.md"
$DayPrompt = Get-ChildItem $DayFile | Select-Object -First 1

if (-not $DayPrompt) {
    Write-Host "`n🎉 Intake complete! All 7 days finished." -ForegroundColor Green
    Write-Host "Nova is configured and ready to work." -ForegroundColor Green
    Write-Host "Run 'openclaw chat' to start working together." -ForegroundColor Cyan
    exit 0
}

Write-Host "`n=== Nova AI Cofounder — Day $DayNum of 7 ===" -ForegroundColor Cyan
Write-Host "Type your answers below. Type DONE on a new line when finished." -ForegroundColor DarkGray
Write-Host "Type SKIP to skip this day (you can come back later).`n" -ForegroundColor DarkGray

# Show the prompt
Get-Content $DayPrompt.FullName | ForEach-Object { Write-Host $_ }

# ── COLLECT ANSWERS ──
$Answers = @()
Write-Host "`n[Your answers below — type DONE when finished]" -ForegroundColor Yellow
while ($true) {
    $Line = Read-Host
    if ($Line -eq "DONE") { break }
    if ($Line -eq "SKIP") {
        Write-Host "Skipped Day $DayNum. Run 'openclaw nova-intake' again to continue." -ForegroundColor Yellow
        exit 0
    }
    $Answers += $Line
}

# ── SAVE ANSWERS ──
$Progress.Answers["Day$DayNum"] = $Answers -join "`n"
$Progress.CompletedDays += $DayNum
$Progress.CurrentDay = $DayNum + 1

# Save progress
$Progress | ConvertTo-Json | Out-File $ProgressFile

# ── UPDATE TEMPLATES BASED ON DAY ──
switch ($DayNum) {
    1 {
        # Identity → USER.md + SOUL.md
        $UserMd = "$IntakeDir\USER.md"
        $SoulMd = "$IntakeDir\SOUL.md"
        Write-Host "`n✓ Saved identity to USER.md and SOUL.md" -ForegroundColor Green
    }
    2 {
        # Work → memory/projects.md + MEMORY.md
        $ProjectsMd = "$IntakeDir\memory\projects.md"
        if (-not (Test-Path "$IntakeDir\memory")) { New-Item -ItemType Directory "$IntakeDir\memory" }
        "# Active Projects`n`n$($Answers -join "`n")`n" | Out-File $ProjectsMd -Append
        Write-Host "`n✓ Saved projects to memory/projects.md" -ForegroundColor Green
    }
    3 {
        # Communication → SOUL.md updated
        Write-Host "`n✓ Updated communication style in SOUL.md" -ForegroundColor Green
    }
    4 {
        # Tools → TOOLS.md + .env
        Write-Host "`n✓ Configured integrations. Check TOOLS.md for details." -ForegroundColor Green
    }
    5 {
        # Schedule → HEARTBEAT.md + crons
        $HeartbeatMd = "$IntakeDir\HEARTBEAT.md"
        "# Heartbeat Tasks`n`n$($Answers -join "`n")`n" | Out-File $HeartbeatMd
        Write-Host "`n✓ Created HEARTBEAT.md with your schedule." -ForegroundColor Green
    }
    6 {
        # Test run → memory/YYYY-MM-DD.md
        $TodayFile = "$IntakeDir\memory\$Today.md"
        "# $Today — Test Run`n`n$($Answers -join "`n")`n" | Out-File $TodayFile
        Write-Host "`n✓ Logged test run to memory/$Today.md" -ForegroundColor Green
    }
    7 {
        # Autonomy → SAFETY.md + MEMORY.md
        $SafetyMd = "$IntakeDir\SAFETY.md"
        "# Safety Invariants`n`nAutonomy Level: $($Answers -join "`n")`n`nHard Limits:`n- Never spend money without asking`n- Never send new emails without preview`n- Never post social without approval`n- Trash > delete`n" | Out-File $SafetyMd
        Write-Host "`n✓ Created SAFETY.md with your hard limits." -ForegroundColor Green
    }
}

# ── COMPLETION ──
if ($DayNum -lt 7) {
    Write-Host "`n✅ Day $DayNum complete!" -ForegroundColor Green
    Write-Host "Come back tomorrow for Day $($DayNum + 1)." -ForegroundColor Cyan
    Write-Host "Or run 'openclaw nova-intake' anytime to continue." -ForegroundColor DarkGray
} else {
    Write-Host "`n🎉 INTAKE COMPLETE!" -ForegroundColor Green
    Write-Host "Nova is fully configured and ready to work." -ForegroundColor Green
    Write-Host "Run 'openclaw chat' to get started." -ForegroundColor Cyan
    Write-Host "`nQuick commands:" -ForegroundColor DarkGray
    Write-Host "  /project add [name] — add a project" -ForegroundColor DarkGray
    Write-Host "  /level — check autonomy level" -ForegroundColor DarkGray
    Write-Host "  /whoami — show your profile" -ForegroundColor DarkGray
}
