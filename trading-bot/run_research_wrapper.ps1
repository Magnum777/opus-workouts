$j = Start-Job -ScriptBlock { param($p,$a) & $p $a } -ArgumentList 'C:\ProgramData\chocolatey\bin\python3.14.exe','C:\Users\compj\.openclaw\workspace\trading-bot\run_research.py'
Wait-Job $j -Timeout 180 | Out-Null
$r = Receive-Job $j
Write-Output $r
Remove-Job $j -Force
