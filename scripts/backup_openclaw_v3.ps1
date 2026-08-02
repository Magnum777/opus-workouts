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
$destRoot = "\\MND\Nova-Backups"
$dest = "$destRoot\openclaw-backup-$ts"

$pass = ConvertTo-SecureString 'Kjn`B]' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('Nova', $pass)
$drive = New-PSDrive -Name 'N' -PSProvider FileSystem -Root $destRoot -Credential $cred -ErrorAction SilentlyContinue
if (!$drive) {
    Write-Host "[WARN] Could not map N: drive"
    $dest = "C:\Nova-Backups\openclaw-backup-$ts"
} else {
    Write-Host "Mapped N: drive OK"
}

New-Item -ItemType Directory -Force -Path $dest | Out-Null

Write-Host "Backing up workspace..."
Copy-Item -Path 'C:\Users\compj\.openclaw\workspace' -Destination "$dest\workspace" -Recurse -Force -ErrorAction SilentlyContinue

if (Test-Path 'C:\Users\compj\.openclaw\gateway') {
    Write-Host "Backing up gateway..."
    Copy-Item -Path 'C:\Users\compj\.openclaw\gateway' -Destination "$dest\gateway" -Recurse -Force -ErrorAction SilentlyContinue
}

if (Test-Path 'C:\Users\compj\.openclaw\skills') {
    Write-Host "Backing up skills..."
    Copy-Item -Path 'C:\Users\compj\.openclaw\skills' -Destination "$dest\skills" -Recurse -Force -ErrorAction SilentlyContinue
}

if (Test-Path 'C:\Users\compj\.openclaw\agents') {
    Write-Host "Backing up agents..."
    Copy-Item -Path 'C:\Users\compj\.openclaw\agents' -Destination "$dest\agents" -Recurse -Force -ErrorAction SilentlyContinue
}

$files = (Get-ChildItem -Path $dest -Recurse -File -ErrorAction SilentlyContinue).Count
Write-Host "Backup complete. $files files copied."
Write-Host "Location: $dest"
if ($drive) { Remove-PSDrive -Name 'N' -ErrorAction SilentlyContinue }
