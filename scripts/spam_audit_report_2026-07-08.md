# Gmail Spam Audit Report
**Date:** 2026-07-08
**Accounts checked:** 4
**Window:** Last 3 days (INBOX cap: 80 emails, Spam cap: 80 emails)

## compjunkie@gmail.com

### INBOX (last 3 days)
- Total checked: 80
- Spam found: 3
  - False negatives (blocklisted domain, still in INBOX): 1
  - New uncaught spam: 2

**False Negatives (blocklisted domain still in INBOX):**
- `iwhaa.com` | `Pull My Hair and Make Me  Yours… 😏` | blocklisted domain: iwhaa.com

**New Uncaught Spam (not in blocklist):**
- `rugcoumvlof.ru` | `Get inside before the stream ends. ⚡️` | fake sender name (dating/sexual)
- `ubpew.qpj` | `Your Account has been Blocked All Your Photos and videos will be
 Rem` | business scam

### Spam Folder (last 3 days)
- Total in Spam: 0
- Blocklisted domains caught: 0
- Non-blocklisted caught by Gmail: 0

## jhenderson87@gmail.com

### INBOX (last 3 days)
- Total checked: 80
- Spam found: 0
  - False negatives (blocklisted domain, still in INBOX): 0
  - New uncaught spam: 0

### Spam Folder (last 3 days)
- Total in Spam: 3
- Blocklisted domains caught: 1
- Non-blocklisted caught by Gmail: 2

**Spam caught by Gmail (not in our blocklist):**
- `questionprov5129231.com` | `Your Oral-B Dental Kit Is Ready`
- `privaterelay.appleid.com` | `10 new tools for hiring, invoicing, and closing deals 💼`

## layeredmediallc@gmail.com

### INBOX (last 3 days)
- Total checked: 35
- Spam found: 0
  - False negatives (blocklisted domain, still in INBOX): 0
  - New uncaught spam: 0

### Spam Folder (last 3 days)
- Total in Spam: 1
- Blocklisted domains caught: 0
- Non-blocklisted caught by Gmail: 1

**Spam caught by Gmail (not in our blocklist):**
- `tiktokshop.com` | `James, explore our latest styles`

## nova.cofounder@gmail.com

### INBOX (last 3 days)
- Total checked: 5
- Spam found: 0
  - False negatives (blocklisted domain, still in INBOX): 0
  - New uncaught spam: 0

### Spam Folder (last 3 days)
- Total in Spam: 0
- Blocklisted domains caught: 0
- Non-blocklisted caught by Gmail: 0

---
## Summary

| Metric | Count |
|--------|-------|
| Total false negatives (blocklisted, in INBOX) | 1 |
| Total new uncaught spam (INBOX, not blocklisted) | 2 |
| Total spam in Spam folders | 4 |
| Blocklist hits in Spam folder | 1 |
| **New spam domains discovered** | **5** |

### New Spam Domains to Add
```python
    "privaterelay.appleid.com",
    "questionprov5129231.com",
    "rugcoumvlof.ru",
    "tiktokshop.com",
    "ubpew.qpj",
```

### False Negative Details
These domains are in the blocklist but emails still got to INBOX:

- **compjunkie@gmail.com** | `iwhaa.com` | `Pull My Hair and Make Me  Yours… 😏` | blocklisted domain: iwhaa.com

### All New Uncaught Spam

- **compjunkie@gmail.com** | `rugcoumvlof.ru` | `Get inside before the stream ends. ⚡️` | fake sender name (dating/sexual)
- **compjunkie@gmail.com** | `ubpew.qpj` | `Your Account has been Blocked All Your Photos and videos will be
 Removed Today: Wed, 08 Jul 2026 16:31:04 +0200` | business scam
