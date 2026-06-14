import requests
import json

headers = {'X-Api-Key': 'M_9VaI2JRSa4gWtFHzlA-rXK0r55m_KA'}

def api_get(path):
    url = f'https://api.ui.com/ea{path}'
    resp = requests.get(url, headers=headers, timeout=20)
    if resp.status_code == 200:
        return resp.json()
    print(f'ERROR {resp.status_code}: {resp.text[:200]}')
    return None

# Get sites
sites = api_get('/sites')
if sites and 'data' in sites:
    print(f'=== SITES ({len(sites["data"])}) ===')
    for site in sites['data']:
        sid = site.get('_id')
        name = site.get('name', 'N/A')
        host = site.get('host_name', 'N/A')
        stype = site.get('type', 'N/A')
        print(f'\nSite: {name}')
        print(f'  ID: {sid}')
        print(f'  Host: {host}')
        print(f'  Type: {stype}')
        print(f'  Description: {site.get("desc", "N/A")}')
        print(f'  Health: {site.get("health", "N/A")}')
        
        # Get devices for this site
        print(f'\n  Fetching devices...')
        devices = api_get(f'/sites/{sid}/devices')
        if devices and 'data' in devices:
            print(f'  Devices: {len(devices["data"])}')
            for dev in devices['data']:
                print(f'    {dev.get("name", "N/A")} ({dev.get("type", "N/A")}) - {dev.get("mac", "N/A")}')
                print(f'      Status: {dev.get("state", {}).get("ip", "N/A")}')
                print(f'      FW: {dev.get("version", "N/A")}')
                print(f'      Uptime: {dev.get("state", {}).get("uptime", 0)//86400} days')
        
        # Get clients
        print(f'\n  Fetching clients...')
        clients = api_get(f'/sites/{sid}/clients')
        if clients and 'data' in clients:
            print(f'  Active clients: {len(clients["data"])}')
        
        # Get WLANS
        print(f'\n  Fetching WiFi...')
        wlans = api_get(f'/sites/{sid}/wlans')
        if wlans and 'data' in wlans:
            print(f'  WiFi networks: {len(wlans["data"])}')
            for wlan in wlans['data']:
                print(f'    {wlan.get("name", "N/A")}: enabled={wlan.get("enabled", False)} band={wlan.get("bandsteering_mode", "N/A")}')
        
        # Get health
        print(f'\n  Fetching health...')
        health = api_get(f'/sites/{sid}/health')
        if health and 'data' in health:
            print(f'  Subsystems: {len(health["data"])}')
            for h in health['data']:
                print(f'    {h.get("subsystem", "N/A")}: status={h.get("status", "N/A")}')
        
        # Get traffic rules
        print(f'\n  Fetching traffic rules...')
        rules = api_get(f'/sites/{sid}/trafficrules')
        if rules and 'data' in rules:
            print(f'  Traffic rules: {len(rules["data"])}')
        elif rules is None:
            print('  Traffic rules: API error or unsupported')
