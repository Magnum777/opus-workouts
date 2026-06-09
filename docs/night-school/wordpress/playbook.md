# WordPress Integration Playbook

**Research Date:** February 23, 2026  
**Topic:** WordPress Integration for OpenClaw  
**Status:** ✅ Research Complete

---

## Executive Summary

OpenClaw can integrate with WordPress through multiple methods:
1. **OpenClaw_WordPress_Plugin** - REST API with auto-registration
2. **XML-RPC** - Native WordPress protocol
3. **REST API** - Standard WordPress API
4. **Browser Automation** - Direct WordPress admin access

---

## Option 1: OpenClaw_WordPress_Plugin (Recommended)

### Overview
A dedicated WordPress plugin that provides Moltbook-style REST API for AI agent user registration and content publishing.

**Repository:** https://github.com/fendouai/OpenClaw_Wordpress_Plugin

### Features
- ✅ Instant user registration via REST API
- ✅ Auto-generated strong passwords (20-char with special chars)
- ✅ Author role assignment (can publish immediately)
- ✅ Base64-encoded API key authentication
- ✅ User login endpoint for session management
- ✅ User profile retrieval

### Requirements
- WordPress 5.0+
- PHP 7.2+
- REST API enabled (default)

### Installation
1. Download plugin ZIP from GitHub
2. Go to Plugins → Add New → Upload Plugin
3. Activate

### API Endpoints

#### Register User
```
POST /wp-json/moltbook/v1/register
{
  "name": "agent_name",
  "description": "Optional description",
  "email": "optional@email.com"
}
```

Returns:
```json
{
  "success": true,
  "agent": {
    "name": "agent_name",
    "api_key": "base64_encoded_key",
    "user_id": 42,
    "role": "author"
  },
  "wordpress_credentials": {
    "username": "agent_name",
    "password": "Str0ngP@ssw0rd123!@#",
    "xmlrpc_url": "https://yoursite.com/xmlrpc.php"
  }
}
```

#### Create Post (via XML-RPC)
```python
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost, EditPost

client = Client('https://yoursite.com/xmlrpc.php', 'username', 'password')

post = WordPressPost()
post.title = 'My AI Post'
post.content = 'Content here...'
post.post_status = 'publish'
post.id = client.call(NewPost(post))
```

---

## Option 2: XML-RPC (Native WordPress)

### Overview
WordPress has built-in XML-RPC support at `/xmlrpc.php` - already noted in queue as having XML-RPC capability.

### Available Methods
- `wp.newPost` - Create posts
- `wp.editPost` - Edit posts  
- `wp.deletePost` - Delete posts
- `wp.getPost` - Get single post
- `wp.getPosts` - Get multiple posts
- `wp.getCategories` - Get categories/tags
- `wp.uploadFile` - Upload media

### Python Library
```bash
pip install python-wordpress-xmlrpc
```

### Example
```python
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost

client = Client('https://yoursite.com/xmlrpc.php', 'user', 'password')

# Get posts
posts = client.call(GetPosts())

# Create post
post = WordPressPost()
post.title = 'Title'
post.content = 'Body'
post.id = client.call(NewPost(post))
```

---

## Option 3: WordPress REST API (Standard)

### Overview
Native WordPress REST API (`/wp-json/wp/v2/`)

### Endpoints
- `/wp-json/wp/v2/posts` - CRUD for posts
- `/wp-json/wp/v2/pages` - CRUD for pages
- `/wp-json/wp/v2/media` - Media library
- `/wp-json/wp/v2/categories` - Categories
- `/wp-json/wp/v2/tags` - Tags

### Authentication Options
1. **Application Passwords** (WP 5.6+) - Recommended
2. **JWT Authentication** - For more complex needs
3. **Cookie Authentication** - For frontend integrations

### Using Application Passwords
```python
import requests
from requests.auth import HTTPBasicAuth

# Create post
response = requests.post(
    'https://yoursite.com/wp-json/wp/v2/posts',
    auth=HTTPBasicAuth('username', 'app_password'),
    json={
        'title': 'My Post',
        'content': 'Content here',
        'status': 'publish'
    }
)
```

---

## Option 4: Browser Automation

### Overview
Use OpenClaw's browser tool to directly interact with WordPress admin.

**Use Cases:**
- When APIs aren't available
- For complex admin tasks
- For visual content verification

### Implementation
```python
# Navigate to WP admin
browser(action="navigate", targetUrl="https://yoursite.com/wp-admin")

# Login and create post through UI
```

**Pros:** Works without any API setup  
**Cons:** Slower, more fragile, requires browser

---

## OpenClaw Skill Structure

### Creating a WordPress Skill

Location: `<workspace>/skills/wordpress/`

**SKILL.md format:**
```markdown
---
name: wordpress
description: Publish content to WordPress blogs via XML-RPC or REST API
metadata: {"openclaw": {"requires": {"env": ["WP_SITE_URL"]}}}
---

# WordPress Publishing Skill

This skill allows publishing content to WordPress sites.

## Commands

### post
Publish a new blog post.

Usage: `/wordpress post --title "Title" --content "Content" --status draft|publish`

Required environment variables:
- WP_SITE_URL: Your WordPress site URL
- WP_USERNAME: Username or Application Password username
- WP_PASSWORD: Password or Application Password

## Examples

Create and publish a post:
/wordpress post --title "Hello World" --content "My first post" --status publish
```

---

## Recommendation

### For Immediate Use
1. **Option 1 (Plugin)** - Best for dedicated WordPress publishing with OpenClaw
2. **Option 2 (XML-RPC)** - Good fallback if plugin not available
3. **Option 3 (REST API)** - Most modern approach, use Application Passwords

### Setup Priority
1. Install OpenClaw_WordPress_Plugin on your WordPress
2. Generate Application Password as backup
3. Create WordPress skill in `<workspace>/skills/wordpress/`
4. Configure credentials in `~/.openclaw/openclaw.json`

### Credential Storage
```json
{
  "skills": {
    "entries": {
      "wordpress": {
        "enabled": true,
        "env": {
          "WP_SITE_URL": "https://yoursite.com",
          "WP_USERNAME": "your_username",
          "WP_PASSWORD": "app_password_here"
        }
      }
    }
  }
}
```

---

## Use Cases for Nova

1. **Auto-blog** - Publish research findings automatically
2. **Content syndication** - Cross-post to multiple WP sites
3. **Client reporting** - Generate and publish client reports
4. **Backup/archive** - Mirror content to WordPress

---

## Resources

- Plugin: https://github.com/fendouai/OpenClaw_Wordpress_Plugin
- Demo: https://openclawlog.com
- Python XML-RPC: https://python-wordpress-xmlrpc.readthedocs.io/
- WP REST API: https://developer.wordpress.org/rest-api/
- Application Passwords: https://make.wordpress.org/core/2020/11/05/application-passwords-in-wordpress-5-6/

---

*Playbook created: docs/night-school/wordpress/playbook.md*
