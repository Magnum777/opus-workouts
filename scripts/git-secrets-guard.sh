#!/usr/bin/env bash
# Pre-commit hook: Block commits containing hardcoded secrets
# Install: cp scripts/git-secrets-guard.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

set -euo pipefail

# Patterns that indicate hardcoded secrets
FORBIDDEN_PATTERNS=(
    # Plaid credentials
    'PLAID_[A-Z_]*SECRET\s*='
    'api_key.*clientId.*secret'
    # WordPress passwords
    "'pass':\s*'[^']+'"
    'APP_PASSWORD.*=.*"[^"]+"'
    'APP_PASSWORD.*=.*\047[^\047]+\047'
    # API keys/tokens (generic)
    'api[_-]?key\s*=\s*["\047][a-zA-Z0-9_-]{16,}["\047]'
    'api[_-]?secret\s*=\s*["\047][a-zA-Z0-9_-]{16,}["\047]'
    'password\s*=\s*["\047][^"\047]{8,}["\047]'
    'token\s*=\s*["\047][a-zA-Z0-9_-]{20,}["\047]'
    ***REMOVED*** pattern
    'MT[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{20,}'
    # Email app passwords (Google style)
    '[a-z]{4}\s+[a-z]{4}\s+[a-z]{4}\s+[a-z]{4}\s+[a-z]{4}\s+[a-z]{4}'
)

BLOCKED=0
FILES=$(git diff --cached --name-only --diff-filter=ACM)

for file in $FILES; do
    # Skip binary files and lock files
    [[ "$file" =~ \.(jpg|jpeg|png|gif|pdf|zip|lock|jsonl|pyc)$ ]] && continue
    [[ "$file" =~ node_modules/ ]] && continue
    [[ "$file" =~ venv/ ]] && continue
    [[ "$file" =~ \.git/ ]] && continue

    for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
        if git diff --cached -U0 -- "$file" | grep -iE "$pattern" > /dev/null 2>&1; then
            echo "ERROR: Potential secret detected in $file"
            echo "       Pattern matched: $pattern"
            echo "       Move credentials to env files or use os.environ.get()"
            BLOCKED=1
        fi
    done
done

if [ $BLOCKED -eq 1 ]; then
    echo ""
    echo "Commit blocked. Fix the secrets above before committing."
    echo "Allowed patterns: os.environ.get('VAR_NAME') or .env files"
    exit 1
fi

exit 0
