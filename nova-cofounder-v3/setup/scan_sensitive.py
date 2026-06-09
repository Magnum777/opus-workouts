import os
from pathlib import Path

base = Path(r'C:\Users\compj\.openclaw\workspace\nova-cofounder-v3')
sensitive_terms = [
    'compjunkie', 'jhenderson87', 'layeredmediallc', 'nova.cofounder',
    '192.168.68.', 'MND', 'MGD', '9800X3D', '9070 XT',
    '7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA',
    'ntn_144733', 'n_144733',
    'DUau yrXK', 'sp4B Fqlq', 'aX9$E$4l', 'Ro7IoPnc',
    'NAS_PASSWORD_REDACTED',
    'opusmagnum', '137379362700787713',
    '1425600872938995714', '1470831964721250395',
    'Magnum777',
]

print('=== SENSITIVE DATA SCAN ===')
print(f'Scanning: {base}')
print()

all_clean = True
for term in sensitive_terms:
    found_any = False
    for file_path in base.rglob('*'):
        if file_path.is_file() and '.git' not in str(file_path):
            # Skip the scan script itself
            if 'scan_sensitive' in str(file_path):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                if term.lower() in content.lower():
                    if not found_any:
                        print(f'--- {term} ---')
                        found_any = True
                    rel_path = file_path.relative_to(base)
                    print(f'  FOUND: {rel_path}')
                    all_clean = False
            except:
                pass
    if found_any:
        print()

if all_clean:
    print('OK: NO SENSITIVE DATA FOUND')
else:
    print('WARNING: SENSITIVE DATA DETECTED - SEE ABOVE')
