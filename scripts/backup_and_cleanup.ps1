# Full workspace backup to NAS with 2-week retention
# NAS IP updated to MND

$nasIP = 'MND'
$smbTest = Test-NetConnection -ComputerName $nasIP -Port 445 -WarningAction SilentlyContinue
if (!$smbTest.TcpTestSucceeded) {
    Write-Host "[ERROR] NAS at $nasIP:445 is unreachable. Aborting." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] NAS at $nasIP is reachable" -ForegroundColor Green

$workspace = "C:\Users\compj\.openclaw\workspace"
$timestamp = Get-Date -Format "yyyy-MM-dd-HHmm"
$zipName = "workspace-backup-$timestamp.zip"
$nasPath = "\\$nasIP\home\backups"

# Ensure NAS path is accessible
if (-not (Test-Path $nasPath)) {
    Write-Host "Mapping NAS drive..."
    try {
        $cred = New-Object System.Management.Automation.PSCredential("Nova", (ConvertTo-SecureString 'D0ngaYHRuthV93qD' -AsPlainText -Force))
        New-PSDrive -Name "Z" -PSProvider FileSystem -Root "\\$nasIP\home" -Credential $cred -ErrorAction Stop | Out-Null
        $nasPath = "Z:\backups"
        if (-not (Test-Path $nasPath)) {
            New-Item -ItemType Directory -Path $nasPath -Force | Out-Null
        }
        Write-Host "Mapped NAS to Z:"
    } catch {
        Write-Host "[FATAL] Cannot reach NAS: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Ensure backups dir
if (-not (Test-Path $nasPath)) {
    New-Item -ItemType Directory -Path $nasPath -Force | Out-Null
}

# Use 7-Zip for fast compression
$7zPath = "C:\Program Files\7-Zip\7z.exe"
$zipPath = Join-Path $env:TEMP $zipName

Write-Host "=== Workspace NAS Backup ==="
Write-Host "Source: $workspace"
Write-Host "Dest: $nasPath\$zipName"
Write-Host "Timestamp: $timestamp"
Write-Host ""

if (Test-Path $7zPath) {
    Write-Host "Compressing with 7-Zip (fast)..."
    $7zArgs = @("a", "-tzip", "-r", "-mx=1",
        "-xr!node_modules", "-xr!.git", "-xr!__pycache__", "-xr!.pytest_cache",
        "-xr!*.tmp", "-xr!*.log", "-xr!output\images", "-xr!output\audio",
        "-xr!media\generated", "-xr!.openclaw", "-xr!*.zip", "-xr!*.7z",
        $zipPath, "$workspace\*")
    & $7zPath @7zArgs
} else {
    Write-Host "Compressing with PowerShell (slower)..."
    Compress-Archive -Path "$workspace\*" -DestinationPath $zipPath -CompressionLevel Fastest -Force
}

if (-not (Test-Path $zipPath)) {
    Write-Host "[ERROR] Zip creation failed" -ForegroundColor Red
    exit 1
}

$zipSize = (Get-Item $zipPath).Length
$zipSizeMB = [math]::Round($zipSize / 1MB, 1)
Write-Host "Zip created: $zipSizeMB MB"

# Copy to NAS
$nasDest = Join-Path $nasPath $zipName
Write-Host "Copying to NAS..."
Copy-Item $zipPath $nasDest -Force

# Verify
if (Test-Path $nasDest) {
    $nasSize = (Get-Item $nasDest).Length
    if ($nasSize -eq $zipSize) {
        Write-Host "[OK] NAS copy verified ($zipSizeMB MB)" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Size mismatch! Local: $zipSize, NAS: $nasSize" -ForegroundColor Yellow
    }
} else {
    Write-Host "[ERROR] NAS copy failed" -ForegroundColor Red
    exit 1
}

# Cleanup local temp
Remove-Item $zipPath -Force -ErrorAction SilentlyContinue

# Retention: keep last 14 days of backups (2 weeks)
Write-Host ""
Write-Host "=== Retention Cleanup (keep last 14 days) ==="
$cutoff = (Get-Date).AddDays(-14)
$existing = Get-ChildItem $nasPath -Filter "workspace-backup-*.zip" -ErrorAction SilentlyContinue
$removed = 0
$kept = 0
foreach ($f in $existing) {
    if ($f.LastWriteTime -lt $cutoff) {
        Write-Host "  REMOVING: $($f.Name) ($([math]::Round($f.Length/1MB,1)) MB, $($f.LastWriteTime.ToString('yyyy-MM-dd')))"
        Remove-Item $f.FullName -Force -ErrorAction SilentlyContinue
        $removed++
    } else {
        $kept++
    }
}
Write-Host "Kept: $kept backups, Removed: $removed old backups"

Write-Host ""
Write-Host "=== Backup Complete ==="
Write-Host "File: $zipName"
Write-Host "Size: $zipSizeMB MB"
Write-Host "Location: $nasDest"

# Clean up Z: drive if mapped
if (Get-PSDrive -Name "Z" -ErrorAction SilentlyContinue) {
    Remove-PSDrive -Name "Z" -Force
}