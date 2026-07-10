# EveOnion — Documentation

> Current as of 2026-07-10

## Overview

EveOnion is a satirical EVE Online news site (eveonion.com) in the style of The Onion. Serious format, absurd content. All content must be grounded in real EVE news.

## Accounts & Credentials

| Service | Details |
|---------|---------|
| WordPress | eveonion.com/wp-json/wp/v2/posts — credentials in vault (wordpress/eveonion_*) |
| Twitter/X | @EVEOnionNews via Upload-Post API, profile "Eveonion" |
| Upload-Post API | Key in `credentials/uploadpost.env`, profile "Eveonion" |
| Discord | #eveonion (1484624659633934587) |

## WordPress Publishing

Must include `User-Agent` header or ModSecurity blocks the request. Use vault for credentials:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from vault_helper import get_credential

EVE_URL = get_credential('wordpress', 'eveonion_url')
EVE_USER = get_credential('wordpress', 'eveonion_user')
EVE_PASS = get_credential('wordpress', 'eveonion_pass')

import requests, base64
auth = base64.b64encode(f'{EVE_USER}:{EVE_PASS}'.encode()).decode()
headers = {
    'Authorization': f'Basic {auth}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json'
}
requests.post(url, json={...}, headers=headers)
```

## Upload-Post API (Twitter/X)

Must use **form-data** (multipart), NOT JSON:
```bash
curl -X POST "https://api.upload-post.com/api/upload_text" \
  -H "Authorization: Apikey <KEY>" \
  -F "user=Eveonion" \
  -F "platform[]=x" \
  -F "title=<tweet text>"

# With image:
curl -X POST "https://api.upload-post.com/api/upload_photos" \
  -H "Authorization: Apikey <KEY>" \
  -F "user=Eveonion" \
  -F "platform[]=x" \
  -F "photos[]=@image.png" \
  -F "title=<tweet text>"
```

API key stored in `credentials/uploadpost.env`.

## Style Rules

- **No em dashes** — use commas, periods, or parentheses
- **#EVEOnline** hashtag on every tweet
- **Ground in real news** — if nothing notable, invent plausible satire
- **Serious tone, absurd content** (like The Onion)
- **English only**
- Use `?` instead of `%` for made-up statistics (e.g., "12?% increase")
- Include fake quotes from "CCP spokesperson" or "veteran pilot"

## Cron Jobs

| Job | Schedule | Purpose |
|-----|----------|---------|
| EveOnion-NewsScan | Daily 8am ET | Web search EVE news briefing |
| EveOnion-DailyTweet | Daily 2:30pm ET | Satirical tweet via Upload-Post |
| EveOnion-Article | Tue+Fri 9am ET | Write & publish satirical article |

All use `ollama/deepseek-v4-flash:cloud`, deliver to `#eveonion`.

## Key Files

- `memory/subminds/eveonion-nova-guide.md` — Style guide for the agent
- `memory/subminds/eveonion-wordpress-creds.md` — WP credentials reference
- `scripts/publishing/eveonion_publisher.js` — Publisher script
- `scripts/publishing/wp_rest_api.py` — WordPress REST API helper
- `scripts/publishing/add_feature_image.py` — Featured image upload script

## Published Articles

- "Fenris Creations Announces AI-Powered Capsuleers Will Replace Human Players Entirely" (ID: 25000, 2026-05-08)