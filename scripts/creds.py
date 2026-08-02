#!/usr/bin/env python3
"""
Unified credential helper for all scripts.
Consolidates vault.db, .secrets file, and env var access into one interface.

Usage:
    from creds import get_cred

    # WordPress credentials
    wp = get_cred('wordpress', 'aitoolalliance')  # returns dict with url, user, pass

    # NAS credentials
    nas = get_cred('nas', 'password')

    # Simple key
    api_key = get_cred('upload_post', 'api_key')

    # Check if exists
    has_it = has_cred('plaid', 'client_id')
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional

WORKSPACE = Path("C:/Users/compj/.openclaw/workspace")
VAULT_PATH = WORKSPACE / "scripts" / "credentials" / "vault.db"
SECRETS_PATH = WORKSPACE / ".secrets"

# Cache for .secrets file to avoid re-reading
_secrets_cache = None


def _load_secrets() -> dict:
    """Load and cache the .secrets file."""
    global _secrets_cache
    if _secrets_cache is not None:
        return _secrets_cache

    _secrets_cache = {}
    if SECRETS_PATH.exists():
        for line in SECRETS_PATH.read_text(encoding='utf-8').strip().split('\n'):
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                _secrets_cache[key.strip()] = value.strip()
    return _secrets_cache


def _get_from_vault(service: str, key: str) -> Optional[str]:
    """Try to get a credential from the SQLite vault."""
    if not VAULT_PATH.exists():
        return None
    try:
        conn = sqlite3.connect(str(VAULT_PATH))
        row = conn.execute(
            "SELECT value FROM credentials WHERE service = ? AND key = ?",
            (service, key)
        ).fetchone()
        conn.close()
        return row[0] if row else None
    except Exception:
        return None


def _get_from_env(key: str) -> Optional[str]:
    """Try to get a credential from environment variables."""
    # Try exact key, then uppercased, then with underscores
    for variant in [key, key.upper(), key.replace('-', '_'), key.upper().replace('-', '_')]:
        val = os.environ.get(variant)
        if val:
            return val
    return None


def get_cred(service: str, key: str, default: Optional[str] = None) -> str:
    """Get a credential from vault, .secrets, or env vars.

    Search order: vault.db -> .secrets file -> env vars -> default

    Raises KeyError if not found and no default provided.
    """
    # 1. Try vault.db
    val = _get_from_vault(service, key)
    if val is not None:
        return val

    # 2. Try .secrets file
    secrets = _load_secrets()
    # Try service/key format first
    secrets_key = f"{service}_{key}"
    if secrets_key in secrets:
        return secrets[secrets_key]
    # Try just the key
    if key in secrets:
        return secrets[key]
    # Try common aliases
    aliases = {
        'password': ['pass', 'pwd'],
        'user': ['username', 'login'],
        'url': ['host', 'endpoint'],
        'hostname': ['host'],
    }
    for main_key, alts in aliases.items():
        if key == main_key or key in alts:
            for alt in [main_key] + alts:
                if f"{service}_{alt}" in secrets:
                    return secrets[f"{service}_{alt}"]
                if alt in secrets:
                    return secrets[alt]

    # 3. Try env vars
    val = _get_from_env(f"{service}_{key}")
    if val is not None:
        return val

    # 4. Default
    if default is not None:
        return default

    raise KeyError(f"Credential not found: {service}/{key} (checked vault, .secrets, env vars)")


def has_cred(service: str, key: str) -> bool:
    """Check if a credential exists without raising."""
    try:
        get_cred(service, key)
        return True
    except KeyError:
        return False


def get_wp_site(site_key: str) -> dict:
    """Get all WordPress credentials for a site as a dict.

    Returns: {'url': str, 'user': str, 'pass': str}
    Raises KeyError if any credential is missing.
    """
    return {
        'url': get_cred('wordpress', f'{site_key}_url'),
        'user': get_cred('wordpress', f'{site_key}_user'),
        'pass': get_cred('wordpress', f'{site_key}_pass'),
    }


def get_wp_auth_header(site_key: str) -> dict:
    """Get WordPress Basic Auth headers for a site.

    Returns: {'Authorization': 'Basic ...', 'User-Agent': '...', 'Accept': '...', 'Content-Type': '...'}
    """
    import base64
    site = get_wp_site(site_key)
    auth_str = base64.b64encode(f"{site['user']}:{site['pass']}".encode()).decode()
    return {
        'Authorization': f'Basic {auth_str}',
        'User-Agent': 'ContentNovaBot/2.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }


def list_services() -> dict:
    """List all available credential services and their keys.

    Returns: {'vault': {service: [keys]}, 'secrets': [keys]}
    """
    result = {'vault': {}, 'secrets': []}

    if VAULT_PATH.exists():
        conn = sqlite3.connect(str(VAULT_PATH))
        rows = conn.execute(
            "SELECT service, key FROM credentials ORDER BY service, key"
        ).fetchall()
        conn.close()
        for service, key in rows:
            result['vault'].setdefault(service, []).append(key)

    secrets = _load_secrets()
    result['secrets'] = list(secrets.keys())

    return result


if __name__ == "__main__":
    import sys
    if '--list-services' in sys.argv:
        services = list_services()
        print("=== Vault ===")
        for service, keys in sorted(services['vault'].items()):
            print(f"  {service}: {', '.join(keys)}")
        print("\n=== .secrets ===")
        for key in services['secrets']:
            print(f"  {key}")
        sys.exit(0)

    if len(sys.argv) < 3:
        print("Usage: python creds.py <service> <key> [--list]")
        print("       python creds.py --list-services")
        print()
        print("Examples:")
        print("  python creds.py wordpress aitoolalliance_url")
        print("  python creds.py nas password")
        print("  python creds.py --list-services")
        sys.exit(1)

    service = sys.argv[1]
    key = sys.argv[2]
    try:
        val = get_cred(service, key)
        # Mask most of the value for security
        if len(val) > 8:
            print(f"{service}/{key} = {val[:3]}...{val[-3:]}")
        else:
            print(f"{service}/{key} = [found, {len(val)} chars]")
    except KeyError as e:
        print(f"NOT FOUND: {e}")
        sys.exit(1)