$p = Start-Process -FilePath "C:\Users\compj\.openclaw\workspace\trading-bot\run_executor.cmd" -NoNewWindow -RedirectStandardOutput "C:\Users\compj\.openclaw\workspace\trading-bot\executor_output.txt" -RedirectStandardError "C:\Users\compj\.openclaw\workspace\trading-bot\executor_err.txt" -PassThru
Wait-Process -Id $p.Id -Timeout 120
$out = Get-Content "C:\Users\compj\.openclaw\workspace\trading-bot\executor_output.txt" -Raw
Write-Host $out
$err = Get-Content "C:\Users\compj\.openclaw\workspace\trading-bot\executor_err.txt" -Raw
if ($err -ne "") { Write-Host "STDERR:"; Write-Host $err }
