"""Audit for secrets in git-tracked files."""
import re, os, subprocess
from pathlib import Path

PATTERNS = [
    (r'api_key\s*=\s*["\'][^"\']{10,}', 'api_key'),
    (r'apikey\s*=\s*["\'][^"\']{10,}', 'apikey'),
    (r'password\s*=\s*["\'][^"\']{6,}', 'password'),
    (r'secret\s*=\s*["\'][^"\']{10,}', 'secret'),
    (r'token\s*=\s*["\'][^"\']{10,}', 'token'),
    (r'client_secret\s*=\s*["\']?[^\s,)\]]+', 'client_secret'),
    (r'sk-[a-zA-Z0-9]{20,}', 'openai_key'),
    (r'[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}', 'jwt'),
    (r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----', 'private_key'),
    (r'gmail_password', 'gmail_password'),
    (r'smtp_password', 'smtp_password'),
    (r'app_password', 'app_password'),
    (r'nova:sp4B', 'eveonion_old'),
    (r'nova:DUau', 'eveonion_old'),
    (r'nova:PXop', 'eveonion_old'),
    (r'nova:sDLx', 'eveonion_old'),
]

EXCLUDES = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'env'}
SKIP_EXTS = {'.db', '.lock', '.log', '.tmp', '.png', '.jpg', '.webp', '.gif', '.pdf', '.zip', '.tar', '.gz', '.exe', '.dll', '.jsonl', '.trajectory'}

FALSE_POSITIVES = ['get_credential', 'vault_helper', 'env.get', 'os.environ', 'config.get', 'example', 'placeholder', 'your_', 'xxxx', 'test_', 'mock_', 'fake_', 'changeme', 'CHANGEME', 'getenv', 'from vault']

# Only check git-tracked files
git_files = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
tracked = set(git_files.stdout.strip().split('\n'))

hits = []
for f in tracked:
    if any(f.endswith(e) for e in SKIP_EXTS):
        continue
    path = Path(f)
    if not path.exists():
        continue
    try:
        content = path.read_text(errors='ignore')
    except:
        continue
    for pat, label in PATTERNS:
        for m in re.finditer(pat, content):
            line_num = content[:m.start()].count('\n') + 1
            line = content.split('\n')[line_num-1].strip()
            if any(x in line.lower() for x in FALSE_POSITIVES):
                continue
            if line.startswith('#') or line.startswith('//'):
                continue
            # Skip vault helper itself (has 'get_credential' in it which is fine)
            if 'vault_helper' in f:
                continue
            hits.append(f'{f}:{line_num} [{label}] {line[:100]}')

for h in hits[:80]:
    print(h)
print(f'--- Total potential hits: {len(hits)} ---')
