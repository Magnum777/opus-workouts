# Airlock Design - Secure Testing Environment

## Overview

**Airlock** is a hardened sandbox environment for testing agents new skills,, and configurations safely before deploying to the main Nova instance.

## Why Airlock?

- Prevent compromised skills from accessing credentials
- Test unknown skills in isolation
- Validate skill integrity before production use
- Safe experimentation environment

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MAIN NOVA                             │
│                  (Production)                           │
│  - Full credentials                                   │
│  - All channels                                      │
│  - Production data                                   │
└─────────────────────────────────────────────────────────┘
                          │
                    [Firewall]
                          │
┌─────────────────────────────────────────────────────────┐
│                    AIRLOCK                              │
│                  (Sandbox)                             │
│  - No credentials                                     │
│  - Limited channels (test Discord only)               │
│  - Synthetic/test data                               │
│                                                         │
│  ┌─────────────────┐  ┌─────────────────┐            │
│  │  Airlock-Nova   │  │ Airlock-Sentinel│            │
│  │  (Test Agent)   │  │  (Monitoring)  │            │
│  └─────────────────┘  └─────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. Airlock Workspace

Separate OpenClaw workspace:
- Location: `C:\Users\compj\.openclaw-airlock\`
- No access to main credentials
- Test API keys only
- Configured via environment variables

### 2. Airlock-Nova

Test agent instance:
- Spawned on demand for testing
- No persistent memory (starts fresh each time)
- Limited tool access
- Logs everything for review

### 3. Airlock-Sentinel

Monitoring sub-mind:
- Watches Airlock-Nova behavior
- Detects anomalies
- Alerts on suspicious activity
- Reports to main Nova

## Security Rules

| Rule | Description |
|------|-------------|
| **No Credentials** | Airlock cannot access CREDENTIALS.md |
| **Channel Limits** | Only test Discord channel |
| **Network Isolation** | Limited external access |
| **Auto-Wipe** | Reset after each test session |
| **Logging** | Every action logged for review |

## Implementation

### Setup

```bash
# Create separate workspace
mkdir C:\Users\compj\.openclaw-airlock
cp C:\Users\compj\.openclaw\openclaw.json C:\Users\compj\.openclaw-airlock\

# Modify config
# - Remove credentials references
# - Add test-only API keys
# - Restrict channels
```

### Test Workflow

```
1. Skill developer shares new skill
2. Upload to Airlock workspace
3. Start Airlock-Nova with skill
4. Run test scenarios
5. Airlock-Sentinel reviews behavior
6. If safe: deploy to main
7. If suspicious: flag for review
```

### Validation Checklist

- [ ] No credential access attempts
- [ ] No external data exfiltration
- [ ] Expected tool behavior
- [ ] No prompt injection
- [ ] Clean shutdown/reset

## Prompt-Guard Integration

Airlock pairs with prompt-guard for defense:

| Layer | Protection |
|-------|------------|
| **Input** | Scan all incoming prompts for injection |
| **Output** | Verify agent responses |
| **Actions** | Block dangerous tool calls |
| **Memory** | Prevent memory poisoning |

## Use Cases

1. **New Skills** - Test ClawHub skills before installing
2. **Untrusted Code** - Run unverified scripts safely
3. **Experiment** - Try new agent configurations
4. **Debug** - Isolate problematic behavior

## For V3 Enterprise Customers

Airlock is included in V3 Enterprise ($100+):

- Pre-configured Airlock workspace
- prompt-guard integration
- Sentinel monitoring
- Custom test scenarios
- Priority support

## Commands

```bash
# Start Airlock session
/session_spawn task="Test new skill" label="airlock-test"

# Run Sentinel
/session_spawn task="Monitor Airlock-Nova" label="airlock-sentinel"

# Manual reset
rm -rf C:\Users\compj\.openclaw-airlock\memory\
```

## Future Enhancements

- Docker containerization
- Network traffic monitoring
- Automated behavior testing
- Multi-persona validation

---

*Last Updated: 2026-02-17*
