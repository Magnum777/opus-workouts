#!/usr/bin/env python3
"""Secure local credential vault using SQLite.

Usage:
    python credential_vault.py set <service> <key> <value>
    python credential_vault.py get <service> <key>
    python credential_vault.py list <service>
    python credential_vault.py delete <service> <key>
"""

import argparse
import logging
import os
import sqlite3
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VAULT_PATH = Path(__file__).parent / "credentials" / "vault.db"


def init_db():
    """Create the credentials table if it doesn't exist."""
    VAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(VAULT_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS credentials (
            service TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (service, key)
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Vault initialized: %s", VAULT_PATH)


def set_credential(service: str, key: str, value: str) -> None:
    """Store or update a credential."""
    init_db()
    conn = sqlite3.connect(VAULT_PATH)
    conn.execute(
        "INSERT INTO credentials (service, key, value) VALUES (?, ?, ?) "
        "ON CONFLICT(service, key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP",
        (service, key, value)
    )
    conn.commit()
    conn.close()
    logger.info("Stored: %s/%s", service, key)


def get_credential(service: str, key: str) -> str | None:
    """Retrieve a credential. Returns None if not found."""
    init_db()
    conn = sqlite3.connect(VAULT_PATH)
    row = conn.execute(
        "SELECT value FROM credentials WHERE service = ? AND key = ?",
        (service, key)
    ).fetchone()
    conn.close()
    return row[0] if row else None


def list_credentials(service: str) -> list[tuple]:
    """List all keys for a service."""
    init_db()
    conn = sqlite3.connect(VAULT_PATH)
    rows = conn.execute(
        "SELECT key, updated_at FROM credentials WHERE service = ? ORDER BY key",
        (service,)
    ).fetchall()
    conn.close()
    return rows


def delete_credential(service: str, key: str) -> None:
    """Delete a credential."""
    init_db()
    conn = sqlite3.connect(VAULT_PATH)
    conn.execute("DELETE FROM credentials WHERE service = ? AND key = ?", (service, key))
    conn.commit()
    conn.close()
    logger.info("Deleted: %s/%s", service, key)


def main() -> int:
    parser = argparse.ArgumentParser(description="Secure credential vault")
    parser.add_argument("action", choices=["set", "get", "list", "delete"])
    parser.add_argument("service", help="Service name (e.g., plaid, wordpress)")
    parser.add_argument("key", nargs="?", help="Credential key")
    parser.add_argument("value", nargs="?", help="Credential value (for set)")
    args = parser.parse_args()

    if args.action == "set":
        if not args.key or not args.value:
            logger.error("Usage: set <service> <key> <value>")
            return 1
        set_credential(args.service, args.key, args.value)
    elif args.action == "get":
        if not args.key:
            logger.error("Usage: get <service> <key>")
            return 1
        value = get_credential(args.service, args.key)
        if value is None:
            logger.error("Credential not found: %s/%s", args.service, args.key)
            return 1
        print(value)
    elif args.action == "list":
        rows = list_credentials(args.service)
        if not rows:
            print(f"No credentials found for service: {args.service}")
        for key, updated in rows:
            print(f"{key} (updated: {updated})")
    elif args.action == "delete":
        if not args.key:
            logger.error("Usage: delete <service> <key>")
            return 1
        delete_credential(args.service, args.key)

    return 0


if __name__ == "__main__":
    sys.exit(main())
