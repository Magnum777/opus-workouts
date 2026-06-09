# RSS Reader Integration - Night School Playbook

## Overview

RSS (Really Simple Syndication) enables automated content monitoring from blogs, news sites, and newsletters. For the AI Co-Founder Stack, RSS feeds provide a continuous stream of industry content for research, content creation, and competitive intelligence.

## Use Cases

1. **Content Discovery** - Monitor industry blogs for trending topics
2. **Competitive Intelligence** - Track competitor announcements
3. **News Aggregation** - Stay informed on AI/tech news
4. **Newsletter Harvesting** - Capture curated content from trusted sources
5. **AI Feeding** - Supply LLM pipelines with fresh content

---

## Implementation Options

### Option 1: Python Script (Recommended for OpenClaw)

**Libraries:**
- `feedparser` - Most mature RSS/Atom parser (PyPI: feedparser)
- `rss-parser` - Alternative with different API (PyPI: rss-parser)

**Basic Implementation:**
```python
import feedparser
import json
from datetime import datetime

def fetch_feed(url, limit=10):
    """Fetch and parse RSS feed"""
    feed = feedparser.parse(url)
    articles = []
    
    for entry in feed.entries[:limit]:
        articles.append({
            'title': entry.get('title', ''),
            'link': entry.get('link', ''),
            'published': entry.get('published', ''),
            'summary': entry.get('summary', ''),
            'source': feed.feed.get('title', url)
        })
    
    return articles

# Example usage
feeds = [
    'https://www.reddit.com/r/ArtificialIntelligence/.rss',
    'https://news.ycombinator.com/rss',
    'https://www.AINewsBrief.com/feed'
]

for feed_url in feeds:
    articles = fetch_feed(feed_url)
    print(f"Found {len(articles)} articles from {feed_url}")
```

### Option 2: Self-Hosted Aggregators

| Tool | Type | Docker | API | Best For |
|------|------|--------|-----|----------|
| **Miniflux** | Aggregator | ✅ | REST | Minimalist, fast |
| **FreshRSS** | Aggregator | ✅ | REST, GReader | Feature-rich |
| **TT-RSS** | Aggregator | ✅ | REST, Fever | Advanced users |
| **Cloudflare** | SaaS | ❌ | API | No maintenance |

**Miniflux (Recommended):**
```yaml
# docker-compose.yml
version: '3'
services:
  miniflux:
    image: miniflux/miniflux:latest
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgres://user:pass@db/miniflux?sslmode=disable
      - RUN_MIGRATIONS=1
      - CREATE_ADMIN=1
      - ADMIN_USERNAME=nova
      - ADMIN_PASSWORD=secure_password
    depends_on:
      - db
    restart: unless-stopped
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=miniflux
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  pgdata:
```

### Option 3: Cloud Services

- **Feedly** - Popular SaaS, $7+/month
- **Inoreader** - Feature-rich, $5+/month
- **The Old Reader** - Free, social features

### Option 4: Automation Platforms

- **n8n** - Has RSS nodes for workflows
- **Zapier** - RSS to Slack/Email/Chat
- **IFTTT** - Basic RSS triggers

---

## OpenClaw Skill Integration

### Skill Structure

```
skills/rss-reader/
├── SKILL.md          # Main skill file
├── README.md         # Documentation
├── config.json       # Feed configurations
├── feeds/            # Feed definitions
└── scripts/
    ├── fetcher.py    # RSS fetching logic
    └── processor.py  # Content processing
```

### SKILL.md Template

```markdown
# RSS Reader Skill

Monitor and process RSS feeds for content discovery.

## Setup
1. Add feed URLs to config.json
2. Set fetch interval (recommended: hourly)
3. Configure output (Discord, webhook, file)

## Commands
- `rss add <url>` - Add new feed
- `rss list` - Show all feeds
- `rss fetch` - Fetch latest articles
- `rss search <query>` - Search articles
```

### Sample config.json

```json
{
  "feeds": [
    {"name": "HN", "url": "https://news.ycombinator.com/rss", "category": "tech"},
    {"name": "AI News", "url": "https://www.ainewsbrief.com/feed", "category": "ai"},
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss", "category": "ai"}
  ],
  "settings": {
    "fetch_interval_minutes": 60,
    "max_articles_per_feed": 20,
    "output_channel": "discord",
    "filter_keywords": ["AI", "GPT", "automation", "OpenClaw"]
  }
}
```

---

## AI Content Pipeline

```
RSS Feeds → Fetch → Filter → Summarize → Publish
              ↓         ↓          ↓
           feedparser  keywords  LLM API   WordPress/Postiz
```

### Example: AI-Powered Summary

```python
import feedparser
from openai import OpenAI  # or local LLM

def summarize_articles(feeds, client):
    """Fetch and summarize RSS articles"""
    all_articles = []
    
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:
            # Use LLM to summarize
            summary = client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system", 
                    "content": "Summarize this article in 2 sentences"
                }, {
                    "role": "user", 
                    "content": entry.summary
                }]
            )
            all_articles.append({
                'title': entry.title,
                'summary': summary.choices[0].message.content,
                'link': entry.link
            })
    
    return all_articles
```

---

## Recommended Feeds for AI/Tech

| Feed | URL | Category |
|------|-----|----------|
| Hacker News | https://news.ycombinator.com/rss | tech |
| OpenAI Blog | https://openai.com/blog/rss | ai |
| Anthropic | https://www.anthropic.com/rss | ai |
| MIT Tech Review | https://www.technologyreview.com/feed/ | tech |
| Wired | https://www.wired.com/feed/rss | tech |
| Verge | https://www.theverge.com/rss/index.xml | tech |
| Ars Technica | https://feeds.arstechnica.com/arstechnica/index | tech |

---

## Installation Priority

| Priority | Item | Effort | Value |
|----------|------|--------|-------|
| **HIGH** | feedparser Python script | 1 hr | Content pipeline |
| **HIGH** | Curated feed list | 2 hr | Research efficiency |
| **MEDIUM** | Miniflux self-hosted | 4 hr | Better UX |
| **LOW** | n8n RSS automation | 8 hr | Workflows |

---

## Next Steps

1. ✅ Install `feedparser` (pip install feedparser)
2. Create `~/rss-feeds/` config directory
3. Add initial feed list (HN, AI news, tech blogs)
4. Build simple fetch script for Discord reporting
5. Consider Miniflux for visual interface later

---

*Created: 2026-02-22*
*Topic: RSS Reader Integration*
*Status: Research Complete*
