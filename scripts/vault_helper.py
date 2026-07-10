"""Helper to load credentials from the local SQLite vault.

Usage:
    from vault_helper import get_credential

    client_id = get_credential('plaid', 'client_id')
    secret = get_credential('plaid', 'secret')
"""

import sqlite3
from pathlib import Path

VAULT_PATH = Path(__file__).parent / "credentials" / "vault.db"


def get_credential(service: str, key: str) -> str:
    """Retrieve a credential from the vault. Raises if not found."""
    if not VAULT_PATH.exists():
        raise FileNotFoundError(f"Vault not found: {VAULT_PATH}")
    
    conn = sqlite3.connect(VAULT_PATH)
    row = conn.execute(
        "SELECT value FROM credentials WHERE service = ? AND key = ?",
        (service, key)
    ).fetchone()
    conn.close()
    
    if not row:
        raise KeyError(f"Credential not found: {service}/{key}")
    
    return row[0]
