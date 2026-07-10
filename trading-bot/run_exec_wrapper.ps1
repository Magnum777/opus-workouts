$p = Start-Process -FilePath "C:\Users\compj\.openclaw\workspace\trading-bot\run_executor.cmd" -NoNewWindow -RedirectStandardOutput "C:\Users\compj\.openclaw\workspace\trading-bot\exec_out.txt" -RedirectStandardError "C:\Users\compj\.openclaw\workspace\trading-bot\exec_err.txt" -PassThru
Wait-Process -Id $p.Id -Timeout 90 -ErrorAction SilentlyContinue
if (-not $p.HasExited) { $p.Kill(); "TIMEOUT" } else { "DONE" }
