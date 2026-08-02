import urllib.request
import gzip
import json
import time

headers = {
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip',
    'User-Agent': 'Nova Intel Tracker (Kybernauts) / Contact: layeredmediallc@gmail.com'
}

# Test corporationID endpoint kills
time.sleep(3)
url = 'https://zkillboard.com/api/corporationID/98754582/kills/pastSeconds/345600/'
print('Testing: ' + url)
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = gzip.decompress(resp.read())
        parsed = json.loads(data.decode('utf-8', errors='ignore'))
        print('Kills returned: ' + str(len(parsed)) + ' records')
        if parsed and len(parsed) > 0:
            print('First record keys: ' + str(list(parsed[0].keys())))
            km_id = parsed[0].get('killmail_id', 'N/A')
            print('Sample killmail_id: ' + str(km_id))
            zkb = parsed[0].get('zkb', {})
            print('Sample zkb totalValue: ' + str(zkb.get('totalValue', 'N/A')))
except Exception as e:
    print('Kills error: ' + str(e))

# Test losses endpoint
time.sleep(3)
url = 'https://zkillboard.com/api/corporationID/98754582/losses/pastSeconds/345600/'
print('Testing: ' + url)
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = gzip.decompress(resp.read())
        parsed = json.loads(data.decode('utf-8', errors='ignore'))
        print('Losses returned: ' + str(len(parsed)) + ' records')
        if parsed and len(parsed) > 0:
            print('First record keys: ' + str(list(parsed[0].keys())))
            km_id = parsed[0].get('killmail_id', 'N/A')
            print('Sample killmail_id: ' + str(km_id))
except Exception as e:
    print('Losses error: ' + str(e))

print('Test complete.')
