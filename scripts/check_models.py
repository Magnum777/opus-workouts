import json
with open('C:/Users/compj/.openclaw/openclaw.json', encoding='utf-8') as f:
    cfg = json.load(f)
models = cfg.get('models', {}).get('providers', {})
ollama = models.get('ollama', {})
for m in ollama.get('models', []):
    print(f"id={m['id']} api={m.get('api')} base={ollama.get('baseUrl')}")
