# Disk check script
$disk = Get-PSDrive C
$usedGB = [math]::Round($disk.Used/1GB, 1)
$freeGB = [math]::Round($disk.Free/1GB, 1)
$totalGB = [math]::Round(($disk.Used + $disk.Free)/1GB, 1)
Write-Host "C: $usedGB GB used / $freeGB GB free / $totalGB GB total"

Write-Host ""
Write-Host "=== Temp folder ==="
$tmpFiles = Get-ChildItem $env:TEMP -Recurse -File -ErrorAction SilentlyContinue
$tmpSize = ($tmpFiles | Measure-Object -Property Length -Sum).Sum
$tmpMB = [math]::Round($tmpSize/1MB, 1)
Write-Host "Temp: $tmpMB MB in $($tmpFiles.Count) files"

Write-Host ""
Write-Host "=== OpenClaw workspace ==="
$wsFiles = Get-ChildItem "C:\Users\compj\.openclaw" -Recurse -File -ErrorAction SilentlyContinue
$wsSize = ($wsFiles | Measure-Object -Property Length -Sum).Sum
$wsMB = [math]::Round($wsSize/1MB, 1)
Write-Host "Workspace: $wsMB MB in $($wsFiles.Count) files"

Write-Host ""
Write-Host "=== Top folders under user profile ==="
Get-ChildItem "C:\Users\compj" -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $s = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    [PSCustomObject]@{Folder=$_.Name; SizeMB=[math]::Round($s/1MB, 1)}
} | Sort-Object SizeMB -Descending | Select-Object -First 15 | Format-Table -AutoSize

Write-Host ""
Write-Host "=== NAS backups ==="
$nasPath = "\\MND\home\backups"
if (Test-Path $nasPath) {
    $backups = Get-ChildItem $nasPath -Filter "workspace-backup-*.zip" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
    Write-Host "Found $($backups.Count) workspace backups on NAS:"
    $backups | ForEach-Object {
        $sizeMB = [math]::Round($_.Length/1MB, 1)
        Write-Host "  $($_.Name)  $sizeMB MB  $($_.LastWriteTime)"
    }
} else {
    Write-Host "NAS path not accessible, trying SMB mount..."
    try {
        $cred = New-Object System.Management.Automation.PSCredential("Nova", (ConvertTo-SecureString 'D0ngaYHRuthV93qD' -AsPlainText -Force))
        New-PSDrive -Name "Z" -PSProvider FileSystem -Root "\\MND\home" -Credential $cred -ErrorAction Stop | Out-Null
        $backups = Get-ChildItem "Z:\backups" -Filter "workspace-backup-*.zip" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
        Write-Host "Found $($backups.Count) workspace backups on NAS:"
        $backups | ForEach-Object {
            $sizeMB = [math]::Round($_.Length/1MB, 1)
            Write-Host "  $($_.Name)  $sizeMB MB  $($_.LastWriteTime)"
        }
        Remove-PSDrive -Name "Z" -Force
    } catch {
        Write-Host "ERROR: Cannot reach NAS - $($_.Exception.Message)"
    }
}