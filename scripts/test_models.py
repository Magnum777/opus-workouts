import requests, json

ollama_url = "http://192.168.68.50:11434"

# Test deepseek-v4-flash:cloud
models_to_test = ["deepseek-v4-flash:cloud", "kimi-k2.6:cloud", "minimax-m2.7:cloud"]

for model in models_to_test:
    print(f"\nTesting: {model}")
    try:
        r = requests.post(
            f"{ollama_url}/api/generate",
            json={"model": model, "prompt": "Say 'hi' in 3 words. Do not elaborate.", "stream": False, "options": {"num_predict": 10}},
            timeout=15
        )
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"  Response: {data.get('response', '')[:100]}")
        else:
            print(f"  Error: {r.text[:200]}")
    except Exception as e:
        print(f"  Exception: {type(e).__name__}: {e}")
