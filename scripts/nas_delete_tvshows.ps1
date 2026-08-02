# Delete all TV shows from NAS video share
# TV shows identified from audit: multi-episode folders with S##E## patterns
$cred = New-Object System.Management.Automation.PSCredential("Nova", (ConvertTo-SecureString 'D0ngaYHRuthV93qD' -AsPlainText -Force))
New-PSDrive -Name "V" -PSProvider FileSystem -Root "\\MND\video" -Credential $cred -ErrorAction Stop | Out-Null

# Get all top-level folders
$dirs = Get-ChildItem "V:\" -Directory -ErrorAction SilentlyContinue

# Identify TV shows - folders containing episode patterns or known show names
$tvPatterns = @(
    'S\d{1,2}E\d{1,2}', 'S\d{1,2}\.', '\d{1,2}x\d{1,2}',
    'Season\s*\d', 'Series\s*\d', 'Episode',
    # Known show name patterns
    'Greys\.Anatomy', 'The\.Rookie', 'Tulsa\.King', 'Ahsoka',
    'SEAL\.Team', 'American\.Dad', 'Bad\.Batch', 'Star\.Wars.*Bad',
    'Handmaids\.Tale', 'Homeland', 'Doctor\.Who', 'Westworld',
    'Stargirl', 'Last\.Week\.Tonight', '60\.Minutes',
    'The\.Office', 'Hillsong', 'Prison\.Confessions',
    'Mandalorian', 'Halo'
)

$tvDirs = @()
$movieDirs = @()

foreach ($d in $dirs) {
    $name = $d.Name
    $isTV = $false
    
    # Check if folder name matches TV patterns
    foreach ($pattern in $tvPatterns) {
        if ($name -match $pattern) {
            $isTV = $true
            break
        }
    }
    
    # Also check if folder contains episode-style files inside
    if (-not $isTV) {
        $files = Get-ChildItem $d.FullName -File -ErrorAction SilentlyContinue | Select-Object -First 20
        foreach ($f in $files) {
            if ($f.Name -match 'S\d{1,2}E\d{1,2}' -or $f.Name -match '\d{1,2}x\d{1,2}') {
                $isTV = $true
                break
            }
        }
    }
    
    if ($isTV) {
        $size = (Get-ChildItem $d.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $sizeGB = [math]::Round($size/1GB, 2)
        $tvDirs += [PSCustomObject]@{Name=$name; SizeGB=$sizeGB; Path=$d.FullName}
    }
}

$tvDirs = $tvDirs | Sort-Object SizeGB -Descending

Write-Host "=== TV SHOWS TO DELETE ==="
$totalGB = 0
foreach ($t in $tvDirs) {
    Write-Host "$($t.SizeGB) GB  $($t.Name)"
    $totalGB += $t.SizeGB
}
Write-Host ""
Write-Host "Total TV shows: $($tvDirs.Count) folders, $([math]::Round($totalGB, 2)) GB"
Write-Host ""

# Delete them
Write-Host "Deleting..."
foreach ($t in $tvDirs) {
    Write-Host "  DELETING: $($t.Name) ($($t.SizeGB) GB)"
    Remove-Item $t.Path -Recurse -Force -ErrorAction SilentlyContinue
}
Write-Host "Done!"

Remove-PSDrive -Name "V" -Force