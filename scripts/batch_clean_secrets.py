import os, subprocess, re

WORKSPACE = r'C:\Users\compj\.openclaw\workspace'

# Get tracked py/ps1 files
r = subprocess.run(['git', '-C', WORKSPACE, 'ls-files', 'trading-bot/'], capture_output=True, text=True)
files = [os.path.join(WORKSPACE, f) for f in r.stdout.strip().split('\n') if f.endswith(('.py', '.ps1'))]

PK = 'edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d'
URL = 'https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887'

cleaned = 0
for fp in files:
    if not os.path.exists(fp):
        continue
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if PK not in content and URL not in content:
        continue
    
    if fp.endswith('.ps1'):
        content = content.replace(f'"{URL}"', '$env:HELIUS_RPC_URL')
        content = content.replace(f"'{URL}'", '$env:HELIUS_RPC_URL')
    else:
        content = content.replace(f'bytes.fromhex("{PK}")', 'bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", ""))')
        content = content.replace(f"bytes.fromhex('{PK}')", 'bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", ""))')
        content = content.replace(f'Client("{URL}")', 'Client(os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE"))')
        content = content.replace(f"Client('{URL}')", 'Client(os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE"))')
        content = content.replace(f'HELIUS = "{URL}"', 'HELIUS = os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE")')
        content = content.replace(f"HELIUS = '{URL}'", 'HELIUS = os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE")')
        content = content.replace(f'HELIUS_RPC = "{URL}"', 'HELIUS_RPC = os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE")')
        content = content.replace(f"HELIUS_RPC = '{URL}'", 'HELIUS_RPC = os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE")')
        content = content.replace(f'H = "{URL}"', 'H = os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE")')
        content = content.replace(f"H = '{URL}'", 'H = os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE")')
        content = content.replace('HELIUS_API_KEY = "2e3fb808-0c5f-4101-8c2b-82b4c4aa0887"', 'HELIUS_API_KEY = os.environ.get("HELIUS_API_KEY", "")')
        content = content.replace("HELIUS_API_KEY = '2e3fb808-0c5f-4101-8c2b-82b4c4aa0887'", 'HELIUS_API_KEY = os.environ.get("HELIUS_API_KEY", "")')
        content = content.replace(f'helius_url = "{URL}"', 'helius_url = os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE")')
        content = content.replace(f"helius_url = '{URL}'", 'helius_url = os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE")')
        
        # Ensure import os
        if 'import os' not in content and ('os.environ' in content):
            lines = content.split('\n')
            import_idx = next((i for i, l in enumerate(lines) if l.startswith('import ') or l.startswith('from ')), -1)
            if import_idx >= 0:
                lines.insert(import_idx, 'import os')
            else:
                lines.insert(0, 'import os')
            content = '\n'.join(lines)
    
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    cleaned += 1
    print(f'Cleaned: {os.path.relpath(fp, WORKSPACE)}')

print(f'\nTotal cleaned: {cleaned}')
