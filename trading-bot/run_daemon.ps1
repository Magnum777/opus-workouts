$p = Start-Process -FilePath 'C:\ProgramData\chocolatey\bin\python3.14.exe' -ArgumentList 'C:\Users\compj\.openclaw\workspace\trading-bot\daemon.py' -NoNewWindow -RedirectStandardOutput 'C:\Users\compj\.openclaw\workspace\trading-bot\daemon_output.txt' -RedirectStandardError 'C:\Users\compj\.openclaw\workspace\trading-bot\daemon_error.txt' -PassThru
Start-Sleep -Seconds 120
if (-not $p.HasExited) { $p.Kill(); Write-Output 'Killed after 120s' } else { Write-Output 'Exited naturally' }
