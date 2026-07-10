import requests, json

# Test what happens when we call kimi-k2.6:cloud on the local Ollama
r = requests.post(
    "http://192.168.68.50:11434/api/generate",
    json={"model": "kimi-k2.6:cloud", "prompt": "Say 'hi' in 3 words", "stream": False},
    timeout=10
)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")
