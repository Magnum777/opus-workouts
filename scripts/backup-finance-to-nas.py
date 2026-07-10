#!/usr/bin/env python3
"""
Backup finance data to Synology NAS
Run manually or via cron
"""

import shutil
import subprocess
from pathlib import Path
from datetime import datetime

NAS_HOST = "192.168.68.82"
NAS_USER = "Nova"
NAS_PATH = "/volume1/homes/Nova/nova-backups/finance"
LOCAL_DIR = Path("C:/Users/compj/.openclaw/workspace")

# What to back up
BACKUP_ITEMS = [
    "credentials/plaid.env",
    "credentials/.plaid_tokens.json",
    "finance-dashboard/",
    "scripts/plaid_finance.py",
    "scripts/plaid_link_server.py",
    "scripts/nova_finance_dashboard.py",
    "docs/nova-finance.md",
]

def main():
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = f"{NAS_PATH}/{timestamp}"
    
    print(f"Backing up to {NAS_HOST}:{backup_dir}")
    
    # Create remote dir via SSH
    subprocess.run([
        "ssh", f"{NAS_USER}@{NAS_HOST}",
        f"mkdir -p {backup_dir}"
    ], check=True)
    
    # Copy each item
    for item in BACKUP_ITEMS:
        src = LOCAL_DIR / item
        if src.exists():
            if src.is_dir():
                subprocess.run([
                    "scp", "-r", str(src),
                    f"{NAS_USER}@{NAS_HOST}:{backup_dir}/"
                ], check=True)
            else:
                subprocess.run([
                    "scp", str(src),
                    f"{NAS_USER}@{NAS_HOST}:{backup_dir}/"
                ], check=True)
            print(f"  [OK] {item}")
        else:
            print(f"  [MISSING] {item}")
    
    # Update latest symlink
    subprocess.run([
        "ssh", f"{NAS_USER}@{NAS_HOST}",
        f"ln -sfn {backup_dir} {NAS_PATH}/latest"
    ], check=True)
    
    print(f"\nDone. Latest: {NAS_HOST}:{NAS_PATH}/latest")

if __name__ == "__main__":
    main()
