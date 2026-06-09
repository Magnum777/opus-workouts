# Fix Discord for #professional channel

## Step 1: Update the Discord bot token env var

Run this in PowerShell as Administrator:

```powershell
# Set new bot token (system-wide)
[Environment]::SetEnvironmentVariable("DISCORD_BOT_TOKEN", "DISCORD_BOT_TOKEN_REDACTED", "Machine")

# Also set for current session
$env:DISCORD_BOT_TOKEN = "DISCORD_BOT_TOKEN_REDACTED"
```

## Step 2: Update openclaw.json

Run this to add `#professional` to the Discord guild config:

```powershell
$configPath = "$env:USERPROFILE\.openclaw\openclaw.json"
$content = Get-Content $configPath -Raw

# Remove ANSI codes if present
$content = $content -replace "`e\[[0-9;]*m", ""
$config = $content | ConvertFrom-Json

# Add professional channel to guild
$config.channels.discord.guilds."1425600872938995714".channels | Add-Member -MemberType NoteProperty -Name "professional" -Value @{ enabled = $true } -Force

# Add binding for linkedin-manager agent to #professional
$newBinding = @{
    agentId = "linkedin-manager"
    match = @{
        channel = "discord"
        peer = @{
            kind = "channel"
            id = "1509605510163333363"
        }
    }
}
$config.bindings += $newBinding

# Save
$config | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8
Write-Host "Config updated!"
```

## Step 3: Restart gateway

```powershell
openclaw gateway restart
```

## Verify

After restart, check:
```powershell
openclaw gateway status
```

Then test by sending a message in `#professional` — the linkedin-manager agent should respond.
