$p = Start-Process -FilePath 'C:\ProgramData\chocolatey\bin\python3.14.exe' -ArgumentList 'C:\Users\compj\.openclaw\workspace\scripts\gmail_spam_sweep_v2.py' -NoNewWindow -RedirectStandardOutput 'C:\Users\compj\.openclaw\workspace\temp\spam_out.txt' -RedirectStandardError 'C:\Users\compj\.openclaw\workspace\temp\spam_err.txt' -PassThru
$p.WaitForExit(120)
if ($p.ExitCode -eq 0) {
    Get-Content 'C:\Users\compj\.openclaw\workspace\temp\spam_out.txt'
} else {
    Write-Host "EXIT:" $p.ExitCode
    Get-Content 'C:\Users\compj\.openclaw\workspace\temp\spam_err.txt'
}
