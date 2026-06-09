#!/usr/bin/env pwsh
# Backup workspace to NAS
$date = Get-Date -Format "yyyy-MM-dd-HHmm"
$source = "C:\Users\compj\.openclaw\workspace"
$localZip = "C:\Users\compj\workspace-backup-$date.zip"
$nasDest = "Z:\backups\workspace-backup-$date.zip"

Write-Host "Creating lightweight backup..." -ForegroundColor Green

# Ensure backups dir exists
if (-not (Test-Path "Z:\backups")) {
    New-Item -ItemType Directory -Path "Z:\backups" -Force | Out-Null
}

# Create zip excluding heavy dirs
$exclude = @('ComfyUI','stable-diffusion-webui','media','node_modules','.git')
$items = Get-ChildItem $source -Exclude $exclude | Select-Object -ExpandProperty FullName

Compress-Archive -Path $items -DestinationPath $localZip -Force

Write-Host "Copying to NAS..." -ForegroundColor Green
Copy-Item $localZip $nasDest -Force

# Verify
if (Test-Path $nasDest) {
    $size = (Get-Item $nasDest).Length / 1MB
    Write-Host "Backup complete: $nasDest ($([math]::Round($size,1)) MB)" -ForegroundColor Green
} else {
    Write-Host "Backup FAILED" -ForegroundColor Red
}

# Cleanup
Remove-Item $localZip -Force
net use Z: /delete 2>$null
Write-Host "Done." -ForegroundColor Green
