"""
UniFi Phase 3 -- VLANs + Guest Portal (Fixed)
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
    print("PHASE 3 -- VLANs + GUEST PORTAL (FIXED)")
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
        
        # Step 1: Get existing networks
        print("[1/4] Checking existing networks...")
        r = await controller.request(ApiRequest(
            method="get",
            path="/rest/networkconf",
            data={}
        ))
        print(f"  Response type: {type(r)}")
        
        # Step 2: Create VLANs with unique IDs
        print("\n[2/4] Creating VLAN networks...")
        
        networks = [
            {"name": "sojourn-office", "vlan_id": 10, "purpose": "corporate", "dhcpd_start": "192.168.10.10", "dhcpd_stop": "192.168.10.250", "dhcpd_enabled": True},
            {"name": "sojourn-prod", "vlan_id": 20, "purpose": "corporate", "dhcpd_start": "192.168.20.10", "dhcpd_stop": "192.168.20.250", "dhcpd_enabled": True},
            {"name": "sojourn-guest", "vlan_id": 30, "purpose": "guest", "dhcpd_start": "192.168.30.10", "dhcpd_stop": "192.168.30.250", "dhcpd_enabled": True},
        ]
        
        for net in networks:
            print(f"  Creating {net['name']} (VLAN {net['vlan_id']})...")
            try:
                await controller.request(ApiRequest(
                    method="post",
                    path="/rest/networkconf",
                    data=net
                ))
                print(f"    [OK] Created")
                changes.append(f"network:{net['name']} ({net['vlan_id']})")
            except Exception as e:
                print(f"    [FAIL] {e}")
        
        # Step 3: Configure guest portal (fixed expire_unit)
        print("\n[3/4] Configuring guest portal...")
        
        guest_config = {
            "key": "guest_access",
            "enabled": True,
            "auth": "none",
            "expire": 720,
            "expire_number": 12,
            "expire_unit": 1,  # hours, not seconds
            "download_enabled": True,
            "download_limit": 5120,  # 5 Mbps
            "upload_enabled": True,
            "upload_limit": 5120,  # 5 Mbps
            "redirect_enabled": False,
            "portal_enabled": True,
            "template_engine": "angular",
            "portal_customization": {
                "title": "Welcome to Sojourn Church",
                "welcome_text": "Guest WiFi Access",
                "tos_text": "By connecting, you agree to use this network for lawful purposes only. Do not transmit sensitive information. Access limited to 12 hours.",
                "button_text": "Connect to Internet",
                "footer_text": "Trouble? sojournchurchtech@gmail.com"
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
        
        # Step 4: Map WLANs to networks (after networks created)
        print("\n[4/4] Mapping WLANs to networks...")
        
        await controller.wlans.update()
        wlans = list(controller.wlans.values())
        
        # Get network IDs
        r = await controller.request(ApiRequest(
            method="get",
            path="/rest/networkconf",
            data={}
        ))
        
        # Find network IDs by name
        network_ids = {}
        if hasattr(r, 'data'):
            for net in r.data:
                name = net.get('name', '')
                if name:
                    network_ids[name] = net.get('_id', '')
        
        print(f"  Found networks: {list(network_ids.keys())}")
        
        for wlan in wlans:
            name = wlan.name
            # Map to network
            target_net = None
            if name == 'sojourn':
                target_net = network_ids.get('sojourn-prod', '')
            elif name == 'sojourn-office':
                target_net = network_ids.get('sojourn-office', '')
            elif name == 'sojourn-guest':
                target_net = network_ids.get('sojourn-guest', '')
            
            if target_net:
                print(f"  Mapping {name} to network {target_net[:8]}...")
                try:
                    wlan.raw['networkconf_id'] = target_net
                    await controller.request(ApiRequest(
                        method="put",
                        path=f"/rest/wlanconf/{wlan.id}",
                        data=wlan.raw
                    ))
                    print(f"    [OK] Mapped")
                    changes.append(f"wlan_map:{name}")
                except Exception as e:
                    print(f"    [FAIL] {e}")
        
        print("\n" + "="*60)
        print(f"PHASE 3 COMPLETE: {len(changes)} changes")
        print("="*60)
        for c in changes:
            print(f"  [OK] {c}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
