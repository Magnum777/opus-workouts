#!/usr/bin/env python3
"""
Backup finance data to Synology NAS.

Run manually or via cron. Prefers SMB (reliable) over SSH/SCP (often hangs).
Falls back to SMB copy if SSH is unavailable.
"""

import logging
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

NAS_HOST = "MND"
NAS_USER = "Nova"


def _load_nas_password():
    """Load NAS password from .secrets file ([nas] section)."""
    secrets_path = Path(__file__).resolve().parent.parent / ".secrets"
    try:
        with open(secrets_path, "r") as f:
            in_nas = False
            for line in f:
                line = line.strip()
                if line == "[nas]":
                    in_nas = True
                    continue
                if line.startswith("[") and line.endswith("]"):
                    in_nas = False
                    continue
                if in_nas and line.startswith("password="):
                    return line.split("=", 1)[1]
    except Exception as e:
        print(f"WARN: Failed to load NAS password from .secrets: {e}", file=sys.stderr)
    return os.environ.get("NAS_PASSWORD", "")

NAS_PASS = _load_nas_password()
NAS_SSH_PATH = "/volume1/homes/Nova/nova-backups/finance"
NAS_SMB_PATH = "\\\\MND\\home\\Nova\\nova-backups\\finance"
LOCAL_DIR = Path("C:/Users/compj/.openclaw/workspace")
SSH_TIMEOUT = 10  # seconds — fail fast if SSH hangs

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


def ssh_available() -> bool:
    """Quick check if SSH responds within timeout."""
    try:
        result = subprocess.run(
            ["ssh", "-o", f"ConnectTimeout={SSH_TIMEOUT}", "-o", "BatchMode=yes",
             f"{NAS_USER}@{NAS_HOST}", "echo ok"],
            capture_output=True, text=True, timeout=SSH_TIMEOUT + 2
        )
        return result.returncode == 0 and "ok" in result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def run_ssh_command(cmd: str) -> None:
    """Run a command on the NAS via SSH with timeout."""
    subprocess.run(
        ["ssh", "-o", f"ConnectTimeout={SSH_TIMEOUT}", f"{NAS_USER}@{NAS_HOST}", cmd],
        check=True, timeout=SSH_TIMEOUT + 5
    )


def copy_via_scp(src: Path, dest_dir: str) -> None:
    """Copy a file or directory to the NAS via SCP."""
    dest = f"{NAS_USER}@{NAS_HOST}:{dest_dir}/"
    if src.is_dir():
        subprocess.run(
            ["scp", "-o", f"ConnectTimeout={SSH_TIMEOUT}", "-r", str(src), dest],
            check=True, timeout=300
        )
    else:
        subprocess.run(
            ["scp", "-o", f"ConnectTimeout={SSH_TIMEOUT}", str(src), dest],
            check=True, timeout=60
        )


def ensure_smb_dir(path: Path) -> None:
    """Ensure directory exists via SMB path."""
    path.mkdir(parents=True, exist_ok=True)


def copy_via_smb(src: Path, dest_dir: Path) -> None:
    """Copy a file or directory via SMB (network path)."""
    if src.is_dir():
        dest = dest_dir / src.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    else:
        shutil.copy2(src, dest_dir)


def smb_backup(timestamp: str) -> tuple[int, int]:
    """Perform backup via SMB. Returns (files_backed_up, total_bytes)."""
    backup_dir = Path(NAS_SMB_PATH) / timestamp
    ensure_smb_dir(backup_dir)

    files_backed = 0
    total_bytes = 0

    for item in BACKUP_ITEMS:
        src = LOCAL_DIR / item
        if not src.exists():
            logger.warning("  [MISSING] %s", item)
            continue
        try:
            copy_via_smb(src, backup_dir)
            size = src.stat().st_size if src.is_file() else sum(
                f.stat().st_size for f in src.rglob("*") if f.is_file()
            )
            files_backed += 1
            total_bytes += size
            logger.info("  [OK] %s (%s bytes)", item, size)
        except Exception as e:
            logger.error("  [FAIL] %s: %s", item, e)

    # Update latest symlink by writing a marker file
    latest_marker = Path(NAS_SMB_PATH) / "latest.txt"
    try:
        latest_marker.write_text(str(backup_dir), encoding="utf-8")
    except Exception as e:
        logger.error("Failed to write latest marker: %s", e)

    return files_backed, total_bytes


def ssh_backup(timestamp: str) -> tuple[int, int]:
    """Perform backup via SSH/SCP. Returns (files_backed_up, total_bytes)."""
    backup_dir = f"{NAS_SSH_PATH}/{timestamp}"
    run_ssh_command(f"mkdir -p {backup_dir}")

    files_backed = 0
    total_bytes = 0

    for item in BACKUP_ITEMS:
        src = LOCAL_DIR / item
        if not src.exists():
            logger.warning("  [MISSING] %s", item)
            continue
        try:
            copy_via_scp(src, backup_dir)
            size = src.stat().st_size if src.is_file() else sum(
                f.stat().st_size for f in src.rglob("*") if f.is_file()
            )
            files_backed += 1
            total_bytes += size
            logger.info("  [OK] %s (%s bytes)", item, size)
        except subprocess.CalledProcessError as e:
            logger.error("  [FAIL] %s: %s", item, e)

    # Update latest symlink
    try:
        run_ssh_command(f"ln -sfn {backup_dir} {NAS_SSH_PATH}/latest")
    except subprocess.CalledProcessError as e:
        logger.error("Failed to update latest symlink: %s", e)

    return files_backed, total_bytes


def main() -> dict:
    """Run backup. Returns result dict for cron reporting."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    logger.info("Starting finance backup at %s", timestamp)

    # Test SSH first, but with short timeout
    use_ssh = ssh_available()
    method = "SSH" if use_ssh else "SMB"
    logger.info("Using %s method (SSH available: %s)", method, use_ssh)

    try:
        if use_ssh:
            files_backed, total_bytes = ssh_backup(timestamp)
        else:
            files_backed, total_bytes = smb_backup(timestamp)

        logger.info("Done. Files: %d, Total: %d bytes", files_backed, total_bytes)
        return {
            "status": "success",
            "method": method,
            "timestamp": timestamp,
            "files_backed_up": files_backed,
            "total_bytes": total_bytes,
        }
    except Exception as e:
        logger.error("Backup failed: %s", e)
        return {
            "status": "failure",
            "method": method,
            "timestamp": timestamp,
            "error": str(e),
        }


if __name__ == "__main__":
    import json
    result = main()
    print(json.dumps(result, indent=2))
