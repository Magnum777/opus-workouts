"""
UniFi Phase 3 -- VLANs + Guest Portal
Creates VLANs, maps WLANs, configures guest portal
"""
import asyncio
import aiohttp
import aiounifi
from aiounifi.controller import Controller
from aiounifi.models.configuration import Configuration
from aiounifi.models.api import ApiRequest
import ssl

async def main():
    print("="*60)
    print("PHASE 3 -- VLANs + GUEST PORTAL")
    print("="*60)
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))
    
    try:
        config = Configuration(
            session=session,
            host="192.241.248.242",
            username="Nova",
            password="N0v4!123N0v4!12",
            site="default",
            ssl_context=ssl_context,
            port=443
        )
        
        controller = Controller(config)
        await controller.login()
        print("[OK] Authenticated!\n")
        
        changes = []
        
        # Step 1: Create VLANs
        print("[1/4] Creating VLANs...")
        
        vlans = [
            {"name": "sojourn-office", "vlan_id": 10, "purpose": "corporate", "dhcpd_start": "192.168.10.10", "dhcpd_stop": "192.168.10.250", "dhcpd_enabled": True},
            {"name": "sojourn", "vlan_id": 20, "purpose": "corporate", "dhcpd_start": "192.168.20.10", "dhcpd_stop": "192.168.20.250", "dhcpd_enabled": True},
            {"name": "sojourn-guest", "vlan_id": 30, "purpose": "guest", "dhcpd_start": "192.168.30.10", "dhcpd_stop": "192.168.30.250", "dhcpd_enabled": True},
        ]
        
        for vlan in vlans:
            print(f"  Creating {vlan['name']} (VLAN {vlan['vlan_id']})...")
            try:
                await controller.request(ApiRequest(
                    method="post",
                    path="/rest/networkconf",
                    data=vlan
                ))
                print(f"    [OK] Created")
                changes.append(f"vlan:{vlan['name']} ({vlan['vlan_id']})")
            except Exception as e:
                print(f"    [FAIL] {e}")
        
        # Step 2: Map WLANs to VLANs
        print("\n[2/4] Mapping WLANs to VLANs...")
        
        await controller.wlans.update()
        wlans = list(controller.wlans.values())
        
        vlan_map = {
            'sojourn': 20,
            'sojourn-office': 10,
            'sojourn-guest': 30,
        }
        
        for wlan in wlans:
            name = wlan.name
            if name in vlan_map:
                vlan_id = vlan_map[name]
                print(f"  Mapping {name} to VLAN {vlan_id}...")
                try:
                    # Update WLAN with network_id
                    wlan.raw['networkconf_id'] = str(vlan_id)
                    await controller.request(ApiRequest(
                        method="put",
                        path=f"/rest/wlanconf/{wlan.id}",
                        data=wlan.raw
                    ))
                    print(f"    [OK] Mapped")
                    changes.append(f"wlan_vlan:{name} -> {vlan_id}")
                except Exception as e:
                    print(f"    [FAIL] {e}")
        
        # Step 3: Configure guest portal
        print("\n[3/4] Configuring guest portal...")
        
        guest_config = {
            "key": "guest_access",
            "enabled": True,
            "auth": "none",  # Hotspot with terms
            "restricted_subnet_1": "192.168.0.0/16",
            "restricted_subnet_2": "10.0.0.0/8",
            "restricted_subnet_3": "172.16.0.0/12",
            "expire": 720,  # 12 hours
            "expire_number": 12,
            "expire_unit": 3600,
            "download_enabled": True,
            "download_limit": 5120,  # 5 Mbps in kbps
            "upload_enabled": True,
            "upload_limit": 5120,  # 5 Mbps in kbps
            "redirect_enabled": False,
            "custom_ip": "",
            "ecosystem_enabled": False,
            "template_engine": "angular",
            "portal_enabled": True,
            "portal_use_hostname": False,
            "portal_hostname": "",
            "portal_use_https": False,
            "hotspot_id": "",
            "portal_customization": {
                "title": "Welcome to Sojourn Church",
                "welcome_text": "Guest WiFi Access",
                "tos_text": "By connecting to this network, you agree to use it for lawful purposes only. Do not transmit sensitive information over this public connection. Access is limited to 12 hours per session.",
                "button_text": "Connect to Internet",
                "footer_text": "Having trouble? Email sojournchurchtech@gmail.com",
                "logo_file": "",
                "background_color": "#ffffff",
                "text_color": "#333333",
                "link_color": "#0066cc",
                "button_color": "#0066cc",
                "button_text_color": "#ffffff"
            }
        }
        
        try:
            await controller.request(ApiRequest(
                method="put",
                path="/rest/setting/guest_access",
                data=guest_config
            ))
            print("  [OK] Guest portal configured")
            changes.append("guest_portal: configured")
        except Exception as e:
            print(f"  [FAIL] {e}")
        
        # Step 4: Verify
        print("\n[4/4] Verifying configuration...")
        await controller.devices.update()
        await controller.wlans.update()
        
        print(f"\n  WLANs:")
        for wlan in controller.wlans.values():
            print(f"    - {wlan.name}")
        
        print(f"\n  Devices:")
        for device in controller.devices.values():
            if device.name.upper() in ['YAP', 'OAP', 'CAP', 'SAP', 'FAP']:
                print(f"    - {device.name}: {len(device.raw.get('vap_table', []))} VAPs")
        
        print("\n" + "="*60)
        print(f"PHASE 3 COMPLETE: {len(changes)} changes")
        print("="*60)
        for c in changes:
            print(f"  [OK] {c}")
        
        print("\n[NOTE] Some settings may require manual verification in console:")
        print("  - Church logo upload")
        print("  - Portal HTML customization")
        print("  - WPA3/PMF settings")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
