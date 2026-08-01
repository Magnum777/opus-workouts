# NAS connectivity check
$nasIP = 'MND'
$smbTest = Test-NetConnection -ComputerName $nasIP -Port 445 -WarningAction SilentlyContinue
if (!$smbTest.TcpTestSucceeded) {
    Write-Host "[ERROR] NAS at $nasIP:445 is unreachable. Skipping backup." -ForegroundColor Red
    Write-Host "[INFO] Please check DSM: Control Panel > File Services > SMB > Enable SMB service" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] NAS connectivity verified" -ForegroundColor Green
# Workspace NAS Backup Script v2
# Fast backup using robocopy mirror + zip, no staging
# Excludes: node_modules, .git, __pycache__, runtime dirs, temp files

$workspace = "C:\Users\compj\.openclaw\workspace"
$nasPath = "\\MND\home\backups"
$timestamp = Get-Date -Format "yyyy-MM-dd-HHmm"
$zipName = "workspace-backup-$timestamp.zip"
$zipPath = Join-Path $env:TEMP $zipName
$nasDest = Join-Path $nasPath $zipName

Write-Host "=== Workspace NAS Backup ==="
Write-Host "Source: $workspace"
Write-Host "Destination: $nasDest"
Write-Host "Timestamp: $timestamp"
Write-Host ""

# Check if NAS is reachable
if (-not (Test-Path $nasPath)) {
    Write-Host "ERROR: NAS path not accessible: $nasPath"
    Write-Host "Attempting to map..."
    try {
        $cred = New-Object System.Management.Automation.PSCredential("Nova", (ConvertTo-SecureString 'D0ngaYHRuthV93qD' -AsPlainText -Force))
        New-PSDrive -Name "Z" -PSProvider FileSystem -Root "\\MND\home" -Credential $cred -ErrorAction Stop | Out-Null
        $nasPath = "Z:\backups"
        $nasDest = Join-Path $nasPath $zipName
        Write-Host "Mapped NAS to Z: successfully"
    } catch {
        Write-Host "FATAL: Cannot reach NAS. Backup aborted."
        exit 1
    }
}

# Ensure backups dir exists
if (-not (Test-Path $nasPath)) {
    New-Item -ItemType Directory -Path $nasPath -Force | Out-Null
}

# Use 7z if available (much faster), fallback to Compress-Archive
$7zPath = "C:\Program Files\7-Zip\7z.exe"
$use7z = Test-Path $7zPath

# Build exclude arguments
# Workspace is 12+ GB across 120k files - mostly tool installs that can
# be re-downloaded (ComfyUI, agents, msvc). Source code is <1 GB.
# These exclusions are critical for the cron timeout (1800s = 30min).
$excludeArgs = @(
    "-xr!node_modules",
    "-xr!.git",
    "-xr!__pycache__",
    "-xr!.pytest_cache",
    "-xr!*.tmp",
    "-xr!*.log",
    "-xr!output\images",
    "-xr!output\audio",
    "-xr!media\generated",
    "-xr!.openclaw",
    "-xr!*.zip",
    "-xr!*.7z",
    # Heavy tool installs - can be re-downloaded, no need to back up
    "-xr!ComfyUI",
    "-xr!stable-diffusion-webui",
    "-xr!stable-diffusion-webui-backup-a1111",
    "-xr!agents",
    "-xr!6.8.0",
    "-xr!assets-viewer",
    "-xr!workout-tracker",
    # Sub-projects with their own backup strategies
    "-xr!trading-bot\logs",
    "-xr!trading-bot\*.bak",
    "-xr!trading-bot\portfolio_state.json",
    "-xr!trading-bot\price_history.json",
    "-xr!trading-bot\trading-queue.json",
    # Inbound staged files from other agents - ephemeral
    "-xr!media\inbound",
    # Skill install rollback snapshots
    "-xr!skills\.openclaw-install-backups",
    # Throwaway temp dirs from prior sessions
    "-xr!temp",
    "-xr!scripts\temp_torrents",
    "-xr!scripts\.cache",
    "-xr!scripts\content-nova\temp_images",
    # Runtime queue data (can rebuild from logs)
    "-xr!memory\prompt-pack-social-drafts",
    "-xr!memory\prompt-pack-aibusinessinsider-queue"
)

if ($use7z) {
    Write-Host "Using 7-Zip for fast compression..." -NoNewline
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $7zArgs = @("a", "-tzip", "-r", "-mx=1", "-bb3") + $excludeArgs + @($zipPath, "$workspace\*")
    & $7zPath @7zArgs
    $sw.Stop()
    Write-Host " done in $([math]::Round($sw.Elapsed.TotalSeconds,1))s"
} else {
    Write-Host "Using Compress-Archive (slower)..."
    # Get files excluding patterns - mirror the 7-Zip exclude list
    $files = Get-ChildItem $workspace -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
        $p = $_.FullName
        -not ($p -like "*node_modules*" -or $p -like "*.git*" -or $p -like "*__pycache__*" -or
              $p -like "*.pytest_cache*" -or $p -like "*.tmp" -or $p -like "*.log" -or
              $p -like "*output\images*" -or $p -like "*output\audio*" -or
              $p -like "*media\generated*" -or $p -like "*.openclaw*" -or
              $p -like "*.zip" -or $p -like "*.7z" -or
              $p -like "*\ComfyUI\*" -or $p -like "*\agents\*" -or
              $p -like "*\6.8.0\*" -or $p -like "*\assets-viewer\*" -or
              $p -like "*\workout-tracker\*" -or $p -like "*\media\inbound\*" -or
              $p -like "*\.openclaw-install-backups\*" -or $p -like "*\temp\*" -or
              $p -like "*\scripts\temp_torrents\*" -or $p -like "*\scripts\.cache\*" -or
              $p -like "*\content-nova\temp_images\*" -or
              $p -like "*\prompt-pack-social-drafts\*" -or
              $p -like "*\prompt-pack-aibusinessinsider-queue\*")
    }
    Write-Host "  compressing $($files.Count) files..." -NoNewline
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    Compress-Archive -Path $files.FullName -DestinationPath $zipPath -CompressionLevel Fastest
    $sw.Stop()
    Write-Host " done in $([math]::Round($sw.Elapsed.TotalSeconds,1))s"
}

if (-not (Test-Path $zipPath)) {
    Write-Host "ERROR: Zip creation failed"
    exit 1
}

$zipSize = (Get-Item $zipPath).Length
$zipSizeMB = [math]::Round($zipSize / 1MB, 2)
Write-Host "Zip created: $zipSizeMB MB"

# Copy to NAS
Write-Host "Copying to NAS..." -NoNewline
$sw = [System.Diagnostics.Stopwatch]::StartNew()
Copy-Item $zipPath $nasDest -Force
$sw.Stop()
Write-Host " done in $([math]::Round($sw.Elapsed.TotalSeconds,1))s"

# Verify
if (Test-Path $nasDest) {
    $nasSize = (Get-Item $nasDest).Length
    if ($nasSize -eq $zipSize) {
        Write-Host "NAS copy verified."
    } else {
        Write-Host "WARNING: Size mismatch! Local: $zipSize, NAS: $nasSize"
    }
} else {
    Write-Host "ERROR: NAS copy failed"
    exit 1
}

# Cleanup local temp
Remove-Item $zipPath -Force

Write-Host ""
Write-Host "=== Backup Complete ==="
Write-Host "File: $zipName"
Write-Host "Size: $zipSizeMB MB"
Write-Host "Location: $nasDest"

# Retention: keep last 14 backups
Write-Host ""
Write-Host "Checking retention (keeping last 14)..."
$existing = Get-ChildItem $nasPath -Filter "workspace-backup-*.zip" | Sort-Object LastWriteTime -Descending
if ($existing.Count -gt 14) {
    $toDelete = $existing | Select-Object -Skip 14
    foreach ($old in $toDelete) {
        Write-Host "  Removing old: $($old.Name)"
        Remove-Item $old.FullName -Force
    }
}
Write-Host "Done. $($existing.Count) total backups on NAS."
