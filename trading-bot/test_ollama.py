import requests
import json

url = "http://192.168.68.50:11434/api/chat"
payload = {
    "model": "qwen2.5:7b",
    "messages": [
        {"role": "user", "content": "Return ONLY valid JSON: { \"action\": \"HOLD\", \"size_eth\": 0.0 }"}
    ],
    "stream": False
}

try:
    resp = requests.post(url, json=payload, timeout=60)
    print("Status:", resp.status_code)
    print("Response:", resp.text[:500])
except Exception as e:
    print("Error:", e)
