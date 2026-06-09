$token = "DISCORD_BOT_TOKEN_REDACTED"
$channelId = "1470957359248576699"
$msg = "QuickScan Report | 1:54 PM ET - SOL: 0.4626. No active positions. Total Portfolio: $37.05. Position check only."
$body = @{"content" = $msg} | ConvertTo-Json -Compress
$headers = @{"Authorization" = "Bot $token"; "Content-Type" = "application/json"}
try {
    $r = Invoke-RestMethod -Uri "https://discord.com/api/v10/channels/$channelId/messages" -Method Post -Headers $headers -Body $body
    Write-Host "Sent: $($r.id)"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    $err = $_.Exception.Response
    if ($err) {
        $reader = [System.IO.StreamReader]::new($err.GetResponseStream())
        $body = $reader.ReadToEnd()
        $reader.Close()
        Write-Host "Response: $body"
    }
}