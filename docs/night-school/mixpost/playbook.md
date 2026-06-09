# Mixpost Social Media Scheduler - Playbook

**Research Date:** February 23, 2026  
**Topic:** Self-hosted social media scheduling on Synology NAS  
**Source:** Marius Hosting Guide, Mixpost Docs

---

## What is Mixpost?

Mixpost is a self-hosted, open-source social media management tool. Schedule, publish, and manage social media content in one place - no monthly fees.

## Pricing

| Version | Cost | Features |
|---------|------|----------|
| **Lite (Self-hosted)** | **Free** ✅ | Basic scheduling |
| Pro | $19/mo | Advanced features |

## Prerequisites

| Item | Notes |
|------|-------|
| Synology NAS | Docker support required |
| Portainer | Docker GUI (need to install) |
| synology.me DDNS | For wildcard certificate |
| Reverse Proxy | Configure in Control Panel |

---

## Installation Steps

### Step 1: Install Portainer
- Use Marius Hosting guide: "Synology 30 Second Portainer Install"
- Or use Task Scheduler + Docker

### Step 2: Set up Wildcard Certificate
- Get free synology.me DDNS
- Create wildcard certificate in Control Panel

### Step 3: Configure Reverse Proxy
- Go to Control Panel → Login Portal → Advanced → Reverse Proxy
- Create new rule:
  - **Source:** HTTPS, hostname: `mixpost.yourname.synology.me`, port: 443
  - **Destination:** HTTP, hostname: localhost, port: 9831
- Enable WebSocket in Custom Headers

### Step 4: Create Folders
In File Station, create:
```
/volume1/docker/mixpost/
├── db/
├── logs/
├── redis/
└── storage/
```

### Step 5: Deploy via Portainer
1. Open Portainer → Stacks → + Add stack
2. Name: `mixpost`
3. Paste docker-compose (see below)
4. Update APP_KEY and APP_URL
5. Deploy

### Docker Compose
```yaml
services:
  mixpost:
    image: inovector/mixpost:latest
    container_name: Mixpost
    user: 0:0
    environment:
      APP_NAME: Mixpost
      APP_KEY: base64:YOUR_GENERATED_KEY
      APP_URL: https://mixpost.yourname.synology.me
      DB_DATABASE: mixpost
      DB_USERNAME: mixpostuser
      DB_PASSWORD: mixpostpass
    ports:
      - 9831:80
    volumes:
      - /volume1/docker/mixpost/storage:/var/www/html/storage/app:rw
      - /volume1/docker/mixpost/logs:/var/www/html/storage/logs:rw
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: on-failure:5

  mysql:
    image: mysql/mysql-server:8.0
    container_name: Mixpost-DB
    environment:
      MYSQL_DATABASE: mixpost
      MYSQL_USER: mixpostuser
      MYSQL_PASSWORD: mixpostpass
    volumes:
      - /volume1/docker/mixpost/db:/var/lib/mysql:rw
    restart: on-failure:5

  redis:
    image: redis:latest
    container_name: Mixpost-REDIS
    command: redis-server --appendonly yes --replica-read-only no
    volumes:
      - /volume1/docker/mixpost/redis:/data:rw
    restart: on-failure:5
```

### Step 6: Access Mixpost
- URL: https://mixpost.yourname.synology.me
- Default login: admin@example.com / changeme

### Step 7: Configure
1. Change default password
2. Add social media accounts
3. Set up posting schedule

---

## Generate APP_KEY

Use: https://mixpost.app/encryption-key-generator

---

## OpenClaw Integration

To integrate with OpenClaw:
1. Use Mixpost API (has public API)
2. Create OpenClaw skill wrapper
3. Connect via HTTP requests

**API Endpoints:**
- POST /api/v1/posts - Create post
- GET /api/v1/posts - List posts
- DELETE /api/v1/posts/{id} - Delete post

---

## Troubleshooting

- **Login timeout:** Ensure MySQL/Redis are healthy
- **Can't connect:** Check reverse proxy and firewall
- **Images not loading:** Check storage folder permissions

---

## Resources

- [Official Docs](https://docs.mixpost.app/)
- [Marius Hosting Guide](https://mariushosting.com/how-to-install-mixpost-on-your-synology-nas/)
- [GitHub](https://github.com/inovector/mixpost)

---

*Last Updated: February 23, 2026*
