# Night School NAS Sync Script
# Copies all files from local docs/night-school/ + subminds/ to NAS W:\night-school\
# Skips unchanged files, reports what was copied

$local = "C:\Users\compj\.openclaw\workspace\docs\night-school"
$subminds = "C:\Users\compj\.openclaw\workspace\memory\subminds"
$nas = "W:\night-school"

$copied = 0
$skipped = 0
$missingDirs = 0

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
