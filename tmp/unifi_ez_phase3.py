"""
UniFi Phase 3 -- Using ez-unifi skill properly
"""
import asyncio
import aiohttp
import aiounifi
from aiounifi.controller import Controller
from aiounifi.models.configuration import Configuration
from aiounifi.models.api import ApiRequest
import ssl
import sys
import os

# Load env from ez-unifi skill
from dotenv import load_dotenv
load_dotenv('skills/ez-unifi/.env')

async def main():
    print("="*60)
    print("PHASE 3 -- VLANs + GUEST PORTAL (EZ-UNIFI)")
    print("="*60)
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))
    
    try:
        config = Configuration(
            session=session,
            host=os.environ.get('UNIFI_HOST', '192.241.248.242'),
            username=os.environ.get('UNIFI_USERNAME', 'Nova'),
            password=os.environ.get('UNIFI_PASSWORD', 'N0v4!123N0v4!12'),
            site=os.environ.get('UNIFI_SITE', 'default'),
            ssl_context=ssl_context,
            port=443
        )
        
        controller = Controller(config)
        await controller.login()
        print("[OK] Authenticated!\n")
        
        changes = []
        
        # Step 1: Create VLAN networks
        print("[1/3] Creating VLAN networks...")
        
        networks = [
            {
                "name": "sojourn-office",
                "vlan_id": 10,
                "purpose": "corporate",
                "ip_subnet": "192.168.10.1/24",
                "dhcpd_start": "192.168.10.10",
                "dhcpd_stop": "192.168.10.250",
                "dhcpd_enabled": True,
                "vlan_enabled": True,
                "networkgroup": "LAN"
            },
            {
                "name": "sojourn",
                "vlan_id": 20,
                "purpose": "corporate",
                "ip_subnet": "192.168.20.1/24",
                "dhcpd_start": "192.168.20.10",
                "dhcpd_stop": "192.168.20.250",
                "dhcpd_enabled": True,
                "vlan_enabled": True,
                "networkgroup": "LAN"
            },
            {
                "name": "sojourn-guest",
                "vlan_id": 30,
                "purpose": "guest",
                "ip_subnet": "192.168.30.1/24",
                "dhcpd_start": "192.168.30.10",
                "dhcpd_stop": "192.168.30.250",
                "dhcpd_enabled": True,
                "vlan_enabled": True,
                "networkgroup": "LAN"
            }
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
                changes.append(f"network:{net['name']}")
            except Exception as e:
                print(f"    [FAIL] {e}")
        
        # Step 2: Update WLANs to use new networks
        print("\n[2/3] Mapping WLANs to networks...")
        
        # First get network IDs
        r = await controller.request(ApiRequest(
            method="get",
            path="/rest/networkconf",
            data={}
        ))
        
        network_ids = {}
        if hasattr(r, 'data'):
            for net in r.data:
                name = net.get('name', '')
                network_ids[name] = net.get('_id', '')
        elif isinstance(r, dict) and 'data' in r:
            for net in r['data']:
                name = net.get('name', '')
                network_ids[name] = net.get('_id', '')
        
        print(f"  Available networks: {list(network_ids.keys())}")
        
        # Update WLANs
        await controller.wlans.update()
        wlans = list(controller.wlans.values())
        
        for wlan in wlans:
            name = wlan.name
            target_id = None
            
            if name == 'sojourn':
                target_id = network_ids.get('sojourn', '')
            elif name == 'sojourn-office':
                target_id = network_ids.get('sojourn-office', '')
            elif name == 'sojourn-guest':
                target_id = network_ids.get('sojourn-guest', '')
            
            if target_id:
                print(f"  Mapping {name} to network {target_id[:8]}...")
                try:
                    wlan.raw['networkconf_id'] = target_id
                    await controller.request(ApiRequest(
                        method="put",
                        path=f"/rest/wlanconf/{wlan.id}",
                        data=wlan.raw
                    ))
                    print(f"    [OK] Mapped")
                    changes.append(f"wlan_map:{name}")
                except Exception as e:
                    print(f"    [FAIL] {e}")
        
        # Step 3: Configure guest portal
        print("\n[3/3] Configuring guest portal...")
        
        guest_config = {
            "key": "guest_access",
            "enabled": True,
            "auth": "none",
            "expire": 720,
            "expire_number": 12,
            "expire_unit": 1,
            "download_enabled": True,
            "download_limit": 5120,
            "upload_enabled": True,
            "upload_limit": 5120,
            "redirect_enabled": False,
            "portal_enabled": True,
            "template_engine": "angular"
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
