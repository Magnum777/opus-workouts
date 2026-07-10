<#
.SYNOPSIS
    Restart the OpenClaw Gateway safely.

.DESCRIPTION
    Finds all node processes related to openclaw, stops them cleanly,
    waits for cleanup, then starts a fresh gateway instance.
    Reports status so you know if something went wrong.

.EXAMPLE
    .\restart-gateway.ps1

.NOTES
    Requires openclaw to be on PATH.
#>

# Find and stop existing openclaw node processes
$processes = Get-Process | Where-Object {
    $_.ProcessName -eq 'node' -and $_.MainWindowTitle -like '*openclaw*'
}

if ($processes) {
    Write-Host "Stopping $($processes.Count) openclaw node process(es)..."
    $processes | Stop-Process -Force
    Start-Sleep -Seconds 3
} else {
    Write-Host "No openclaw processes found running."
}

# Also catch any stray node processes that might be the gateway
$allNode = Get-Process node -ErrorAction SilentlyContinue
if ($allNode) {
    $stray = $allNode | Where-Object { $_.MainWindowTitle -like '*openclaw*' -or $_.CommandLine -like '*openclaw*' }
    if ($stray) {
        Write-Host "Found $($stray.Count) stray node process(es), stopping..."
        $stray | Stop-Process -Force
        Start-Sleep -Seconds 2
    }
}

# Start the gateway
Write-Host 'Starting OpenClaw Gateway...'
$proc = Start-Process -FilePath 'openclaw' -ArgumentList 'gateway','start' -NoNewWindow -WindowStyle Hidden -PassThru

# Verify it started
Start-Sleep -Seconds 5
$running = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
if ($running) {
    Write-Host "Gateway started (PID: $($proc.Id))"
} else {
    Write-Error "Gateway may have failed to start. Check logs."
}
