# Empty the home recycle bin on NAS
$cred = New-Object System.Management.Automation.PSCredential("Nova", (ConvertTo-SecureString 'D0ngaYHRuthV93qD' -AsPlainText -Force))
New-PSDrive -Name "Z" -PSProvider FileSystem -Root "\\MND\home" -Credential $cred -ErrorAction Stop | Out-Null

# Check recycle bin size first
$recycle = Get-ChildItem "Z:\#recycle" -Recurse -File -ErrorAction SilentlyContinue
$recycleGB = [math]::Round(($recycle | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
Write-Host "Recycle bin: $($recycle.Count) files, $recycleGB GB"
Write-Host "Deleting..."
Remove-Item "Z:\#recycle\*" -Recurse -Force -ErrorAction SilentlyContinue

# Verify
$after = Get-ChildItem "Z:\#recycle" -Recurse -File -ErrorAction SilentlyContinue
$afterGB = 0
if ($after) { $afterGB = [math]::Round(($after | Measure-Object -Property Length -Sum).Sum / 1GB, 2) }
Write-Host "After: $afterGB GB remaining"

Remove-PSDrive -Name "Z" -Force