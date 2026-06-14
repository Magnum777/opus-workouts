import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
console_ip = "192.241.248.242"
username = "nova.cofounder@gmail.com"
password = "Fr34k3r!123123"
mfa_token = "009332"

# Login
resp = session.post(
    f"https://{console_ip}/api/auth/login",
    json={"username": username, "password": password, "token": mfa_token, "remember": True},
    timeout=15, verify=False
)

if resp.status_code != 200:
    print(f"Login failed: {resp.status_code}")
    print(resp.text[:500])
    exit(1)

print("=== FRESH COMPREHENSIVE SCAN ===\n")

# 1. Full device details
print("=== DEVICES (Detailed) ===")
devices_resp = session.get(f"https://{console_ip}/proxy/network/api/s/default/stat/device", timeout=20, verify=False)
if devices_resp.status_code == 200:
    devices = devices_resp.json().get('data', [])
    print(f"Total devices: {len(devices)}\n")
    
    for dev in devices:
        name = dev.get('name', 'Unknown')
        model = dev.get('model', 'Unknown')
        dev_type = dev.get('type', 'unknown')
        mac = dev.get('mac', 'N/A')
        ip = dev.get('ip', 'N/A')
        version = dev.get('version', 'N/A')
        uptime = dev.get('uptime', 0)
        num_sta = dev.get('num_sta', 0)
        adopted = dev.get('adopted', False)
        disconnected = dev.get('disconnected', False)
        
        # Radio details
        radio_table = dev.get('radio_table', [])
        radio_na = dev.get('radio_na', {})  # 5GHz
        radio_ng = dev.get('radio_ng', {})  # 2.4GHz
        
        print(f"Device: {name} ({model})")
        print(f"  MAC: {mac} | IP: {ip}")
        print(f"  Status: {'ONLINE' if adopted and not disconnected else 'OFFLINE'}")
        print(f"  Firmware: {version}")
        print(f"  Uptime: {uptime//86400}d {(uptime%86400)//3600}h")
        print(f"  Clients: {num_sta}")
        
        if radio_table:
            for i, radio in enumerate(radio_table):
                band = "5GHz" if radio.get('is_11ac') or radio.get('is_11ax') or radio.get('is_11be') else "2.4GHz"
                print(f"  Radio {i} ({band}):")
                print(f"    Channel: {radio.get('channel', 'N/A')} (Width: {radio.get('ht', 'N/A')})")
                print(f"    TX Power: {radio.get('tx_power', 'N/A')} dBm")
                print(f"    Clients: {radio.get('num_sta', 0)}")
                print(f"    Noise Floor: {radio.get('noise', 'N/A')} dBm")
                print(f"    Satisfaction: {radio.get('satisfaction', 'N/A')}")
        
        # Mesh info
        if dev.get('meshvap_table'):
            print(f"  Mesh links: {len(dev.get('meshvap_table', []))}")
        
        # Port table (for switches)
        port_table = dev.get('port_table', [])
        if port_table:
            print(f"  Ports: {len(port_table)}")
            for port in port_table[:5]:  # First 5 ports
                print(f"    Port {port.get('port_idx', '?')}: {port.get('name', 'N/A')} - {port.get('op_mode', 'N/A')} - PoE: {port.get('poe_enable', False)}")
        
        # TX retry details
        tx_retries = dev.get('stat', {}).get('tx_retries', 0)
        tx_packets = dev.get('stat', {}).get('tx_packets', 1)
        rx_errors = dev.get('stat', {}).get('rx_errors', 0)
        if tx_packets > 0:
            retry_pct = (tx_retries / tx_packets) * 100
            print(f"  TX Retry Rate: {retry_pct:.2f}% (retries: {tx_retries}, packets: {tx_packets})")
        if rx_errors > 0:
            print(f"  RX Errors: {rx_errors}")
        
        print()

# 2. WLAN detailed config
print("\n=== WLAN CONFIG (Detailed) ===")
wlan_resp = session.get(f"https://{console_ip}/proxy/network/api/s/default/rest/wlanconf", timeout=15, verify=False)
if wlan_resp.status_code == 200:
    wlans = wlan_resp.json().get('data', [])
    for wlan in wlans:
        print(f"SSID: {wlan.get('name', 'N/A')}")
        print(f"  ID: {wlan.get('_id', 'N/A')[:8]}...")
        print(f"  Enabled: {wlan.get('enabled', False)}")
        print(f"  Security: {wlan.get('security', 'N/A')}")
        print(f"  WPA Mode: {wlan.get('wpa_mode', 'N/A')}")
        print(f"  WPA3: {wlan.get('wpa3_support', False)}")
        print(f"  PMF: {wlan.get('pmf_mode', 'N/A')}")
        print(f"  Band Steering: {wlan.get('bssiante', 'disabled')}")
        print(f"  Min RSSI: {wlan.get('min_rssi_enabled', False)} (threshold: {wlan.get('min_rssi', 'N/A')})")
        print(f"  VLAN: {wlan.get('vlan_enabled', False)} (ID: {wlan.get('vlan', 'N/A')})")
        print(f"  VLAN Bridging: {wlan.get('is_guest', False)}")
        print(f"  11r (Fast Roaming): {wlan.get('roaming_vlan_id', 'N/A')}")
        print(f"  Rates: 2.4GHz min={wlan.get('minrate_ng_enabled', False)}, 5GHz min={wlan.get('minrate_na_enabled', False)}")
        print(f"  Hide SSID: {wlan.get('hide_ssid', False)}")
        print(f"  MAC Filter: {wlan.get('mac_filter_enabled', False)}")
        print(f"  Multicast Enhancement: {wlan.get('mcastenhance_enabled', False)}")
        print(f"  DTIM: 2.4G={wlan.get('dtim_ng', 'N/A')}, 5G={wlan.get('dtim_na', 'N/A')}")
        print(f"  Schedule: {wlan.get('schedule_enabled', False)} {wlan.get('schedule', [])}")
        print()

# 3. Network settings
print("\n=== NETWORK SETTINGS ===")
settings_resp = session.get(f"https://{console_ip}/proxy/network/api/s/default/rest/setting", timeout=15, verify=False)
if settings_resp.status_code == 200:
    settings = settings_resp.json().get('data', [])
    for s in settings:
        key = list(s.keys())[0] if s else 'unknown'
        print(f"Setting: {key}")
        if 'mgmt' in key.lower():
            print(f"  Auto Upgrade: {s.get(key, {}).get('auto_upgrade', False)}")
            print(f"  SSH Enabled: {s.get(key, {}).get('ssh_enabled', False)}")
        if 'guest_access' in key.lower():
            print(f"  Guest Portal: {s.get(key, {}).get('portal_enabled', False)}")
            print(f"  Portal Customization: {s.get(key, {}).get('portal_customization', 'N/A')}")
        if 'usg' in key.lower():
            print(f"  DPI: {s.get(key, {}).get('dpi_enabled', False)}")
            print(f"  IDS/IPS: {s.get(key, {}).get('ips_enabled', False)}")
        print()

# 4. Rogue APs
print("\n=== ROGUE APs (Interference Sources) ===")
rogue_resp = session.get(f"https://{console_ip}/proxy/network/api/s/default/stat/rogueap", timeout=15, verify=False)
if rogue_resp.status_code == 200:
    rogues = rogue_resp.json().get('data', [])
    if rogues:
        print(f"Found {len(rogues)} rogue/interfering APs:")
        for r in rogues[:10]:
            print(f"  {r.get('ssid', 'Hidden')} ({r.get('bssid', 'N/A')}) - Ch {r.get('channel', 'N/A')} - Signal: {r.get('rssi', 'N/A')} dBm")
    else:
        print("No rogue APs detected")

# 5. Client details
print("\n=== CLIENT DETAILS ===")
clients_resp = session.get(f"https://{console_ip}/proxy/network/api/s/default/stat/sta", timeout=15, verify=False)
if clients_resp.status_code == 200:
    clients = clients_resp.json().get('data', [])
    print(f"Total clients: {len(clients)}\n")
    
    # Group by band
    clients_2g = [c for c in clients if c.get('channel', 0) <= 14]
    clients_5g = [c for c in clients if c.get('channel', 0) > 14]
    
    print(f"2.4GHz clients: {len(clients_2g)}")
    print(f"5GHz clients: {len(clients_5g)}")
    
    # Group by AP
    ap_clients = {}
    for c in clients:
        ap_mac = c.get('ap_mac', 'Unknown')
        if ap_mac not in ap_clients:
            ap_clients[ap_mac] = []
        ap_clients[ap_mac].append(c)
    
    print(f"\nClients per AP:")
    for ap_mac, clist in sorted(ap_clients.items(), key=lambda x: -len(x[1])):
        # Get AP name from device list
        ap_name = ap_mac
        for dev in devices:
            if dev.get('mac') == ap_mac:
                ap_name = dev.get('name', ap_mac)
                break
        
        print(f"\n  {ap_name}: {len(clist)} clients")
        # Show worst signal clients
        weak_clients = [c for c in clist if c.get('rssi', 0) < -70]
        if weak_clients:
            print(f"    ⚠️  {len(weak_clients)} weak signal clients (< -70 dBm):")
            for c in weak_clients[:3]:
                hostname = c.get('hostname', c.get('name', 'Unknown'))
                print(f"      {hostname}: {c.get('rssi', 'N/A')} dBm on Ch {c.get('channel', 'N/A')}")

# 6. DPI / Traffic stats
print("\n=== DPI (Deep Packet Inspection) ===")
dpi_resp = session.get(f"https://{console_ip}/proxy/network/api/s/default/stat/dpi", timeout=15, verify=False)
if dpi_resp.status_code == 200:
    dpi = dpi_resp.json().get('data', [])
    if dpi:
        print(f"DPI categories tracked: {len(dpi)}")
        # Top bandwidth consumers
        sorted_dpi = sorted(dpi, key=lambda x: x.get('rx_bytes', 0) + x.get('tx_bytes', 0), reverse=True)
        for d in sorted_dpi[:5]:
            rx = d.get('rx_bytes', 0) / (1024*1024)
            tx = d.get('tx_bytes', 0) / (1024*1024)
            print(f"  {d.get('catname', 'Unknown')}: {rx:.1f} MB down / {tx:.1f} MB up")
    else:
        print("DPI not enabled or no data")

# 7. Alerts / Events
print("\n=== RECENT EVENTS ===")
events_resp = session.get(f"https://{console_ip}/proxy/network/api/s/default/stat/event", params={"_limit": 20}, timeout=15, verify=False)
if events_resp.status_code == 200:
    events = events_resp.json().get('data', [])
    for e in events[:10]:
        msg = e.get('msg', 'N/A')
        if 'connected' in msg.lower() or 'disconnected' in msg.lower() or 'adopted' in msg.lower() or 'upgrade' in msg.lower() or 'rogue' in msg.lower() or 'interference' in msg.lower():
            print(f"  {e.get('datetime', 'N/A')}: {msg}")

print("\n=== SCAN COMPLETE ===")
