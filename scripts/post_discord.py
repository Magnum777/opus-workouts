import urllib.request, json

msg = (
    "**Nova Trading Bot - FAST SCAN**\n"
    "```\n"
    "SOL: 0.6585 ($56.77)\n"
    "No active positions\n"
    "Total Portfolio: $56.77\n"
    "```\n"
    "_Position check only - no trades executed_ | 2026-04-07 23:34 UTC"
)

body = json.dumps({"content": msg})
req = urllib.request.Request(
    "https://discord.com/api/v10/channels/149285899270447104/messages",
    data=body.encode(),
    headers={
        "Authorization": "Bot DISCORD_BOT_TOKEN_REDACTED",
        "Content-Type": "application/json"
    },
    method="POST"
)
with urllib.request.urlopen(req) as resp:
    print(resp.status)