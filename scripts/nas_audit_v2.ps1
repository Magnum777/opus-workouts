# Fast NAS audit - only top-level sizes, no deep recursion
$cred = New-Object System.Management.Automation.PSCredential("Nova", (ConvertTo-SecureString 'D0ngaYHRuthV93qD' -AsPlainText -Force))
New-PSDrive -Name "Z" -PSProvider FileSystem -Root "\\MND\home" -Credential $cred -ErrorAction Stop | Out-Null

Write-Host "=== HOME share top-level ==="
Get-ChildItem "Z:\" -ErrorAction SilentlyContinue | ForEach-Object {
    $size = 0; $count = 0
    if ($_.PSIsContainer) {
        $items = Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue
        $size = ($items | Measure-Object -Property Length -Sum).Sum
        $count = ($items | Measure-Object).Count
    } else {
        $size = $_.Length; $count = 1
    }
    $gb = [math]::Round($size/1GB, 2)
    Write-Host "$($_.Name): $gb GB ($count files)"
} | Sort-Object { [double]($_ -split ': ')[1] -replace ' GB.*','' } -Descending

Remove-PSDrive -Name "Z" -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=== Checking other shares ==="
$shares = @("Nova", "video", "photo", "music", "docker", "web", "downloads", "backups")
foreach ($share in $shares) {
    try {
        New-PSDrive -Name "Y" -PSProvider FileSystem -Root "\\MND\$share" -Credential $cred -ErrorAction Stop | Out-Null
        $items = Get-ChildItem "Y:\" -Recurse -File -ErrorAction SilentlyContinue
        $size = [math]::Round(($items | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
        $count = ($items | Measure-Object).Count
        Write-Host "$share`: $size GB ($count files)"
        Remove-PSDrive -Name "Y" -Force -ErrorAction SilentlyContinue
    } catch {
        Write-Host "$share`: not accessible"
    }
}