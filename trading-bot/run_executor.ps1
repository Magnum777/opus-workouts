Set-Location -Path 'C:\Users\compj\.openclaw\workspace\trading-bot'
$p = Start-Process -NoNewWindow -FilePath 'cmd.exe' -ArgumentList '/c run_executor.cmd' -RedirectStandardOutput 'executor_output_new.txt' -RedirectStandardError 'executor_error.txt' -Wait -PassThru
exit $p.ExitCode
