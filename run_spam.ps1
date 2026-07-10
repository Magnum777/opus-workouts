$p = Start-Process -FilePath "C:\ProgramData\chocolatey\bin\python3.14.exe" -ArgumentList "C:\Users\compj\.openclaw\workspace\scripts\gmail_spam_sweep_v2.py" -NoNewWindow -RedirectStandardOutput "C:\Users\compj\.openclaw\workspace\temp_spam_output.txt" -RedirectStandardError "C:\Users\compj\.openclaw\workspace\temp_spam_error.txt" -PassThru
$p.WaitForExit(180)
if (!$p.HasExited) { $p.Kill(); Write-Output "TIMEOUT" } else { Write-Output "DONE" }
