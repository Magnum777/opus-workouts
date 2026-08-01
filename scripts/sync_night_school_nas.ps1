# Night School NAS Sync Script
# Copies all files from local docs/night-school/ + subminds/ to NAS
# Uses UNC path (no W: drive dependency)
# Skips unchanged files, reports what was copied

$local = "C:\Users\compj\.openclaw\workspace\docs\night-school"
$subminds = "C:\Users\compj\.openclaw\workspace\memory\subminds"
$nas = "\\MND\home\night-school"

$copied = 0
$skipped = 0
$missingDirs = 0
$authFailed = $false

# Authenticate to NAS first
$nasUser = "Nova"
$nasPass = "D0ngaYHRuthV93qD"
try {
    $driveLetter = "N:"
    # Remove existing mapping if any
    if (Test-Path $driveLetter) {
        net use $driveLetter /delete 2>$null
    }
    # Create new mapped drive with credentials
    $result = net use $driveLetter "\\MND\home" $nasPass /user:$nasUser /persistent:no 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to authenticate to NAS. $result" -ForegroundColor Red
        $authFailed = $true
    } else {
        Write-Host "Authenticated to NAS via $driveLetter" -ForegroundColor Green
    }
} catch {
    Write-Host "ERROR: Failed to connect to NAS: $_" -ForegroundColor Red
    $authFailed = $true
}

if ($authFailed) {
    Write-Host ""
    Write-Host "Done. Copied 0 files, skipped 0 unchanged, created 0 directories. AUTH FAILED."
    exit 1
}

# Use mapped drive for NAS path
$nas = "N:\night-school"

# Sync playbooks from docs/night-school/
$localFiles = Get-ChildItem $local -Recurse -File | Select-Object FullName, Length, LastWriteTime

foreach ($file in $localFiles) {
    $relative = $file.FullName.Substring($local.Length + 1)
    $nasPath = Join-Path $nas $relative
    $nasDir = Split-Path $nasPath -Parent

    if (-not (Test-Path $nasDir)) {
        New-Item -ItemType Directory -Path $nasDir -Force | Out-Null
        $missingDirs++
    }

    if (Test-Path $nasPath) {
        $nasFile = Get-Item $nasPath
        if ($nasFile.Length -eq $file.Length) {
            $skipped++
            continue
        }
    }

    Copy-Item $file.FullName $nasPath -Force
    Write-Host "  Copied: $relative ($($file.Length) bytes)"
    $copied++
}

# Sync subminds/knowledge files to NAS subminds/ folder
$knowledgeFiles = @("eve-lore-knowledge.md", "kybernauts-knowledge.md", "anti-yagas-phased-plan.md", "anti-yagas-psyops.md")
foreach ($kfile in $knowledgeFiles) {
    $src = Join-Path $subminds $kfile
    if (Test-Path $src) {
        $dest = Join-Path $nas "subminds\$kfile"
        $destDir = Split-Path $dest -Parent
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        $srcInfo = Get-Item $src
        if (Test-Path $dest) {
            $destInfo = Get-Item $dest
            if ($destInfo.Length -eq $srcInfo.Length) {
                $skipped++
                continue
            }
        }
        Copy-Item $src $dest -Force
        Write-Host "  Copied: subminds/$kfile ($($srcInfo.Length) bytes)"
        $copied++
    }
}

Write-Host ""
Write-Host "Done. Copied $copied files, skipped $skipped unchanged, created $missingDirs directories."

# Cleanup mapped drive
net use N: /delete 2>$null