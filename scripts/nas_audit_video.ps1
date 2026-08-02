# Audit video share - top-level folders with sizes
$cred = New-Object System.Management.Automation.PSCredential("Nova", (ConvertTo-SecureString 'D0ngaYHRuthV93qD' -AsPlainText -Force))
New-PSDrive -Name "V" -PSProvider FileSystem -Root "\\MND\video" -Credential $cred -ErrorAction Stop | Out-Null

Write-Host "=== VIDEO share top-level ==="
Get-ChildItem "V:\" -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $size = 0; $count = 0
    $items = Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue
    $size = ($items | Measure-Object -Property Length -Sum).Sum
    $count = ($items | Measure-Object).Count
    $gb = [math]::Round($size/1GB, 2)
    [PSCustomObject]@{Folder=$_.Name; SizeGB=$gb; Files=$count}
} | Sort-Object SizeGB -Descending | Format-Table -AutoSize

Write-Host ""
Write-Host "=== Large files (>1 GB) ==="
Get-ChildItem "V:\" -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt 1GB } | Sort-Object Length -Descending | Select-Object -First 30 | ForEach-Object {
    $gb = [math]::Round($_.Length/1GB, 2)
    $rel = $_.FullName.Replace("V:\", "")
    Write-Host "$gb GB  $rel"
}

Remove-PSDrive -Name "V" -Force -ErrorAction SilentlyContinue