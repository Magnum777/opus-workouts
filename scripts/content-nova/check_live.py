import requests
r = requests.get('https://www.aicofounderstack.com/2026/07/11/ai-cofounder-tools-for-startups-the-2026-guide-to-building-solo-with-ai/', timeout=15)
print(f'Status: {r.status_code}')
found = 'AI Cofounder Tools for Startups' in r.text
print(f'Title found: {found}')
print(f'Content length: {len(r.text)}')
