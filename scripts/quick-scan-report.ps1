$token = "DISCORD_BOT_TOKEN_REDACTED"
$channelId = "1470957359248576699"

# Message with proper escaping
$msg = "QuickScan Report | 1:54 PM ET - SOL: 0.4626 (USD 37.05). No active positions. Total: USD 37.05. Position check only."

$body = @{"content" = $msg} | ConvertTo-Json -Compress
$headers = @{"Authorization" = "Bot $token"; "Content-Type" = "application/json"}

try {
    $r = Invoke-RestMethod -Uri "https://discord.com/api/v10/channels/$channelId/messages" -Method Post -Headers $headers -Body $body
    Write-Host "OK: $($r.id)"
} catch {
    Write-Host "ERR: $($_.Exception.Message)"
}