# My AI Published 90 Articles Last Month: The Content Nova Pipeline

**Author:** James "Opus" Henderson  
**Date:** May 28, 2026  
**Tags:** AI, Content Automation, WordPress, SEO, n8n

---

## The Numbers

Last month, an AI agent published 90 articles across three WordPress sites. I wrote zero of them. I approved zero of them. I only checked the analytics afterward.

Here's the breakdown:

| Site | Articles | Avg Words | Total Words | Featured Images |
|------|----------|-----------|-------------|-----------------|
| aitoolalliance.com | 32 | 1,200 | 38,400 | 32 |
| aibusinessinsider.org | 31 | 1,100 | 34,100 | 31 |
| aicofounderstack.com | 27 | 1,300 | 35,100 | 27 |
| **Total** | **90** | **1,200** | **107,600** | **90** |

Every article has:
- Real research (web search for current topics)
- SEO optimization (keywords, meta descriptions, categories)
- Featured image (Unsplash stock photo, relevant to topic)
- Internal linking (cross-links between posts)
- Published at optimal time (2-4 AM ET when traffic is lowest)

## The Pipeline

This is not "ChatGPT writes a blog post." This is a multi-stage production pipeline:

### Stage 1: Research (5 min)
- Web search for trending AI/business topics
- Scrape competitor headlines for gap analysis
- Pick a topic with search volume but low competition

### Stage 2: Writing (8 min)
- AI drafts 1,200-word article with:
  - H2/H3 structure
  - Bullet points and tables
  - Call to action at the end
  - Affiliate link mentions where natural
- Self-edit pass: check readability, remove fluff, verify facts

### Stage 3: Media (3 min)
- Search Unsplash for relevant stock image
- Download, resize, upload to WordPress Media Library
- Set as featured image

### Stage 4: Publishing (2 min)
- Create WordPress post via REST API
- Set category, tags, SEO meta
- Schedule for optimal time
- Report to Discord with link and stats

**Total pipeline time: ~18 minutes per article.** Running on a $0 compute budget (Ollama local models).

## The Tech Stack

**Research:** Web search via OpenClaw + Perplexity API  
**Writing:** Kimi K2.5 (cloud) for quality, Qwen3:14b (local) for speed  
**Images:** Unsplash API (free) for stock photos  
**Publishing:** WordPress REST API with application passwords  
**Scheduling:** Cron jobs at 2 AM, 3 AM, 4 AM ET (staggered to avoid overlap)  
**Reporting:** Discord webhook to #wordpress channel

## What Actually Works

**Staggered timing prevents crashes.** Three sites publishing simultaneously used to overload the WordPress server. Now they're spaced 1 hour apart — zero failures in 30 days.

**Featured images matter.** Posts with images get 2.3x more social shares. Unsplash integration was the highest-ROI addition to the pipeline.

**Model tiering saves money.** Using Qwen3:14b (local, free) for first drafts and Kimi K2.5 (cloud, ~$0.002/1K tokens) for final polish cuts costs by 70% vs. running everything on premium models.

**Self-healing is critical.** The pipeline has retry logic for:
- WordPress API timeouts (3 retries with backoff)
- Image download failures (fallback to related search terms)
- Model hallucinations (fact-check pass against source material)

## What's Still Broken

**Internal links are manual.** The bot can't reliably determine which existing post is most relevant to link to. I still add 2-3 internal links per post by hand. Working on semantic similarity matching via LanceDB.

**Affiliate links are sparse.** Only 12 of 90 posts included natural affiliate mentions. Need better integration between content research and affiliate product matching.

**No A/B testing.** Headlines are whatever the AI generates first. No testing for CTR. Need a headline variation generator + analytics feedback loop.

## The Economics

| Item | Cost |
|------|------|
| WordPress hosting (3 sites) | $15/month |
| Ollama compute (local) | $0 |
| Cloud model usage (Kimi) | ~$8/month |
| Unsplash API | $0 |
| Domain names | $36/year |
| **Total monthly** | **~$35** |

**Output:** 90 articles/month = ~$0.39 per article. Including research, writing, images, and publishing.

For comparison: a human writer on Upwork charges $50-200 per 1,200-word article. Even Fiverr writers charge $20-40. The AI pipeline is 50-500x cheaper.

## What's Next

1. **Headline A/B testing** — Generate 3 headlines per post, track CTR for 24h, pick winner
2. **Affiliate integration** — Match content topics to affiliate products automatically
3. **Repurposing** — Turn top-performing posts into Twitter threads, LinkedIn carousels, email newsletters
4. **Video scripts** — Use top posts as source material for YouTube Shorts scripts

## Try It Yourself

The full pipeline is available as a downloadable automation ($49). Includes:
- WordPress publisher script
- Topic research engine
- AI article generator with prompts
- Unsplash image integration
- Cron configuration
- Discord reporting setup

Or build your own — the components are all open:
- WordPress REST API docs
- Ollama for local LLMs
- Unsplash API (free tier)
- Any cron scheduler

---

**Questions?** Reply here or DM me on Discord. I read everything.

*This is not content marketing theory. This is a real pipeline publishing real articles to real sites with real traffic. The numbers are from my actual dashboard.*
