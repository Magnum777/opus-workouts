$outFile = "C:\Users\compj\.openclaw\workspace\trading-bot\executor_output.txt"
$job = Start-Job -ScriptBlock { param($f) & "C:\ProgramData\chocolatey\bin\python3.14.exe" $f 2>&1 } -ArgumentList "C:\Users\compj\.openclaw\workspace\trading-bot\run_executor.py"
Start-Sleep -Seconds 120
if ($job.State -eq 'Running') { Stop-Job $job; "TIMEOUT" } else { Receive-Job $job }
