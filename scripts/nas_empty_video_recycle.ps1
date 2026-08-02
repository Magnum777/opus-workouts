# Empty the video share recycle bin
$cred = New-Object System.Management.Automation.PSCredential("Nova", (ConvertTo-SecureString 'D0ngaYHRuthV93qD' -AsPlainText -Force))
New-PSDrive -Name "V" -PSProvider FileSystem -Root "\\MND\video" -Credential $cred -ErrorAction Stop | Out-Null

# Check recycle bin size
$recycle = Get-ChildItem "V:\#recycle" -Recurse -File -ErrorAction SilentlyContinue
if ($recycle) {
    $recycleGB = [math]::Round(($recycle | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
    Write-Host "Video recycle bin: $($recycle.Count) files, $recycleGB GB"
    Write-Host "Deleting..."
    Remove-Item "V:\#recycle\*" -Recurse -Force -ErrorAction SilentlyContinue
    # Verify
    $after = Get-ChildItem "V:\#recycle" -Recurse -File -ErrorAction SilentlyContinue
    $afterGB = 0
    if ($after) { $afterGB = [math]::Round(($after | Measure-Object -Property Length -Sum).Sum / 1GB, 2) }
    Write-Host "After: $afterGB GB remaining"
} else {
    Write-Host "No recycle bin found or already empty"
}

Remove-PSDrive -Name "V" -Force