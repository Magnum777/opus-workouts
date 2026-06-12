$p = Start-Process -NoNewWindow -FilePath 'C:\ProgramData\chocolatey\bin\python3.14.exe' -ArgumentList 'C:\Users\compj\.openclaw\workspace\trading-bot\daemon.py' -RedirectStandardOutput 'daemon_out.txt' -RedirectStandardError 'daemon_err.txt' -PassThru
Wait-Process -Id $p.Id -Timeout 90
$rc = $p.ExitCode
Write-Host "Exit code: $rc"
Get-Content daemon_out.txt
Write-Host "===ERR==="
Get-Content daemon_err.txt
