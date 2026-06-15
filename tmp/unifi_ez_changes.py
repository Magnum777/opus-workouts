"""
UniFi Phase 1 using aiounifi library
Proper auth + device management
"""
import asyncio
import aiohttp
import aiounifi
from aiounifi.controller import Controller
from aiounifi.models.configuration import Configuration
import ssl

async def main():
    print("="*60)
    print("UNIFI PHASE 1 -- EZ-UNIFI / AIOUNIFI")
    print("="*60)
    
    # Create SSL context that doesn't verify
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
        print("\nLogging in...")
        await controller.login()
        print("[OK] Authenticated!")
        
        # Update device list
        print("\nGetting devices...")
        await controller.devices.update()
        devices = list(controller.devices.values())
        print(f"Found {len(devices)} devices")
        
        for device in devices:
            print(f"  - {device.name} ({device.model})")
        
        # Find SAP
        sap = None
        for device in devices:
            if device.name.upper() == 'SAP':
                sap = device
                break
        
        if sap:
            print(f"\nFound SAP: {sap.name} ({sap.mac})")
            print(f"  Current radio config:")
            for i, radio in enumerate(sap.raw.get('radio_table', [])):
                print(f"    Radio {i}: Channel {radio.get('channel', 'auto')}, Width {radio.get('ht', 'auto')}MHz")
            
            # Update SAP 5GHz channel using devmgr command
            print("\n  Updating SAP to Ch 149 / 40MHz...")
            await controller.request(
                aiounifi.models.api.ApiRequest(
                    method="post",
                    path="/cmd/devmgr",
                    data={
                        "cmd": "set-config",
                        "mac": sap.mac,
                        "radio_table": [
                            {},
                            {"channel": 149, "ht": 40}
                        ]
                    }
                )
            )
            print("  [OK] SAP updated")
        else:
            print("  ! SAP not found")
        
        # Update WLANs
        print("\nGetting WLANs...")
        await controller.wlans.update()
        wlans = list(controller.wlans.values())
        print(f"Found {len(wlans)} WLANs")
        
        for wlan in wlans:
            print(f"\n  Updating {wlan.name}...")
            
            # Update band steering
            wlan.raw['bandsteering_mode'] = 'balanced'
            
            # Update min RSSI
            wlan.raw['min_rssi_enabled'] = True
            wlan.raw['min_rssi'] = -70
            
            # Update multicast
            wlan.raw['mcastenhance_enabled'] = True
            
            # Save changes
            await controller.request(
                aiounifi.models.api.ApiRequest(
                    method="put",
                    path=f"/rest/wlanconf/{wlan.id}",
                    data=wlan.raw
                )
            )
            print(f"    [OK] Updated")
        
        # Enable DPI
        print("\nEnabling DPI...")
        await controller.request(
            aiounifi.models.api.ApiRequest(
                method="put",
                path="/rest/setting/dpi",
                data={"enabled": True}
            )
        )
        print("  [OK] DPI enabled")
        
        print("\n" + "="*60)
        print("PHASE 1 COMPLETE")
        print("="*60)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
