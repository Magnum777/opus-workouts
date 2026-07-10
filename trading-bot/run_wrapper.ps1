$p = Start-Process -FilePath "C:\ProgramData\chocolatey\bin\python3.14.exe" -ArgumentList "C:\Users\compj\.openclaw\workspace\trading-bot\run_executor.py" -NoNewWindow -RedirectStandardOutput "C:\Users\compj\.openclaw\workspace\trading-bot\executor_output.txt" -RedirectStandardError "C:\Users\compj\.openclaw\workspace\trading-bot\executor_error.txt" -PassThru
$pid = $p.Id
Write-Host $pid
Start-Sleep -Seconds 90
if (-not $p.HasExited) { $p.Kill(); Write-Host "TIMEOUT" } else { Write-Host "EXITED" }
