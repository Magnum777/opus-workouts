import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console_ip = "192.241.248.242"
username = "nova.cofounder@gmail.com"
password = "Fr34k3r!123123"
mfa_token = "009332"

session = requests.Session()

print("=== UniFi Console Login with MFA ===")
try:
    # Step 1: Login with MFA
    resp = session.post(
        f"https://{console_ip}/api/auth/login",
        json={
            "username": username,
            "password": password,
            "token": mfa_token,
            "remember": True
        },
        timeout=15,
        verify=False
    )
    print(f"Login response: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"SUCCESS!")
        print(f"Token: {data.get('csrfToken', 'N/A')[:20]}...")
        print(f"Role: {data.get('role', 'N/A')}")
        print()
        
        # Step 2: Get all devices with full details
        print("=== DEVICES ===")
        devices_resp = session.get(
            f"https://{console_ip}/proxy/network/api/s/default/stat/device",
            timeout=20,
            verify=False
        )
        if devices_resp.status_code == 200:
            devices = devices_resp.json().get('data', [])
            print(f"Total devices: {len(devices)}")
            
            aps = []
            switches = []
            gateways = []
            
            for dev in devices:
                dev_type = dev.get('type', 'unknown')
                name = dev.get('name', 'Unknown')
                model = dev.get('model', 'Unknown')
                mac = dev.get('mac', 'N/A')
                ip = dev.get('ip', 'N/A')
                adopted = dev.get('adopted', False)
                disconnected = dev.get('disconnected', False)
                
                info = {
                    'name': name,
                    'model': model,
                    'mac': mac,
                    'ip': ip,
                    'status': 'ONLINE' if adopted and not disconnected else 'OFFLINE/DISCONNECTED',
                    'firmware': dev.get('version', 'N/A'),
                    'uptime': dev.get('uptime', 0),
                    'clients': dev.get('num_sta', 0),
                    'tx_retries': dev.get('stat', {}).get('tx_retries', 0),
                    'tx_packets': dev.get('stat', {}).get('tx_packets', 1),
                }
                
                if 'uap' in dev_type or 'ap' in name.lower():
                    # AP-specific data
                    radio_table = dev.get('radio_table', [])
                    for radio in radio_table:
                        if radio.get('is_11ac') or radio.get('is_11ax'):
                            info['5g_channel'] = radio.get('channel', 'N/A')
                            info['5g_width'] = radio.get('ht', 'N/A')
                            info['5g_power'] = radio.get('tx_power', 'N/A')
                            info['5g_clients'] = radio.get('num_sta', 0)
                        else:
                            info['2g_channel'] = radio.get('channel', 'N/A')
                            info['2g_width'] = radio.get('ht', 'N/A')
                            info['2g_power'] = radio.get('tx_power', 'N/A')
                            info['2g_clients'] = radio.get('num_sta', 0)
                    aps.append(info)
                elif 'usw' in dev_type or 'switch' in name.lower():
                    switches.append(info)
                elif 'ugw' in dev_type or 'gateway' in name.lower() or 'usg' in dev_type:
                    gateways.append(info)
                else:
                    # Unknown type, check model
                    if 'UAP' in model or 'U6' in model or 'U7' in model:
                        aps.append(info)
                    elif 'USW' in model:
                        switches.append(info)
                    elif 'UDM' in model or 'USG' in model or 'UXG' in model:
                        gateways.append(info)
            
            print(f"\n--- Access Points ({len(aps)}) ---")
            for ap in aps:
                print(f"  {ap['name']} ({ap['model']})")
                print(f"    Status: {ap['status']}")
                print(f"    MAC: {ap['mac']}")
                print(f"    IP: {ap['ip']}")
                print(f"    Firmware: {ap['firmware']}")
                print(f"    Clients: {ap['clients']}")
                print(f"    5GHz: Ch {ap.get('5g_channel', 'N/A')} / Width: {ap.get('5g_width', 'N/A')}")
                print(f"    2.4GHz: Ch {ap.get('2g_channel', 'N/A')} / Width: {ap.get('2g_width', 'N/A')}")
                tx_retry_pct = (ap['tx_retries'] / max(ap['tx_packets'], 1)) * 100
                print(f"    TX Retry Rate: {tx_retry_pct:.2f}%")
                print()
            
            print(f"--- Switches ({len(switches)}) ---")
            for sw in switches:
                print(f"  {sw['name']} ({sw['model']}) - {sw['status']}")
                print(f"    Clients: {sw['clients']}")
                print()
            
            print(f"--- Gateways ({len(gateways)}) ---")
            for gw in gateways:
                print(f"  {gw['name']} ({gw['model']}) - {gw['status']}")
                print(f"    Clients: {gw['clients']}")
                print()
            
            # Step 3: Get WiFi settings
            print("=== WIFI SETTINGS ===")
            wlan_resp = session.get(
                f"https://{console_ip}/proxy/network/api/s/default/rest/wlanconf",
                timeout=15,
                verify=False
            )
            if wlan_resp.status_code == 200:
                wlans = wlan_resp.json().get('data', [])
                for wlan in wlans:
                    print(f"  SSID: {wlan.get('name', 'N/A')}")
                    print(f"    Enabled: {wlan.get('enabled', False)}")
                    print(f"    Security: {wlan.get('security', 'N/A')}")
                    print(f"    Band Steering: {wlan.get('bssiante', 'N/A')}")
                    print(f"    Min RSSI: {wlan.get('min_rssi_enabled', False)} -> {wlan.get('min_rssi', 'N/A')} dBm")
                    print(f"    VLAN: {wlan.get('vlan_enabled', False)}")
                    print()
            
            # Step 4: Get active clients
            print("=== ACTIVE CLIENTS ===")
            clients_resp = session.get(
                f"https://{console_ip}/proxy/network/api/s/default/stat/sta",
                timeout=15,
                verify=False
            )
            if clients_resp.status_code == 200:
                clients = clients_resp.json().get('data', [])
                print(f"Total clients: {len(clients)}")
                
                # Count by AP
                ap_client_counts = {}
                for client in clients:
                    ap_mac = client.get('ap_mac', 'Unknown')
                    ap_client_counts[ap_mac] = ap_client_counts.get(ap_mac, 0) + 1
                
                print("\nClient distribution by AP:")
                for mac, count in sorted(ap_client_counts.items(), key=lambda x: -x[1]):
                    # Find AP name
                    ap_name = mac
                    for ap in aps:
                        if ap['mac'] == mac:
                            ap_name = ap['name']
                            break
                    print(f"  {ap_name}: {count} clients")
            
            # Step 5: Get health
            print("\n=== HEALTH STATUS ===")
            health_resp = session.get(
                f"https://{console_ip}/proxy/network/api/s/default/stat/health",
                timeout=15,
                verify=False
            )
            if health_resp.status_code == 200:
                health = health_resp.json().get('data', [])
                for h in health:
                    print(f"  {h.get('subsystem', 'N/A')}: {h.get('status', 'N/A')}")
                    if 'num_adopted' in h:
                        print(f"    Adopted: {h.get('num_adopted', 0)}, Disconnected: {h.get('num_disconnected', 0)}, Pending: {h.get('num_pending', 0)}")
                    if 'num_user' in h:
                        print(f"    Users: {h.get('num_user', 0)}, Guests: {h.get('num_guest', 0)}")
                    if 'tx_retries' in h:
                        print(f"    TX Retries: {h.get('tx_retries', 0)}")
        else:
            print(f"Failed to get devices: {devices_resp.status_code}")
    else:
        print(f"Login failed: {resp.status_code}")
        print(resp.text[:500])
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
