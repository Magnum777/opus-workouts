 = Start-Process -FilePath 'C:\ProgramData\chocolatey\bin\python3.14.exe' -ArgumentList '-u', 'C:\Users\compj\.openclaw\workspace\trading-bot\daemon.py' -NoNewWindow -RedirectStandardOutput 'C:\Users\compj\.openclaw\workspace\trading-bot\tradebot_out.txt' -RedirectStandardError 'C:\Users\compj\.openclaw\workspace\trading-bot\tradebot_err.txt' -PassThru
.WaitForExit(120)
Write-Host ("EXIT: " + .ExitCode)
