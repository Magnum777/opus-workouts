# NAS connectivity check
$nasIP = 'MND'
$smbTest = Test-NetConnection -ComputerName $nasIP -Port 445 -WarningAction SilentlyContinue
if (!$smbTest.TcpTestSucceeded) {
    Write-Host "[ERROR] NAS at $nasIP:445 is unreachable. Skipping backup." -ForegroundColor Red
    Write-Host "[INFO] Please check DSM: Control Panel > File Services > SMB > Enable SMB service" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] NAS connectivity verified" -ForegroundColor Green
$ts = Get-Date -Format 'yyyy-MM-dd_HH-mm'
$dest = "\\MND\Nova-Backups\openclaw-backup-$ts"

# Map NAS share persistently
$pass = ConvertTo-SecureString 'Kjn`B]' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('Nova', $pass)
$映射 = New-PSDrive -Name 'N' -PSProvider FileSystem -Root '\\MND\Nova-Backups' -Credential $cred -ErrorAction SilentlyContinue
if (!$映射) {
    Write-Host "[WARN] Could not map N: drive"
} else {
    Write-Host "Mapped N: drive OK"
}

# Ensure destination dir exists
$destN = "N:\openclaw-backup-$ts"
New-Item -ItemType Directory -Force -Path $destN | Out-Null

# Copy workspace
Write-Host "Backing up workspace..."
Copy-Item -Path 'C:\Users\compj\.openclaw\workspace' -Destination "$destN\workspace" -Recurse -Force -ErrorAction SilentlyContinue

# Copy gateway
if (Test-Path 'C:\Users\compj\.openclaw\gateway') {
    Write-Host "Backing up gateway..."
    Copy-Item -Path 'C:\Users\compj\.openclaw\gateway' -Destination "$destN\gateway" -Recurse -Force -ErrorAction SilentlyContinue
}

# Copy skills
if (Test-Path 'C:\Users\compj\.openclaw\skills') {
    Write-Host "Backing up skills..."
    Copy-Item -Path 'C:\Users\compj\.openclaw\skills' -Destination "$destN\skills" -Recurse -Force -ErrorAction SilentlyContinue
}

# Copy agents
if (Test-Path 'C:\Users\compj\.openclaw\agents') {
    Write-Host "Backing up agents..."
    Copy-Item -Path 'C:\Users\compj\.openclaw\agents' -Destination "$destN\agents" -Recurse -Force -ErrorAction SilentlyContinue
}

$files = (Get-ChildItem -Path $destN -Recurse -File -ErrorAction SilentlyContinue).Count
Write-Host "Backup complete. $files files copied."
Write-Host "Location: \\MND\Nova-Backups\openclaw-backup-$ts"
Remove-PSDrive -Name 'N' -ErrorAction SilentlyContinue
