# NAS connectivity check
$nasIP = 'MND'
$smbTest = Test-NetConnection -ComputerName $nasIP -Port 445 -WarningAction SilentlyContinue
if (!$smbTest.TcpTestSucceeded) {
    Write-Host "[ERROR] NAS at $nasIP:445 is unreachable. Skipping backup." -ForegroundColor Red
    Write-Host "[INFO] Please check DSM: Control Panel > File Services > SMB > Enable SMB service" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] NAS connectivity verified" -ForegroundColor Green
# Night School NAS Sync v2
# Maps drive with credentials, then syncs

$pass = ConvertTo-SecureString 'Kjn`B]' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('Nova', $pass)
New-PSDrive -Name 'Z' -PSProvider FileSystem -Root '\\MND\home' -Credential $cred | Out-Null

$local = 'C:\Users\compj\.openclaw\workspace\docs\night-school'
$subminds = 'C:\Users\compj\.openclaw\workspace\memory\subminds'
$nas = 'Z:\night-school'

$copied = 0
$skipped = 0
$missingDirs = 0
$copiedFiles = @()

if (-not (Test-Path $nas)) { New-Item -ItemType Directory -Path $nas -Force | Out-Null }

# Sync playbooks
$localFiles = Get-ChildItem $local -Recurse -File | Select-Object FullName, Length, LastWriteTime
foreach ($file in $localFiles) {
    $relative = $file.FullName.Substring($local.Length + 1)
    $nasPath = Join-Path $nas $relative
    $nasDir = Split-Path $nasPath -Parent
    if (-not (Test-Path $nasDir)) { New-Item -ItemType Directory -Path $nasDir -Force | Out-Null; $missingDirs++ }
    if (Test-Path $nasPath) {
        $nasFile = Get-Item $nasPath
        if ($nasFile.Length -eq $file.Length) { $skipped++; continue }
    }
    Copy-Item $file.FullName $nasPath -Force
    $copiedFiles += $relative
    $copied++
}

# Sync subminds
$knowledgeFiles = @('eve-lore-knowledge.md','kybernauts-knowledge.md','anti-yagas-phased-plan.md','anti-yagas-psyops.md')
foreach ($kfile in $knowledgeFiles) {
    $src = Join-Path $subminds $kfile
    if (Test-Path $src) {
        $dest = Join-Path $nas "subminds\$kfile"
        $destDir = Split-Path $dest -Parent
        if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
        $srcInfo = Get-Item $src
        if (Test-Path $dest) {
            $destInfo = Get-Item $dest
            if ($destInfo.Length -eq $srcInfo.Length) { $skipped++; continue }
        }
        Copy-Item $src $dest -Force
        $copiedFiles += "subminds/$kfile"
        $copied++
    }
}

Write-Host ""
Write-Host "=== RESULTS ==="
Write-Host "Copied:   $copied"
Write-Host "Skipped:  $skipped"
Write-Host "New dirs: $missingDirs"
if ($copiedFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "Files copied:"
    foreach ($f in $copiedFiles) { Write-Host "  $f" }
}
