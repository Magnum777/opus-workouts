$p = Start-Process -NoNewWindow -FilePath 'C:\ProgramData\chocolatey\bin\python3.14.exe' -ArgumentList 'C:\Users\compj\.openclaw\workspace\trading-bot\daemon.py' -RedirectStandardOutput 'C:\Users\compj\.openclaw\workspace\trading-bot\last_run_output.txt' -RedirectStandardError 'C:\Users\compj\.openclaw\workspace\trading-bot\last_run_errors.txt' -PassThru
$p.WaitForExit(180)
Write-Host ('EXIT_CODE: ' + $p.ExitCode)
