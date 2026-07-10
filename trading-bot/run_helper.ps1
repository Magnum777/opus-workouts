 = Start-Process -NoNewWindow -FilePath "C:\Users\compj\.openclaw\workspace\trading-bot\run_executor.cmd" -RedirectStandardOutput "C:\Users\compj\.openclaw\workspace\trading-bot\executor_out_tmp.txt" -RedirectStandardError "C:\Users\compj\.openclaw\workspace\trading-bot\executor_err_tmp.txt" -PassThru
Wait-Process -Id .Id -Timeout 45 -ErrorAction SilentlyContinue
if (-not .HasExited) {
  .Kill()
  Write-Output "TIMEOUT"
} else {
  Write-Output "COMPLETED"
}
