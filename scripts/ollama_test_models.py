import requests, time, json
key = '89cb21d18ccd4822956fae99a65b7bed.doEM4KtS2ibbLl2fSqeK7yFZ'

thinking_models = ['qwen3.5:397b', 'minimax-m2.7', 'kimi-k2.5', 'kimi-k2:1t', 'qwen3-coder-next']
for mod in thinking_models:
    try:
        r = requests.post('https://ollama.com/api/chat',
            headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
            json={'model': mod, 'messages': [{'role': 'user', 'content': 'What is 2+2?'}], 'stream': False, 'think': True, 'options': {'num_predict': 100}},
            timeout=60)
        resp = r.json()
        content = resp.get('message', {}).get('content', '')
        think = resp.get('think_content', '')
        print(f'{mod}: HTTP {r.status_code}')
        print(f'  content: {content[:80]}')
        print(f'  think: {(think[:80] if think else "(none)")}')
        print()
    except Exception as e:
        print(f'{mod}: ERROR - {str(e)[:60]}')
