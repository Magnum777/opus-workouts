<#
.SYNOPSIS
    Run the TradeBot daemon as a background process.

.DESCRIPTION
    Starts trading-bot/daemon.py using the system Python interpreter
    (looks for 'python' on PATH, falls back to python3.14).
    Redirects stdout/stderr to log files and reports exit code.
    Timeout is 90 seconds — the daemon should handle its own loop
    internally, so this wrapper just manages one startup attempt.

.EXAMPLE
    .\run_daemon.ps1

.NOTES
    If daemon fails immediately, check daemon_err.txt for details.
#>

# Find Python on PATH (prefer 'python', fallback to 'python3.14')
$pythonExe = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonExe) {
    $pythonExe = Get-Command python3.14 -ErrorAction SilentlyContinue
    if (-not $pythonExe) {
        Write-Error "Python not found on PATH. Install Python or add it to PATH."
        exit 1
    }
}

$daemonPath = Resolve-Path "$PSScriptRoot\trading-bot\daemon.py" -ErrorAction SilentlyContinue
if (-not $daemonPath) {
    $daemonPath = Join-Path $PSScriptRoot 'trading-bot' 'daemon.py'
}

Write-Host "Starting daemon with $($pythonExe.Source)..."

$p = Start-Process -NoNewWindow `
    -FilePath $pythonExe.Source `
    -ArgumentList $daemonPath `
    -RedirectStandardOutput 'daemon_out.txt' `
    -RedirectStandardError 'daemon_err.txt' `
    -PassThru

# Wait with timeout
try {
    $p | Wait-Process -Timeout 90 -ErrorAction Stop
    $rc = $p.ExitCode
    Write-Host "Exit code: $rc"

    if (Test-Path daemon_out.txt) {
        Write-Host "--- stdout ---"
        Get-Content daemon_out.txt -Raw | Write-Host
    }
    if (Test-Path daemon_err.txt) {
        Write-Host "--- stderr ---"
        Get-Content daemon_err.txt -Raw | Write-Host
    }

    if ($rc -ne 0) {
        Write-Warning "Daemon exited with code $rc. Check logs above."
    }
} catch {
    # Timeout — daemon is still running (which is expected for a long-running process)
    Write-Host "Daemon still running after 90s timeout (PID: $($p.Id))"
}
