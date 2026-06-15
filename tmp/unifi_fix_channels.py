"""
Fix channels using direct REST API + restart
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
    print("FIXING CHANNELS -- REST API + RESTART")
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
        
        for device in devices:
            name = device.name.upper()
            if name not in channel_plan:
                continue
            
            plan = channel_plan[name]
            mac = device.mac
            
            print(f"Updating {name} ({mac})...")
            
            # Method 1: Use raw PUT to rest/device
            radio_table = device.raw.get('radio_table', [{}, {}])
            
            if len(radio_table) > 0:
                radio_table[0]['channel'] = plan['2ghz']['channel']
                radio_table[0]['ht'] = plan['2ghz']['ht']
            
            if len(radio_table) > 1:
                radio_table[1]['channel'] = plan['5ghz']['channel']
                radio_table[1]['ht'] = plan['5ghz']['ht']
            
            # Update via REST API
            update_data = {
                "radio_table": radio_table,
                "radio_table_index": 0
            }
            
            await controller.request(ApiRequest(
                method="put",
                path=f"/rest/device/{device.id}",
                data=update_data
            ))
            
            print(f"  [OK] Config updated")
            
            # Now restart the device to apply
            print(f"  Restarting {name}...")
            await controller.request(ApiRequest(
                method="post",
                path="/cmd/devmgr",
                data={"cmd": "restart", "mac": mac}
            ))
            print(f"  [OK] Restart triggered")
            
            print(f"  2.4GHz: Ch {plan['2ghz']['channel']}/{plan['2ghz']['ht']}MHz")
            print(f"  5GHz: Ch {plan['5ghz']['channel']}/{plan['5ghz']['ht']}MHz")
        
        print("\n" + "="*60)
        print("All APs restarting with new channels")
        print("="*60)
        print("Wait 60 seconds for them to come back online")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
