import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
console_ip = "192.241.248.242"
username = "nova.cofounder@gmail.com"
password = "Fr34k3r!123123"
mfa_token = "700096"

print("Logging in with MFA token 123030...")
resp = session.post(
    f"https://{console_ip}/api/auth/login",
    json={"username": username, "password": password, "token": mfa_token, "remember": True},
    timeout=15, verify=False
)

if resp.status_code != 200:
    print(f"Login failed: {resp.status_code}")
    print(resp.text[:500])
    exit(1)

print("Logged in!")
print("=== FRESH COMPREHENSIVE SCAN ===")

# 1. Full device details
print("=== DEVICES (Detailed) ===")
devices_resp = session.get(f"https://{console_ip}/proxy/network/api/s/default/stat/device", timeout=20, verify=False)
if devices_resp.status_code == 200:
    devices = devices_resp.json().get('data', [])
    print(f"Total devices: {len(devices)}\n")
    
    for dev in devices:
        name = dev.get('name', 'Unknown')
        model = dev.get('model', 'Unknown')
        mac = dev.get('mac', 'N/A')
        ip = dev.get('ip', 'N/A')
        version = dev.get('version', 'N/A')
        uptime = dev.get('uptime', 0)
        num_sta = dev.get('num_sta', 0)
        adopted = dev.get('adopted', False)
        disconnected = dev.get('disconnected', False)
        
        radio_table = dev.get('radio_table', [])
        
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
                print(f"    Noise: {radio.get('noise', 'N/A')} dBm")
                print(f"    Satisfaction: {radio.get('satisfaction', 'N/A')}")
        
        # Port table (for switches)
        port_table = dev.get('port_table', [])
        if port_table:
            print(f"  Ports: {len(port_table)}")
            for port in port_table[:5]:
                print(f"    Port {port.get('port_idx', '?')}: {port.get('name', 'N/A')} - {port.get('op_mode', 'N/A')} - PoE: {port.get('poe_enable', False)}")
        
        # TX retry details
        tx_retries = dev.get('stat', {}).get('tx_retries', 0)
        tx_packets = dev.get('stat', {}).get('tx_packets', 1)
        if tx_packets > 0:
            retry_pct = (tx_retries / tx_packets) * 100
            print(f"  TX Retry Rate: {retry_pct:.2f}%")
        
        print()

# 2. WLAN detailed config
print("\n=== WLAN CONFIG (Detailed) ===")
wlan_resp = session.get(f"https://{console_ip}/proxy/network/api/s/default/rest/wlanconf", timeout=15, verify=False)
if wlan_resp.status_code == 200:
    wlans = wlan_resp.json().get('data', [])
    for wlan in wlans:
        print(f"SSID: {wlan.get('name', 'N/A')}")
        print(f"  Security: {wlan.get('security', 'N/A')}")
        print(f"  WPA Mode: {wlan.get('wpa_mode', 'N/A')}")
        print(f"  WPA3: {wlan.get('wpa3_support', False)}")
        print(f"  Band Steering: {wlan.get('bssiante', 'disabled')}")
        print(f"  Min RSSI: {wlan.get('min_rssi_enabled', False)} (threshold: {wlan.get('min_rssi', 'N/A')})")
        print(f"  VLAN: {wlan.get('vlan_enabled', False)} (ID: {wlan.get('vlan', 'N/A')})")
        print(f"  Is Guest: {wlan.get('is_guest', False)}")
        print(f"  Hide SSID: {wlan.get('hide_ssid', False)}")
        print(f"  MAC Filter: {wlan.get('mac_filter_enabled', False)}")
        print(f"  Multicast Enhance: {wlan.get('mcastenhance_enabled', False)}")
        print()

# 3. Rogue APs
print("\n=== ROGUE APs (Interference Sources) ===")
rogue_resp = session.get(f"https://{console_ip}/proxy/network/api/s/default/stat/rogueap", timeout=15, verify=False)
if rogue_resp.status_code == 200:
    rogues = rogue_resp.json().get('data', [])
    if rogues:
        print(f"Found {len(rogues)} rogue/interfering APs:")
        for r in rogues[:15]:
            print(f"  {r.get('ssid', 'Hidden')} ({r.get('bssid', 'N/A')}) - Ch {r.get('channel', 'N/A')} - Signal: {r.get('rssi', 'N/A')} dBm - Is Rogue: {r.get('is_rogu', False)}")
    else:
        print("No rogue APs detected")

# 4. Client details
print("\n=== CLIENT DETAILS ===")
clients_resp = session.get(f"https://{console_ip}/proxy/network/api/s/default/stat/sta", timeout=15, verify=False)
if clients_resp.status_code == 200:
    clients = clients_resp.json().get('data', [])
    print(f"Total clients: {len(clients)}\n")
    
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
        ap_name = ap_mac
        for dev in devices:
            if dev.get('mac') == ap_mac:
                ap_name = dev.get('name', ap_mac)
                break
        
        print(f"\n  {ap_name}: {len(clist)} clients")
        weak_clients = [c for c in clist if c.get('rssi', 0) < -70]
        if weak_clients:
            print(f"    ⚠️  {len(weak_clients)} weak signal clients (< -70 dBm):")
            for c in weak_clients[:5]:
                hostname = c.get('hostname', c.get('name', 'Unknown'))
                print(f"      {hostname}: {c.get('rssi', 'N/A')} dBm")
        
        # Count by band
        band2g = len([c for c in clist if c.get('channel', 0) <= 14])
        band5g = len([c for c in clist if c.get('channel', 0) > 14])
        print(f"    Distribution: {band2g} on 2.4GHz, {band5g} on 5GHz")

# 5. DPI / Traffic
print("\n=== DPI (Deep Packet Inspection) ===")
dpi_resp = session.get(f"https://{console_ip}/proxy/network/api/s/default/stat/dpi", timeout=15, verify=False)
if dpi_resp.status_code == 200:
    dpi = dpi_resp.json().get('data', [])
    if dpi:
        print(f"DPI categories tracked: {len(dpi)}")
        sorted_dpi = sorted(dpi, key=lambda x: x.get('rx_bytes', 0) + x.get('tx_bytes', 0), reverse=True)
        for d in sorted_dpi[:5]:
            rx = d.get('rx_bytes', 0) / (1024*1024)
            tx = d.get('tx_bytes', 0) / (1024*1024)
            print(f"  {d.get('catname', 'Unknown')}: {rx:.1f} MB down / {tx:.1f} MB up")
    else:
        print("DPI not enabled or no data")

print("\n=== SCAN COMPLETE ===")
