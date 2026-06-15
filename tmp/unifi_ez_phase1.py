"""
UniFi Phase 1 using ez-unifi skill approach
Uses aiounifi library for proper auth
"""
import asyncio
import aiohttp
import aiounifi
from aiounifi.controller import Controller
from aiounifi.models.configuration import Configuration
import json

async def make_changes():
    config = Configuration(
        aiounifiurl="https://192.241.248.242",
        username="Nova",
        password="N0v4!123N0v4!12",
        site="default",
        ssl_context=False,
        session=aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    )
    
    controller = Controller(config)
    
    try:
        print("Connecting to UniFi...")
        await controller.login()
        print("[OK] Connected!")
        
        # Get devices
        print("\nGetting devices...")
        devices = await controller.devices.update()
        for device in devices:
            print(f"  - {device.name} ({device.model}) - MAC: {device.mac}")
        
        # Get WLANs
        print("\nGetting WLANs...")
        wlans = await controller.wlans.update()
        for wlan in wlans:
            print(f"  - {wlan.name} (ID: {wlan.id[:8]}...)")
        
        # TODO: Make changes via aiounifi API
        # The library handles auth properly, should allow writes
        
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        await controller.logout()
        await config.session.close()

if __name__ == "__main__":
    asyncio.run(make_changes())
