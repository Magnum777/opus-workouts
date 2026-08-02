$ts = Get-Date -Format 'yyyy-MM-dd_HH-mm'
$nas = '\\MND\Nova-Backups'
$dest = Join-Path $nas "openclaw-backup-$ts"
Write-Host "Destination: $dest"

# Test NAS connectivity
if (!(Test-Path $nas)) {
    Write-Host "[WARN] NAS not reachable at $nas, trying D:\Nova-Backups"
    $nas = 'D:\Nova-Backups'
    $dest = Join-Path $nas "openclaw-backup-$ts"
}
New-Item -ItemType Directory -Force -Path $dest | Out-Null

# Copy workspace
$ws = 'C:\Users\compj\.openclaw\workspace'
$wsDest = Join-Path $dest 'workspace'
Write-Host "Backing up workspace..."
Copy-Item -Path $ws -Destination $wsDest -Recurse -Force -ErrorAction SilentlyContinue

# Copy gateway
$gw = 'C:\Users\compj\.openclaw\gateway'
$gwDest = Join-Path $dest 'gateway'
if (Test-Path $gw) {
    Write-Host "Backing up gateway..."
    Copy-Item -Path $gw -Destination $gwDest -Recurse -Force -ErrorAction SilentlyContinue
}

# Copy skills
$sk = 'C:\Users\compj\.openclaw\skills'
$skDest = Join-Path $dest 'skills'
if (Test-Path $sk) {
    Write-Host "Backing up skills..."
    Copy-Item -Path $sk -Destination $skDest -Recurse -Force -ErrorAction SilentlyContinue
}

# Copy agents
$ag = 'C:\Users\compj\.openclaw\agents'
$agDest = Join-Path $dest 'agents'
if (Test-Path $ag) {
    Write-Host "Backing up agents..."
    Copy-Item -Path $ag -Destination $agDest -Recurse -Force -ErrorAction SilentlyContinue
}

# Verify
$files = (Get-ChildItem -Path $dest -Recurse -File -ErrorAction SilentlyContinue).Count
Write-Host "Backup complete. $files files copied to: $dest"
