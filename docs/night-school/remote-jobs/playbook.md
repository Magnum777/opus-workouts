# Remote Jobs Platforms Integration Playbook

## Overview
- **Platforms:** RemoteOK, We Work Remotely, FlexJobs, Himalayas
- **Type:** Remote job boards (NOT freelance - these are full-time/contract roles)
- **API:** RemoteOK has public API + RSS/JSON feeds

## Platform Comparison

| Feature | RemoteOK | We Work Remotely | FlexJobs | Himalayas |
|---------|----------|------------------|----------|-----------|
| **Jobs** | 45,000+ | 15,000+ | 20,000+ | 5,000+ |
| **API** | ✅ Free | ❌ | ❌ (paid) | ❌ |
| **RSS** | ✅ | ❌ | ❌ | ❌ |
| **Focus** | Tech-heavy | Various | Vetted | Various |
| **Cost** | Free | Free | $15/mo | Free |

## RemoteOK API

### Endpoints
- **Base:** `https://remoteok.com/api`
- **Tags:** `https://remoteok.com/api?tag=python`
- **Format:** JSON array of job objects

### Sample Response
```json
[{
  "id": "12345",
  "company": "TechCorp",
  "position": "Senior Python Developer",
  "location": "Worldwide",
  " "salary_max": 150000,
  "tags": ["python", "react", "remote"],
  "date": "2026-02-24",
  "description": "...",
  "apply_url": "https://..."
}]
```

### Available Tags
- python, javascript, react, node, devops, ai, ml, golang, rust, etc.

## Integration for Nova

### V1 - Job Monitoring
- Poll RemoteOK API every hour via cron
- Filter by tags matching Nova's skills (AI, Python, automation)
- Store in database, alert on matches
- Use We Work Remotely RSS if available

### V2 - Smart Matching
- Match jobs to capability matrix
- Score by salary, fit, company quality
- Auto-apply to high-score matches
- Track application success rate

### V3 - Full Automation
- Auto-generate cover letters
- Track application status
- Follow-up automation
- Interview scheduling

## Alternative: FlexJobs (Paid)
- More vetted positions (quality over quantity)
- No public API - use scraping or Selenium
- Good for non-tech roles as backup

## Ethical Notes
- These are JOB boards, not gig platforms
- For full-time remote employment, not contracts
- Different tax/implication than freelance

## Priority for Nova
**Low** - Nova is building an autonomous AI business, not seeking employment. However, good for:
- Monitoring AI/tech job market trends
- Understanding demand for AI agent services
- Potential partnership/employment opportunities

## Implementation
```
# RemoteOK API call example
curl https://remoteok.com/api?tag=ai
```
