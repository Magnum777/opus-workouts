# QuickScan Discord Reporter
$token = "DISCORD_BOT_TOKEN_REDACTED"
$channelId = "1470957359248576699"
$message = "QuickScan Report | 3:24 PM ET - SOL: 0.6628 ($53.43). No active positions. Total: $53.43. Position check only."

$body = @{
    content = $message
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bot $token"
    "Content-Type" = "application/json"
}

$response = Invoke-RestMethod -Uri "https://discord.com/api/v10/channels/$channelId/messages" `
    -Method Post `
    -Headers $headers `
    -Body $body

Write-Host "Message sent: $($response.id)"
