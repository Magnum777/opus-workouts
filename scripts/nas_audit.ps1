# NAS Audit - scan for duplicates, stale files, and space recovery
$cred = New-Object System.Management.Automation.PSCredential("Nova", (ConvertTo-SecureString 'D0ngaYHRuthV93qD' -AsPlainText -Force))
New-PSDrive -Name "Z" -PSProvider FileSystem -Root "\\MND\home" -Credential $cred -ErrorAction Stop | Out-Null

Write-Host "=== NAS Disk Usage ==="
$drive = Get-PSDrive Z
$freeGB = [math]::Round($drive.Free/1GB, 1)
$usedGB = [math]::Round($drive.Used/1GB, 1)
$totalGB = [math]::Round(($drive.Used + $drive.Free)/1GB, 1)
Write-Host "Used: $usedGB GB / Free: $freeGB GB / Total: $totalGB GB"
Write-Host ""

Write-Host "=== Top-Level Folders ==="
Get-ChildItem "Z:\" -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $s = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    [PSCustomObject]@{Folder=$_.Name; SizeGB=[math]::Round($s/1GB, 2); Files=(Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count}
} | Sort-Object SizeGB -Descending | Format-Table -AutoSize
Write-Host ""

Write-Host "=== Backups Folder Contents ==="
$backups = Get-ChildItem "Z:\backups" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
foreach ($f in $backups) {
    $sizeGB = [math]::Round($f.Length/1GB, 2)
    Write-Host "$($f.Name)  $sizeGB GB  $($f.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))"
}
$totalBackupGB = [math]::Round(($backups | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
Write-Host "Total backups: $totalBackupGB GB"
Write-Host ""

Write-Host "=== Finding Duplicates by Name Pattern ==="
# Check for same-day backups (multiple per day)
$groups = $backups | Group-Object { $_.Name -replace '-\d{4}$','' } | Where-Object { $_.Count -gt 1 }
foreach ($g in $groups) {
    Write-Host "Duplicate group: $($g.Name) ($($g.Count) files)"
    $dupSize = [math]::Round(($g.Group | Sort-Object LastWriteTime -Descending | Select-Object -Skip 1 | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
    Write-Host "  Can save: $dupSize GB (keep newest only)"
}
Write-Host ""

Write-Host "=== Files Older Than 14 Days ==="
$cutoff = (Get-Date).AddDays(-14)
$stale = Get-ChildItem "Z:\" -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -lt $cutoff }
$staleGroups = $stale | Group-Object { $_.Extension } | Sort-Object Count -Descending | Select-Object -First 15
foreach ($g in $staleGroups) {
    $sizeGB = [math]::Round(($g.Group | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
    Write-Host "$($g.Name): $($g.Count) files, $sizeGB GB"
}
$totalStaleGB = [math]::Round(($stale | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
Write-Host "Total stale (>$($cutoff.ToString('yyyy-MM-dd'))): $totalStaleGB GB"
Write-Host ""

Write-Host "=== Large Files (>100 MB) ==="
$large = Get-ChildItem "Z:\" -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt 100MB } | Sort-Object Length -Descending | Select-Object -First 20
foreach ($f in $large) {
    $sizeMB = [math]::Round($f.Length/1MB, 0)
    $relPath = $f.FullName.Replace("Z:\", "")
    Write-Host "$sizeMB MB  $($f.LastWriteTime.ToString('yyyy-MM-dd'))  $relPath"
}
Write-Host ""

Write-Host "=== Potential Savings Summary ==="
# Duplicate backups (keep 1 per day)
$dupSavings = 0
$perDay = $backups | Group-Object { $_.Name.Substring(0, $_.Name.LastIndexOf('-')) } | Where-Object { $_.Count -gt 1 }
foreach ($d in $perDay) {
    $keep = $d.Group | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $waste = $d.Group | Where-Object { $_.Name -ne $keep.Name }
    $dupSavings += ($waste | Measure-Object -Property Length -Sum).Sum
}
$dupGB = [math]::Round($dupSavings/1GB, 2)

# Backups older than 14 days
$oldBackups = $backups | Where-Object { $_.LastWriteTime -lt $cutoff }
$oldBackupGB = [math]::Round(($oldBackups | Measure-Object -Property Length -Sum).Sum / 1GB, 2)

Write-Host "Duplicate same-day backups to remove: $dupGB GB"
Write-Host "Backups older than 14 days: $oldBackupGB GB"
Write-Host "Total potential savings: $([math]::Round($dupSavings/1GB + $oldBackupGB, 2)) GB"

Remove-PSDrive -Name "Z" -Force