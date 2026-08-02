$ts = Get-Date -Format 'yyyy-MM-dd_HH-mm'
$localDest = "C:\Nova-Backups\openclaw-backup-$ts"
New-Item -ItemType Directory -Force -Path $localDest | Out-Null

Write-Host "Backing up workspace..."
Copy-Item -Path 'C:\Users\compj\.openclaw\workspace' -Destination "$localDest\workspace" -Recurse -Force -ErrorAction SilentlyContinue

if (Test-Path 'C:\Users\compj\.openclaw\gateway') {
    Write-Host "Backing up gateway..."
    Copy-Item -Path 'C:\Users\compj\.openclaw\gateway' -Destination "$localDest\gateway" -Recurse -Force -ErrorAction SilentlyContinue
}

if (Test-Path 'C:\Users\compj\.openclaw\skills') {
    Write-Host "Backing up skills..."
    Copy-Item -Path 'C:\Users\compj\.openclaw\skills' -Destination "$localDest\skills" -Recurse -Force -ErrorAction SilentlyContinue
}

if (Test-Path 'C:\Users\compj\.openclaw\agents') {
    Write-Host "Backing up agents..."
    Copy-Item -Path 'C:\Users\compj\.openclaw\agents' -Destination "$localDest\agents" -Recurse -Force -ErrorAction SilentlyContinue
}

$files = (Get-ChildItem -Path $localDest -Recurse -File -ErrorAction SilentlyContinue).Count
$sizeGB = [math]::Round((Get-ChildItem -Path $localDest -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
Write-Host "Local backup complete: $files files, ${sizeGB}GB"
Write-Host "Location: $localDest"
