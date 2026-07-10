#!/usr/bin/env python3
"""
Backup finance data to Synology NAS.

Run manually or via cron. Uses SSH/SCP to copy finance-related files
from the local workspace to the NAS backup directory.
"""

import logging
import subprocess
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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


def run_ssh_command(cmd: str) -> None:
    """Run a command on the NAS via SSH."""
    subprocess.run(["ssh", f"{NAS_USER}@{NAS_HOST}", cmd], check=True)


def copy_to_nas(src: Path, dest_dir: str) -> None:
    """Copy a file or directory to the NAS via SCP."""
    dest = f"{NAS_USER}@{NAS_HOST}:{dest_dir}/"
    if src.is_dir():
        subprocess.run(["scp", "-r", str(src), dest], check=True)
    else:
        subprocess.run(["scp", str(src), dest], check=True)


def main() -> None:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = f"{NAS_PATH}/{timestamp}"

    logger.info("Backing up to %s:%s", NAS_HOST, backup_dir)

    # Create remote dir via SSH
    run_ssh_command(f"mkdir -p {backup_dir}")

    # Copy each item
    for item in BACKUP_ITEMS:
        src = LOCAL_DIR / item
        if src.exists():
            try:
                copy_to_nas(src, backup_dir)
                logger.info("  [OK] %s", item)
            except subprocess.CalledProcessError as e:
                logger.error("  [FAIL] %s: %s", item, e)
        else:
            logger.warning("  [MISSING] %s", item)

    # Update latest symlink
    try:
        run_ssh_command(f"ln -sfn {backup_dir} {NAS_PATH}/latest")
        logger.info("Done. Latest: %s:%s/latest", NAS_HOST, NAS_PATH)
    except subprocess.CalledProcessError as e:
        logger.error("Failed to update latest symlink: %s", e)


if __name__ == "__main__":
    main()
