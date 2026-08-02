# Clean up NAS backups - keep newest per day, keep 14-day window
$cred = New-Object System.Management.Automation.PSCredential("Nova", (ConvertTo-SecureString 'D0ngaYHRuthV93qD' -AsPlainText -Force))
New-PSDrive -Name "Z" -PSProvider FileSystem -Root "\\MND\home" -Credential $cred -ErrorAction Stop | Out-Null

$backups = Get-ChildItem "Z:\backups" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending

# Files to delete - same-day duplicates (keep newest per day)
$perDay = $backups | Where-Object { $_.Name -like "workspace-backup-*" } | Group-Object { ($_.Name -replace '-\d{4}\.zip$', '') }
$toDelete = @()
foreach ($g in $perDay) {
    if ($g.Count -gt 1) {
        $keep = $g.Group | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        $waste = $g.Group | Sort-Object LastWriteTime -Descending | Select-Object -Skip 1
        foreach ($w in $waste) {
            $toDelete += $w
        }
    }
}

# Also add empty mirror dirs
$mirrors = $backups | Where-Object { $_.Name -like "workspace-mirror*" }
foreach ($m in $mirrors) {
    $files = Get-ChildItem $m.FullName -Recurse -File -ErrorAction SilentlyContinue
    if ($files.Count -eq 0) {
        $toDelete += $m
    }
}

$totalSavings = [math]::Round(($toDelete | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
Write-Host "Deleting $($toDelete.Count) items, saving $totalSavings GB:"
foreach ($f in $toDelete) {
    $fGB = [math]::Round($f.Length/1GB, 2)
    Write-Host "  DELETE: $($f.Name) ($fGB GB)"
    Remove-Item $f.FullName -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "=== Remaining backups ==="
$remaining = Get-ChildItem "Z:\backups" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
foreach ($f in $remaining) {
    $fGB = [math]::Round($f.Length/1GB, 2)
    Write-Host "$($f.Name)  $fGB GB  $($f.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))"
}
$totalRemaining = [math]::Round(($remaining | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
Write-Host "Total remaining: $totalRemaining GB"

Remove-PSDrive -Name "Z" -Force