"""
UniFi VLAN creation -- Try different field format
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
    print("VLAN CREATION -- FIXED FORMAT")
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
        
        # Try creating VLANs with different field names
        networks = [
            {
                "name": "sojourn-office",
                "vlan": 10,  # Use 'vlan' instead of 'vlan_id'
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
                "vlan": 20,
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
                "vlan": 30,
                "purpose": "guest",
                "ip_subnet": "192.168.30.1/24",
                "dhcpd_start": "192.168.30.10",
                "dhcpd_stop": "192.168.30.250",
                "dhcpd_enabled": True,
                "vlan_enabled": True,
                "networkgroup": "LAN"
            }
        ]
        
        changes = []
        for net in networks:
            print(f"Creating {net['name']} (VLAN {net['vlan']})...")
            try:
                r = await controller.request(ApiRequest(
                    method="post",
                    path="/rest/networkconf",
                    data=net
                ))
                print(f"  [OK] Created")
                changes.append(f"network:{net['name']}")
            except Exception as e:
                print(f"  [FAIL] {e}")
        
        print(f"\n{'='*60}")
        print(f"COMPLETE: {len(changes)} networks created")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
