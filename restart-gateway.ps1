# Restart OpenClaw Gateway
Get-Process | Where-Object {$_.ProcessName -eq 'node' -and $_.MainWindowTitle -like '*openclaw*'} | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Start-Process -FilePath 'openclaw' -ArgumentList 'gateway','start' -NoNewWindow -WindowStyle Hidden
Write-Host 'Gateway restart initiated'
