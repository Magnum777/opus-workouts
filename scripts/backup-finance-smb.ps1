param(
    [string]$Workspace = "C:\Users\compj\.openclaw\workspace",
    [string]$NasRoot = "\\MND\home\Nova\nova-backups\finance"
)

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$dest = Join-Path $NasRoot $timestamp

Write-Host "Creating backup directory: $dest"
New-Item -ItemType Directory -Path $dest -Force | Out-Null

$items = @(
    "credentials\plaid.env",
    "credentials\.plaid_tokens.json",
    "finance-dashboard",
    "scripts\plaid_finance.py",
    "scripts\plaid_link_server.py",
    "scripts\nova_finance_dashboard.py",
    "docs\nova-finance.md"
)

$totalFiles = 0
$totalSize = 0
$results = @()

foreach ($item in $items) {
    $src = Join-Path $Workspace $item
    if (Test-Path $src) {
        $itemObj = Get-Item $src
        if ($itemObj.PSIsContainer) {
            $files = Get-ChildItem -Recurse $src
            $count = $files.Count
            $size = ($files | Measure-Object -Property Length -Sum).Sum
            Copy-Item -Recurse -Path $src -Destination $dest
            $results += [PSCustomObject]@{Item=$item; Status="OK"; Files=$count; SizeKB=[math]::Round($size/1KB, 1)}
        } else {
            $count = 1
            $size = $itemObj.Length
            Copy-Item -Path $src -Destination $dest
            $results += [PSCustomObject]@{Item=$item; Status="OK"; Files=$count; SizeKB=[math]::Round($size/1KB, 1)}
        }
        $totalFiles += $count
        $totalSize += $size
    } else {
        $results += [PSCustomObject]@{Item=$item; Status="MISSING"; Files=0; SizeKB=0}
    }
}

$results | Format-Table -AutoSize
Write-Host "`n=== Summary ==="
Write-Host "Total files: $totalFiles"
Write-Host "Total size: $([math]::Round($totalSize/1MB, 2)) MB"
Write-Host "Backup path: $dest"
Write-Host "Status: SUCCESS"
