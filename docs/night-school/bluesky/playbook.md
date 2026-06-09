# Bluesky Integration Playbook

## Overview

Bluesky is an emerging decentralized social platform built on the AT Protocol. It's rapidly growing and valuable for marketing the AI Co-Founder Stack. The platform has excellent API support for bots and automation.

## Use Cases for AI Co-Founder Stack

1. **Automated posting** - Cross-post blog content to Bluesky
2. **Engagement bots** - Auto-like/repost content matching keywords
3. **Content discovery** - Monitor feeds for relevant topics
4. **Scheduling** - Queue posts for optimal times
5. **Analytics** - Track engagement metrics

## Technical Setup

### Prerequisites
- Node.js + TypeScript
- Bluesky account (create at bsky.app)
- `@atproto/api` npm package

### Installation
```bash
npm install @atproto/api dotenv cron
```

### Basic Bot Script
```typescript
import { BskyAgent } from '@atproto/api';
import * as dotenv from 'dotenv';
import { CronJob } from 'cron';
import * as process from 'process';

dotenv.config();

// Create a Bluesky Agent
const agent = new BskyAgent({
  service: 'https://bsky.social',
})

async function main() {
  await agent.login({ 
    identifier: process.env.BLUESKY_USERNAME!, 
    password: process.env.BLUESKY_PASSWORD! 
  })
  
  await agent.post({
    text: "Hello from my AI bot! 🚀"
  });
  
  console.log("Just posted!");
}

main();
```

### Session Management (Recommended)
```typescript
// Persist session to avoid login rate limits
const session = readSessionFromDisk()
if (session) {
  agent.resumeSession(session)
} else {
  await agent.login({ 
    identifier: process.env.BLUESKY_USERNAME!, 
    password: process.env.BLUESKY_PASSWORD! 
  })
  writeSessionToDisk(agent.session)
}
```

## API Capabilities

| Operation | Endpoint | Description |
|-----------|----------|-------------|
| Post | `agent.post()` | Create new post |
| Like | `agent.like()` | Like a post |
| Repost | `agent.repost()` | Share a post |
| Reply | `agent.post()` with reply | Reply to thread |
| Search | `agent.searchPosts()` | Find content |
| Timeline | `agent.getTimeline()` | Home feed |

## Rate Limits

- **Login**: Limited (persist sessions!)
- **Posting**: ~300 posts/hour
- **Interactions**: Opt-in only (don't spam)

**Important**: Only interact with users who have tagged your bot or opted in. Bluesky is strict about spam.

## Skill Implementation for OpenClaw

### Files Needed
1. `skills/bluesky/SKILL.md` - Instructions
2. `skills/bluesky/index.js` - Integration code
3. `.env` - Credentials (BLUESKY_USERNAME, BLUESKY_PASSWORD)

### Key Features to Implement
- `post(text)` - Create post
- `like(uri)` - Like a post
- `repost(uri)` - Share a post
- `search(query)` - Find posts
- `getTimeline()` - Get home feed

## Integration with Postiz

Bluesky can be added to Postiz for unified scheduling across platforms. This would allow:
- Schedule once → post to Bluesky + Twitter + LinkedIn
- Central analytics
- Queue management

## Priority for AI Co-Founder Stack

**Rating: ⭐⭐⭐⭐ (4/5)**

- Growing platform with engaged tech audience
- Easy API, good docs
- Lower saturation than Twitter
- Great for AI/tech content marketing

## Next Steps

1. Create Bluesky account for Layered Media
2. Build basic posting bot
3. Integrate with Postiz (or standalone skill)
4. Test engagement automation
5. Add to V2 skill recommendations

---

*Created: 2026-02-22*
*Source: docs.bsky.app, atproto.com*
