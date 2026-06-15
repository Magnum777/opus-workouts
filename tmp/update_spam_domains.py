with open('scripts/gmail_spam_sweep_v2.py', 'r') as f:
    content = f.read()

new_domains = [
    'fckfriendfinder.com', 'hers-love.com', 'bestxdateofferings.com',
    'flirtyynights.com', 'poladina.com', 'henrydixonjournal.net',
]

for domain in new_domains:
    if domain not in content:
        content = content.replace('    \"dialuxas.ru\",', f'    \"dialuxas.ru\",\n    \"{domain}\",')

with open('scripts/gmail_spam_sweep_v2.py', 'w') as f:
    f.write(content)

print('Added domains to spam sweep')
for d in new_domains:
    print(f'  - {d}')
