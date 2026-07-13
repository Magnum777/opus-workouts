$p = Get-Process -Id 25496 -ErrorAction SilentlyContinue
if ($p) {
    $p.WaitForExit(120000)
    Write-Host ("Exited: " + $p.HasExited + " Code: " + $p.ExitCode)
} else {
    Write-Host "Already finished"
}
