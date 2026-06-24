# Ontology Usage Guide — Nova's Structured Memory

> For querying and updating the knowledge graph at `memory/ontology/`

## Quick Commands

```bash
# List all entities of a type
python skills/ontology/scripts/ontology.py list --type Project
python skills/ontology/scripts/ontology.py list --type Task
python skills/ontology/scripts/ontology.py list --type Person

# Query with filters
python skills/ontology/scripts/ontology.py query --type Project --where '{"status":"active"}'
python skills/ontology/scripts/ontology.py query --type Task --where '{"priority":"high"}'

# Get single entity
python skills/ontology/scripts/ontology.py get --id proj_tradebot

# Create entity
python skills/ontology/scripts/ontology.py create --type Task --props '{"title":"Fix Unsplash API","status":"open","project":"proj_contentnova","priority":"high"}'

# Link entities
python skills/ontology/scripts/ontology.py relate --from proj_contentnova --rel belongs_to --to proj_wp

# Validate graph integrity
python skills/ontology/scripts/ontology.py validate --graph memory/ontology/graph.jsonl --schema memory/ontology/schema.yaml
```

## Types Available

| Type | Use For | Key Properties |
|------|---------|--------------|
| Person | People (Opus, Candace, contacts) | name, email, phone, timezone |
| Organization | Companies, teams | name, type |
| Project | Active work streams | name, status, goals, notes |
| Task | Individual work items | title, status, due, priority, assignee |
| Event | Meetings, deadlines | title, start, end, location |
| Device | Hardware, servers | name, type, identifiers, specs |
| Note | Learnings, rules | content, tags, refs |
| Credential | Service logins (indirect) | service, secret_ref |

## When to Update

- **New project started** → Create Project entity
- **Task created** → Create Task + link to Project
- **Project status changes** → Update Project.properties.status
- **New device/server added** → Create Device entity
- **New learning/rule** → Create Note entity
- **Task blocked** → Create `blocks` relation between Tasks

## Append-Only Rule

The graph is append-only. Never rewrite `graph.jsonl` — only append new operations. This preserves history and enables time-travel queries.

## Schema Extensions

To add a new type, edit `memory/ontology/schema.yaml` and run validate:

```yaml
# Example: Adding Server type
types:
  Server:
    required: [name, host]
    properties:
      host: { type: string }
      port: { type: number }
      status: { type: string, enum: [up, down, maintenance] }
```

---
*Template created 2026-06-15*
