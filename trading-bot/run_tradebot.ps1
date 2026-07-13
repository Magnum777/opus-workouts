$p = Start-Process -FilePath 'C:\ProgramData\chocolatey\bin\python3.14.exe' -ArgumentList 'C:\Users\compj\.openclaw\workspace\trading-bot\run_executor.py' -WorkingDirectory 'C:\Users\compj\.openclaw\workspace\trading-bot' -NoNewWindow -RedirectStandardOutput 'C:\Users\compj\.openclaw\workspace\trading-bot\executor_output.txt' -RedirectStandardError 'C:\Users\compj\.openclaw\workspace\trading-bot\executor_err.txt' -PassThru
$p | Wait-Process -Timeout 120
Write-Output 'done'
