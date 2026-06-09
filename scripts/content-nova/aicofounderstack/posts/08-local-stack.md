# My AI Runs on $0 Compute: The Local Stack That Powers Everything

**Author:** James "Opus" Henderson  
**Date:** June 2026  
**Tags:** Local AI, Ollama, AMD, GPU, Cost Optimization

---

## The Cloud Tax

Running everything on cloud APIs adds up fast:
- GPT-4: $30/month for moderate usage
- Claude 3.5: $20/month  
- Cloud hosting: $15-50/month
- API quotas: anxiety-inducing

I pay $0 for compute. Here's how.

## The Hardware

**Desktop:** Custom build, ~$2,500 total
- AMD Ryzen 9800X3D (16 cores, 32 threads)
- Radeon 9070 XT (32 GB VRAM)
- 32 GB DDR5 RAM
- 2 TB NVMe SSD
- Windows 10 (not Linux — I like things that work)

**Why AMD over NVIDIA?**
- 32 GB VRAM for $800 vs. 24 GB for $1,200 (RTX 4090)
- DirectML support for PyTorch (not as mature as CUDA, but functional)
- No vendor lock-in

## What Runs Locally

**LLMs (Ollama):**
| Model | Size | VRAM | Use Case |
|-------|------|------|----------|
| Kimi K2.5 | 32B | ~24 GB | Premium reasoning |
| Qwen3:14b | 14B | ~10 GB | Fast classification |
| Qwen3:30b | 30B | ~20 GB | Balanced writing |
| nomic-embed-text | 137M | ~1 GB | Embeddings |

**All models load in under 10 seconds. First token appears in 2-5 seconds.**

**Image Generation (ComfyUI):**
- Stable Diffusion v1.5 via DirectML
- 512x512 image in ~8 seconds
- 1024x1024 in ~25 seconds
- Not as fast as CUDA, but free

**Vector Database (LanceDB):**
- Local storage, no server
- 200ms queries for semantic search
- 54 playbooks, 31K words, zero hosting cost

**Code Execution:**
- Python 3.14 (bleeding edge, because I like problems)
- Node.js for web servers
- Everything runs on the same machine

## What Still Needs Cloud

Not everything can be local:

**Web Search:** Perplexity API ($0.002/query) — local models can't browse the web
**Solana RPC:** Helius free tier — need a reliable node
**Discord Bot:** Runs on OpenClaw Gateway (local, but needs internet)
**WordPress Hosting:** $15/month for 3 sites — can't self-host from home IP

**Total cloud costs: ~$20/month** vs. $100+ if everything was cloud-based.

## The Real Savings

| Category | Cloud-First Cost | Local-First Cost | Savings |
|----------|------------------|------------------|---------|
| LLM compute | $40-60/month | $0 | 100% |
| Image generation | $20-50/month (Midjourney/DALL-E) | $0 | 100% |
| Vector DB | $15-30/month (Pinecone/Weaviate) | $0 | 100% |
| Code execution | $10-20/month (cloud runners) | $0 | 100% |
| **Total** | **$85-160/month** | **$20/month** | **75-90%** |

The $2,500 hardware pays for itself in 15-30 months. And I own it — no API deprecation, no rate limit changes, no vendor lock-in.

## The Tradeoffs

**Slower than cloud for some tasks**
Qwen3:14b is fast, but Kimi K2.5 on local hardware is slower than the cloud version. For time-critical tasks (trading execution), I use cloud. For everything else, local is fine.

**Setup complexity**
Ollama makes it easy, but DirectML on AMD is still rough. ComfyUI needed manual patches. Not as plug-and-play as "sign up for OpenAI API."

**Power consumption**
The GPU draws ~300W under load. At Georgia power rates (~$0.12/kWh), running 8 hours/day costs ~$10/month in electricity. Still cheaper than cloud.

**No automatic scaling**
If I need to run 10 models simultaneously, I can't just "add more instances." Hardware limits are real.

## What's Next

1. **Second GPU** — Adding an RX 7900 XTX for parallel model hosting (24 GB more VRAM)
2. **Linux dual-boot** — ROCm (AMD's CUDA equivalent) has better support on Linux
3. **NAS offload** — Move LanceDB and file storage to the Synology NAS to free up local disk

## The Bottom Line

Local AI isn't for everyone. If you need 99.9% uptime, auto-scaling, or enterprise SLAs, cloud makes sense.

But for a solo operator running personal automations? Local is a no-brainer. The models are good enough. The hardware is affordable. And the freedom from API quotas and vendor whims is worth the setup hassle.

**My monthly AI compute bill: $20.** That covers web search, Solana RPC, and WordPress hosting. Everything else runs on silicon I own.

**Want the setup guide?** I'll include the full local stack configuration in the Nova Operations blueprint — Ollama model configs, DirectML setup, and hardware recommendations.

---

*This is not anti-cloud. This is pro-ownership. I use cloud where it makes sense (web search, hosting). I use local where it makes sense (LLMs, images, databases). The trick is knowing which is which.*
