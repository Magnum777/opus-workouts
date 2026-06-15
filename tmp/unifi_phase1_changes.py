"""
UniFi Quick Change — Push Phase 1 via API once authenticated
"""
import requests
import json
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://192.241.248.242"

def make_changes(session):
    """Push Phase 1 changes."""
    changes_made = []
    
    # 1. Enable band steering on all SSIDs
    print("\n[1/5] Enabling band steering...")
    # Get list of WLANs
    r = session.get(f"{BASE_URL}/proxy/network/api/s/default/rest/wlan", verify=False, timeout=30)
    if r.status_code == 200:
        wlans = r.json().get('data', [])
        for wlan in wlans:
            wlan_id = wlan['_id']
            name = wlan.get('name', 'unknown')
            # Update band steering
            update = {"bandsteering_mode": "balanced"}
            r2 = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlan/{wlan_id}", 
                           json=update, verify=False, timeout=30)
            if r2.status_code == 200:
                print(f"  ✓ {name}: band steering ON")
                changes_made.append(f"band_steering:{name}")
            else:
                print(f"  ✗ {name}: failed ({r2.status_code})")
    
    # 2. Set minimum RSSI to -70
    print("\n[2/5] Setting minimum RSSI to -70...")
    for wlan in wlans:
        wlan_id = wlan['_id']
        name = wlan.get('name', 'unknown')
        update = {"min_rssi_enabled": True, "min_rssi": -70}
        r2 = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlan/{wlan_id}", 
                       json=update, verify=False, timeout=30)
        if r2.status_code == 200:
            print(f"  ✓ {name}: min RSSI -70")
            changes_made.append(f"min_rssi:{name}")
        else:
            print(f"  ✗ {name}: failed ({r2.status_code})")
    
    # 3. Fix SAP 5GHz channel
    print("\n[3/5] Fixing SAP 5GHz (Ch 149, 40MHz)...")
    # Find SAP device
    r = session.get(f"{BASE_URL}/proxy/network/api/s/default/stat/device", verify=False, timeout=30)
    if r.status_code == 200:
        devices = r.json().get('data', [])
        sap = None
        for d in devices:
            if 'UAP6MP' in str(d.get('model', '')) or d.get('name', '').upper() == 'SAP':
                sap = d
                break
        
        if sap:
            device_id = sap['_id']
            # Update radio 1 (5GHz)
            update = {
                "radio_table": [
                    {},  # radio 0 (2.4GHz) - leave as is
                    {"channel": 149, "ht": 40}  # radio 1 (5GHz)
                ]
            }
            r2 = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/device/{device_id}", 
                           json=update, verify=False, timeout=30)
            if r2.status_code == 200:
                print(f"  ✓ SAP: Ch 149 / 40MHz")
                changes_made.append("sap_5ghz:ch149_40mhz")
            else:
                print(f"  ✗ SAP: failed ({r2.status_code})")
        else:
            print("  ! SAP not found")
    
    # 4. Enable DPI
    print("\n[4/5] Enabling DPI...")
    # DPI is a site setting
    update = {"dpi_enabled": True}
    r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/setting", 
                   json=update, verify=False, timeout=30)
    if r.status_code == 200:
        print("  ✓ DPI enabled")
        changes_made.append("dpi:enabled")
    else:
        print(f"  ✗ DPI failed ({r.status_code})")
    
    # 5. Enable multicast enhancement on all SSIDs
    print("\n[5/5] Enabling multicast enhancement...")
    for wlan in wlans:
        wlan_id = wlan['_id']
        name = wlan.get('name', 'unknown')
        update = {"mcastenhance_enabled": True}
        r2 = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlan/{wlan_id}", 
                       json=update, verify=False, timeout=30)
        if r2.status_code == 200:
            print(f"  ✓ {name}: multicast ON")
            changes_made.append(f"multicast:{name}")
        else:
            print(f"  ✗ {name}: failed ({r2.status_code})")
    
    return changes_made


if __name__ == '__main__':
    # Load session cookies from file (created by auth script)
    import pickle
    try:
        with open('tmp/unifi_session.pkl', 'rb') as f:
            session = pickle.load(f)
        print("Loaded saved session")
        changes = make_changes(session)
        print(f"\n{'='*60}")
        print(f"Phase 1 complete: {len(changes)} changes made")
        for c in changes:
            print(f"  ✓ {c}")
    except FileNotFoundError:
        print("No saved session found. Need to authenticate first.")
        sys.exit(1)
