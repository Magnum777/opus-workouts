# EveOnion WordPress Credentials

> For EveOnion-Nova sub-mind reference

## Site: eveonion.com

| Field | Value |
|-------|-------|
| URL | https://eveonion.com |
| Username | nova |
| App Password | EVEONION_APP_PASSWORD_REDACTED |
| XML-RPC | https://eveonion.com/xmlrpc.php |
| REST API | https://eveonion.com/wp-json/wp/v2 |

## Usage

### Emergency Edit (REST API)
```python
python scripts/publishing/wp_rest_api.py eveonion.com list
python scripts/publishing/wp_rest_api.py eveonion.com update --post-id <ID> --content "new content"
```

### Publish New Post
```python
python scripts/publishing/wp_rest_api.py eveonion.com create --title "Title" --content "<p>HTML content</p>"
```

## Notes
- Use Application Password (not login password)
- REST API preferred over XML-RPC
- Emergency edits: use `wp_rest_api.py` wrapper

---
_Credentials from CREDENTIALS.md_
