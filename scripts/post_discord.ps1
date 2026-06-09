$body = @{
  content = "**Nova Trading Bot - FAST SCAN**`n````nSOL: 0.6585 (`$56.77)`nNo active positions`nTotal Portfolio: `$56.77`n````n_Position check only - no trades executed_ | 2026-04-07 23:34 UTC"
} | ConvertTo-Json -Compress

Invoke-RestMethod -Uri "https://discord.com/api/v10/channels/149285899270447104/messages" `
  -Method POST `
  -Headers @{ "Authorization" = "Bot DISCORD_BOT_TOKEN_REDACTED" } `
  -ContentType "application/json" `
  -Body $body