# Quick NAS audit - targeted, not recursive walk
$cred = New-Object System.Management.Automation.PSCredential("Nova", (ConvertTo-SecureString 'D0ngaYHRuthV93qD' -AsPlainText -Force))
New-PSDrive -Name "Z" -PSProvider FileSystem -Root "\\MND\home" -Credential $cred -ErrorAction Stop | Out-Null

Write-Host "=== NAS Backups Folder ==="
$backups = Get-ChildItem "Z:\backups" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
$totalBackupGB = 0
foreach ($f in $backups) {
    $sizeGB = [math]::Round($f.Length/1GB, 2)
    $totalBackupGB += $sizeGB
    Write-Host "$($f.Name)  $sizeGB GB  $($f.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))"
}
Write-Host "Total in backups: $([math]::Round($totalBackupGB, 2)) GB"
Write-Host ""

# Find duplicates - same-day backups
Write-Host "=== Same-Day Duplicate Backups ==="
$dupSavings = 0
$perDay = $backups | Group-Object { ($_.Name -split '-')[0..3] -join '-' }
foreach ($g in ($perDay | Where-Object { $_.Count -gt 1 } | Sort-Object Name)) {
    $sorted = $g.Group | Sort-Object LastWriteTime -Descending
    $keep = $sorted[0]
    $waste = $sorted[1..($sorted.Count-1)]
    $wasteGB = [math]::Round(($waste | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
    Write-Host "$($g.Name): keep $($keep.Name), remove:"
    foreach ($w in $waste) {
        $wGB = [math]::Round($w.Length/1GB, 2)
        Write-Host "  REMOVE: $($w.Name) ($wGB GB)"
    }
    $dupSavings += ($waste | Measure-Object -Property Length -Sum).Sum
}
$dupGB = [math]::Round($dupSavings/1GB, 2)
Write-Host "Duplicate savings: $dupGB GB"
Write-Host ""

# Backups older than 14 days
Write-Host "=== Backups Older Than 14 Days ==="
$cutoff = (Get-Date).AddDays(-14)
$old = $backups | Where-Object { $_.LastWriteTime -lt $cutoff }
$oldGB = [math]::Round(($old | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
foreach ($f in $old) {
    $sGB = [math]::Round($f.Length/1GB, 2)
    Write-Host "$($f.Name)  $sGB GB  $($f.LastWriteTime.ToString('yyyy-MM-dd'))"
}
Write-Host "Old backup savings: $oldGB GB"
Write-Host ""

# Now check other top-level folders (just listing, not recursive)
Write-Host "=== Other Top-Level Folders ==="
Get-ChildItem "Z:\" -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $size = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    $gb = [math]::Round($size/1GB, 2)
    [PSCustomObject]@{Folder=$_.Name; SizeGB=$gb}
} | Sort-Object SizeGB -Descending | Format-Table -AutoSize
Write-Host ""

# Summary
$totalSavings = [math]::Round($dupGB + $oldGB, 2)
Write-Host "=== SUMMARY ==="
Write-Host "Duplicates (keep newest per day):  $dupGB GB"
Write-Host "Backups older than 14 days:        $oldGB GB"
Write-Host "Total potential savings:           $totalSavings GB"

Remove-PSDrive -Name "Z" -Force