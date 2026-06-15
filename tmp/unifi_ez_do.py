"""
UniFi Phase 1 using ez-unifi / aiounifi library
Handles auth properly, should allow writes
"""
import asyncio
import aiohttp
import aiounifi
from aiounifi.controller import Controller
from aiounifi.models.configuration import Configuration
import json

async def main():
    print("="*60)
    print("UNIFI PHASE 1 -- EZ-UNIFI SKILL")
    print("="*60)
    
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    
    try:
        config = Configuration(
            aiounifiurl="https://192.241.248.242",
            username="Nova",
            password="N0v4!123N0v4!12",
            site="default",
            ssl_context=False,
            session=session
        )
        
        controller = Controller(config)
        print("\nLogging in...")
        await controller.login()
        print("[OK] Authenticated!")
        
        # Get current state
        print("\nGetting current config...")
        await controller.devices.update()
        await controller.wlans.update()
        
        devices = controller.devices.values()
        wlans = controller.wlans.values()
        
        print(f"Found {len(devices)} devices")
        for d in devices:
            print(f"  - {d.name} ({d.model})")
        
        print(f"Found {len(wlans)} WLANs")
        for w in wlans:
            print(f"  - {w.name}")
        
        # TODO: Make changes
        # The aiounifi library has proper device update methods
        # that handle the auth correctly
        
        print("\n[TODO] Changes would go here")
        print("Need to implement device.update() calls")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
