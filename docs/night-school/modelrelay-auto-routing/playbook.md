# Modelrelay Auto-Routing Playbook

## Overview

**Topic:** Modelrelay Auto-Routing Integration  
**Research Date:** February 26, 2026  
**Goal:** Determine if modelrelay should be integrated into OpenClaw's fallback system

---

## What is Modelrelay?

**Modelrelay** is a local OpenAI-compatible router that:
- Benchmarks free coding models across multiple providers
- Automatically forwards requests to the fastest available model
- Compatible with OpenCode and OpenClaw
- Runs locally (API keys stay on your machine)

### Supported Providers (Free Tier)

| Provider | Env Variable | Notes |
|----------|--------------|-------|
| NVIDIA NIM | `NVIDIA_API_KEY` | High quality, limited rate limits |
| Groq | `GROQ_API_KEY` | Very fast inference |
| Cerebras | `CEREBRAS_API_KEY` | Extremely fast, generous limits |
| SambaNova | `SAMBANOVA_API_KEY` | Good for coding tasks |
| OpenRouter | `OPENROUTER_API_KEY` | Access to many free models |
| Hyperbolic | `HYPERBOLIC_API_KEY` | Free tier available |
| Scaleway | `SCALEWAY_API_KEY` | European provider |
| Google | `GOOGLE_API_KEY` | Gemini models |

---

## How It Works

1. **Install:** `npm install -g modelrelay`
2. **Onboard:** `modelrelay onboard` - saves API keys for chosen providers
3. **Start:** `modelrelay` - starts local router on port 7352
4. **Use:** Point OpenClaw to `http://127.0.0.1:7352/v1` with any API key

### Auto-Configuration

Modelrelay can auto-configure OpenClaw during onboarding, or you can manually merge this into `~/.openclaw/openclaw.json`:

```json
{
  "models": {
    "providers": {
      "modelrelay": {
        "baseUrl": "http://127.0.0.1:7352/v1",
        "api": "openai-completions",
        "apiKey": "no-key",
        "models": [
          { "id": "auto-fastest", "name": "Auto Fastest" }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "modelrelay/auto-fastest"
      }
    }
  }
}
```

---

## Pros

- ✅ **Zero cost** - Uses free tier APIs
- ✅ **Automatic failover** - Switches providers on rate limits
- ✅ **Local execution** - API keys never leave your machine
- ✅ **Benchmarking** - Automatically finds fastest provider
- ✅ **OpenAI compatible** - Easy integration with OpenClaw
- ✅ **Autostart support** - Can run as background service

---

## Cons

- ❌ **Requires API keys** - Need to sign up for multiple free tier services
- ❌ **Free tier volatility** - Rate limits change, models disappear
- ❌ **Setup complexity** - Multiple provider accounts to manage
- ❌ **No quality routing** - Routes by speed, not task fit
- ❌ **npm dependency** - Requires Node.js

---

## Alternatives

### OpenRouter Built-in Routers
- **Free Models Router** (`openrouter/free`) - Random free model selection
- **Auto Router** (`openrouter/auto`) - NotDiamond-powered smart selection

### NVIDIA NIM
- Local deployment option
- Higher quality but requires more setup

---

## Integration Recommendation

### FOR Nova's Setup: **YES - Integrate**

**Rationale:**
1. **Cost savings** - Complements existing MiniMax/Grok setup for simple tasks
2. **Fallback resilience** - If rate limited, automatically tries next provider
3. **Fast routing** - Good for quick coding tasks (file edits, simple queries)
4. **Op already uses OpenClaw** - Direct compatibility

### Implementation Plan

1. **Phase 1: Core Providers**
   - Get Cerebras API key (fastest, most generous)
   - Get Groq API key (backup for speed)
   - Install and configure modelrelay

2. **Phase 2: OpenClaw Integration**
   - Add modelrelay provider config
   - Set as secondary/fallback model

3. **Phase 3: Testing**
   - Test failover behavior
   - Benchmark vs current free options (Ollama)

### Quick Start Commands

```bash
# Install
npm install -g modelrelay

# Onboard (will prompt for API keys)
modelrelay onboard

# Start router
modelrelay

# Or install autostart
modelrelay install --autostart
```

---

## Key Findings Summary

| Finding | Value |
|---------|-------|
| Does it work? | ✅ Yes, actively maintained |
| Cost | Free (requires API key signups) |
| Difficulty | Easy (npm install + keys) |
| Reliability | Medium (depends on free tier availability) |
| Best for | Simple coding tasks, fallbacks |
| Recommendation | Integrate as secondary/fallback |

---

## Resources

- GitHub: https://github.com/ellipticmarketing/modelrelay
- Free Models: https://openrouter.ai/collections/free-models
- Cerebras Rate Limits: https://inference-docs.cerebras.ai/support/rate-limits
