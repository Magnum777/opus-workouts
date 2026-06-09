# Uptime Kuma - Health Monitoring

**Research Date:** February 23, 2026  
**Topic:** Self-hosted health monitoring on Synology NAS  
**Source:** Marius Hosting Guide

---

## What is Uptime Kuma?

Self-hosted monitoring tool that tracks your website/services uptime. Notifies you when things go down.

**Features:**
- HTTP(s) / TCP / Ping monitoring
- 20-second check interval
- Notifications: Webhook, Telegram, Discord, Email (SMTP)
- Dark mode UI
- Multiple monitors

## Pricing

| Version | Cost |
|---------|------|
| **Self-hosted** | **Free** ✅ |

---

## Installation (Super Simple!)

### Prerequisites
- Synology with Container Manager (or Docker)
- 1 folder: `/volume1/docker/uptimekuma`

### Steps

1. **Create folder** in File Station:
   - `/volume1/docker/uptimekuma`

2. **Create Task** in Task Scheduler:
   - Name: "Install Uptime Kuma"
   - User: root
   - Run command:
   ```
   docker run -d --name=uptime_kuma \
   -p 3444:3001 \
   -e TZ=America/New_York \
   -v /volume1/docker/uptimekuma:/app/data \
   -v /var/run/docker.sock:/var/run/docker.sock \
   --restart always \
   louislam/uptime-kuma:2
   ```

3. **Run the task** - installs automatically

4. **Access** at: `http://YOUR-NAS-IP:3444`

5. **Setup:**
   - Select SQLite database
   - Create admin user
   - Add monitors

---

## What to Monitor

| Monitor | URL | Interval |
|---------|-----|----------|
| aitoolalliance.com | https://aitoolalliance.com | 60s |
| aibusinessinsideraibusinessins.org | https://ider.org | 60s |
| aicofounderstack.com | https://aicofounderstack.com | 60s |
| eveonion.com | https://eveonion.com | 60s |
| NAS | 192.168.68.82 | 60s |
| OpenClaw Gateway | localhost:18789 | 30s |

---

## Notifications

Set up in Settings:
- **Discord** - Webhook
- **Telegram** - Bot API
- **Email** - SMTP

---

## For Nova

Uptime Kuma can alert Nova via webhook when sites go down!

**Webhook URL:** 
```
http://YOUR-NAS-IP:3444/api/notification/push
```

---

## Resources

- [Official Site](https://uptimekuma.org/)
- [GitHub](https://github.com/louislam/uptime-kuma)
- [Marius Hosting Guide](https://mariushosting.com/how-to-install-uptime-kuma-on-your-synology-nas/)

---

*Last Updated: February 23, 2026*
