"""
UniFi Phase 2 -- Channel Optimization
Spread 5GHz channels, de-overlap 2.4GHz
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
    print("UNIFI PHASE 2 -- CHANNEL OPTIMIZATION")
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
        
        # Get devices
        await controller.devices.update()
        devices = list(controller.devices.values())
        
        # Channel plan
        channel_plan = {
            'YAP': {'5ghz': {'channel': 100, 'ht': 40}, '2ghz': {'channel': 1, 'ht': 20}},
            'OAP': {'5ghz': {'channel': 116, 'ht': 40}, '2ghz': {'channel': 11, 'ht': 20}},
            'CAP': {'5ghz': {'channel': 44, 'ht': 40}, '2ghz': {'channel': 6, 'ht': 20}},
            'FAP': {'5ghz': {'channel': 48, 'ht': 40}, '2ghz': {'channel': 6, 'ht': 20}},
            'SAP': {'5ghz': {'channel': 149, 'ht': 40}, '2ghz': {'channel': 1, 'ht': 20}},
        }
        
        changes = []
        
        for device in devices:
            name = device.name.upper()
            if name not in channel_plan:
                continue
            
            plan = channel_plan[name]
            mac = device.mac
            
            print(f"Updating {name} ({mac})...")
            
            # Build radio table
            radio_table = device.raw.get('radio_table', [{}, {}])
            
            # Update 2.4GHz (radio 0)
            if len(radio_table) > 0:
                radio_table[0]['channel'] = plan['2ghz']['channel']
                radio_table[0]['ht'] = plan['2ghz']['ht']
            
            # Update 5GHz (radio 1)
            if len(radio_table) > 1:
                radio_table[1]['channel'] = plan['5ghz']['channel']
                radio_table[1]['ht'] = plan['5ghz']['ht']
            
            # Push update
            await controller.request(ApiRequest(
                method="post",
                path="/cmd/devmgr",
                data={
                    "cmd": "set-config",
                    "mac": mac,
                    "radio_table": radio_table
                }
            ))
            
            print(f"  [OK] 2.4GHz: Ch {plan['2ghz']['channel']}/{plan['2ghz']['ht']}MHz")
            print(f"  [OK] 5GHz: Ch {plan['5ghz']['channel']}/{plan['5ghz']['ht']}MHz")
            changes.append(f"{name}: 2.4GHz Ch {plan['2ghz']['channel']}, 5GHz Ch {plan['5ghz']['channel']}")
        
        # Update OAP firmware
        print("\nChecking OAP firmware...")
        for device in devices:
            if device.name.upper() == 'OAP':
                version = device.raw.get('version', 'unknown')
                print(f"  Current: {version}")
                if version != '6.8.2':
                    print(f"  Triggering upgrade to 6.8.2...")
                    await controller.request(ApiRequest(
                        method="post",
                        path="/cmd/devmgr",
                        data={"cmd": "upgrade", "mac": device.mac}
                    ))
                    print(f"  [OK] Upgrade triggered")
                    changes.append("OAP: firmware upgrade to 6.8.2")
                else:
                    print(f"  Already on 6.8.2")
                break
        
        print("\n" + "="*60)
        print(f"PHASE 2 COMPLETE: {len(changes)} changes")
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
