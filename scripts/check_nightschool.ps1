# Check night-school viewer on NAS
$cred = New-Object System.Management.Automation.PSCredential("Nova", (ConvertTo-SecureString 'D0ngaYHRuthV93qD' -AsPlainText -Force))
New-PSDrive -Name "Z" -PSProvider FileSystem -Root "\\MND\home" -Credential $cred -ErrorAction Stop | Out-Null

Write-Host "=== night-school folder ==="
Get-ChildItem "Z:\night-school" -ErrorAction SilentlyContinue | Format-Table Name,Length,LastWriteTime -AutoSize

Write-Host ""
Write-Host "=== night-school-viewer.html ==="
$viewer = Get-Item "Z:\night-school-viewer.html" -ErrorAction SilentlyContinue
if ($viewer) {
    Write-Host "Size: $([math]::Round($viewer.Length/1KB, 1)) KB"
    Write-Host "Modified: $($viewer.LastWriteTime)"
    $content = Get-Content $viewer.FullName -Raw -ErrorAction SilentlyContinue
    # Find the topics count
    if ($content -match '(\d+)\s+topics') { Write-Host "Topics mentioned: $($Matches[1])" }
    # Find last updated date if present
    if ($content -match '(\d{4}-\d{2}-\d{2})') { Write-Host "Date found in content: $($Matches[1])" }
} else {
    Write-Host "NOT FOUND"
}

Write-Host ""
Write-Host "=== Local viewer for comparison ==="
$local = Get-Item "C:\Users\compj\.openclaw\workspace\night-school-viewer.html" -ErrorAction SilentlyContinue
if ($local) {
    Write-Host "Size: $([math]::Round($local.Length/1KB, 1)) KB"
    Write-Host "Modified: $($local.LastWriteTime)"
} else {
    Write-Host "No local copy found"
}

Remove-PSDrive -Name "Z" -Force