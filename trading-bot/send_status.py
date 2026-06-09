import httpx
import json

async def main():
    payload = {
        "action": "send",
        "channel": "discord",
        "to": "channel:1470957359248576699",
        "message": "**📊 Trading Bot Status — QuickScan**\n\n**Portfolio:**\n- SOL: 0.6572 ($54.02)\n- Active positions: None\n- **Total: $54.02**\n\nPosition check only — no trades executed."
    }
    # This would need to go through OpenClaw's message system - just output for reference
    print(json.dumps(payload))

import asyncio
asyncio.run(main())