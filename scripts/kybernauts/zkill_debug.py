import urllib.request
import gzip
import json

url = 'https://zkillboard.com/api/corporation/98754582/kills/pastSeconds/345600/'
headers = {
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip',
    'User-Agent': 'Nova Intel Tracker (Kybernauts) / Contact: layeredmediallc@gmail.com'
}
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f'Status: {resp.status}')
        print(f'Content-Type: {resp.headers.get("Content-Type")}')
        print(f'Content-Encoding: {resp.headers.get("Content-Encoding")}')
        data = resp.read()
        print(f'Raw length: {len(data)}')
        
        # Try to decompress if gzip
        if resp.headers.get("Content-Encoding") == "gzip":
            try:
                data = gzip.decompress(data)
                print(f'Decompressed length: {len(data)}')
            except Exception as e:
                print(f'Failed to decompress: {e}')
        
        # Try to parse as JSON
        try:
            parsed = json.loads(data.decode('utf-8', errors='ignore'))
            print(f'Parsed type: {type(parsed)}')
            if isinstance(parsed, list):
                print(f'Number of records: {len(parsed)}')
                if parsed:
                    print(f'First record keys: {list(parsed[0].keys())[:5]}')
            else:
                print(f'Content preview: {str(parsed)[:200]}')
        except Exception as e:
            print(f'Failed to parse JSON: {e}')
            print(f'Raw content (first 500): {data[:500]}')
            
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
