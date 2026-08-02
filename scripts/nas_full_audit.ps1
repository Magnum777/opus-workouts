# Full NAS audit - scan ALL shares, then clean up
$cred = New-Object System.Management.Automation.PSCredential("Nova", (ConvertTo-SecureString 'D0ngaYHRuthV93qD' -AsPlainText -Force))

# Mount home share
New-PSDrive -Name "Z" -PSProvider FileSystem -Root "\\MND\home" -Credential $cred -ErrorAction Stop | Out-Null

Write-Host "=== NAS HOME SHARE: Full Tree ==="
Write-Host ""

function Get-FolderSize {
    param($Path)
    $files = Get-ChildItem $Path -Recurse -File -ErrorAction SilentlyContinue
    $size = ($files | Measure-Object -Property Length -Sum).Sum
    $count = ($files | Measure-Object).Count
    [PSCustomObject]@{SizeGB=[math]::Round($size/1GB,2); Files=$count}
}

# List top-level dirs with sizes
$topDirs = Get-ChildItem "Z:\" -Directory -ErrorAction SilentlyContinue
foreach ($d in $topDirs) {
    $info = Get-FolderSize $d.FullName
    Write-Host "$($d.Name): $($info.SizeGB) GB ($($info.Files) files)"
}
# Also list loose files at root
$rootFiles = Get-ChildItem "Z:\" -File -ErrorAction SilentlyContinue
if ($rootFiles) {
    $rootSize = [math]::Round(($rootFiles | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
    Write-Host "(root files): $rootSize GB ($($rootFiles.Count) files)"
}
Write-Host ""

# Now go deeper into each top-level dir - show subfolders
foreach ($d in $topDirs) {
    Write-Host "=== $($d.Name)/ ==="
    $subs = Get-ChildItem $d.FullName -Directory -ErrorAction SilentlyContinue
    foreach ($s in $subs) {
        $sInfo = Get-FolderSize $s.FullName
        Write-Host "  $($s.Name): $($sInfo.SizeGB) GB ($($sInfo.Files) files)"
    }
    $looseFiles = Get-ChildItem $d.FullName -File -ErrorAction SilentlyContinue | Sort-Object Length -Descending | Select-Object -First 10
    foreach ($f in $looseFiles) {
        $fGB = [math]::Round($f.Length/1GB, 2)
        if ($fGB -gt 0.01) { Write-Host "  $($f.Name): $fGB GB" }
    }
    Write-Host ""
}

Remove-PSDrive -Name "Z" -Force -ErrorAction SilentlyContinue

# Try other shares
Write-Host "=== CHECKING OTHER NAS SHARES ==="
$shares = @("Nova", "video", "photo", "music", "docker", "web", "downloads")
foreach ($share in $shares) {
    $path = "\\MND\$share"
    try {
        New-PSDrive -Name "N" -PSProvider FileSystem -Root $path -Credential $cred -ErrorAction Stop | Out-Null
        $info = Get-FolderSize "N:\"
        Write-Host "$share`: $($info.SizeGB) GB ($($info.Files) files)"
        # Show top subfolders
        $subs = Get-ChildItem "N:\" -Directory -ErrorAction SilentlyContinue | Select-Object -First 20
        foreach ($s in $subs) {
            $sInfo = Get-FolderSize $s.FullName
            Write-Host "  $($s.Name): $($sInfo.SizeGB) GB"
        }
        Remove-PSDrive -Name "N" -Force -ErrorAction SilentlyContinue
    } catch {
        Write-Host "$share`: not accessible"
    }
}