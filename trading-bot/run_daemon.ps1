$p = Start-Process -FilePath "C:\ProgramData\chocolatey\bin\python3.14.exe" -ArgumentList "C:\Users\compj\.openclaw\workspace\trading-bot\daemon.py" -NoNewWindow -RedirectStandardOutput "C:\Users\compj\.openclaw\workspace\trading-bot\last_run_out.txt" -RedirectStandardError "C:\Users\compj\.openclaw\workspace\trading-bot\last_run_err.txt" -PassThru
$p.WaitForExit(90)
if (!$p.HasExited) { $p.Kill(); Write-Output "TIMEOUT" } else { Write-Output "DONE" }
