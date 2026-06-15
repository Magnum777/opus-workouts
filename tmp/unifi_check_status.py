"""
Check current AP status after Phase 2
"""
import asyncio
import aiohttp
import aiounifi
from aiounifi.controller import Controller
from aiounifi.models.configuration import Configuration
import ssl

async def main():
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
        
        await controller.devices.update()
        devices = list(controller.devices.values())
        
        print("="*60)
        print("CURRENT AP STATUS")
        print("="*60)
        
        for device in devices:
            if device.name.upper() in ['YAP', 'OAP', 'CAP', 'SAP', 'FAP']:
                print(f"\n{device.name} ({device.model}):")
                print(f"  Uptime: {device.raw.get('uptime', 'unknown')} seconds")
                print(f"  Last seen: {device.raw.get('last_seen', 'unknown')}")
                
                radio_table = device.raw.get('radio_table', [])
                for i, radio in enumerate(radio_table):
                    band = "2.4GHz" if i == 0 else "5GHz"
                    ch = radio.get('channel', 'unknown')
                    width = radio.get('ht', 'unknown')
                    print(f"  {band}: Channel {ch}, Width {width}MHz")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
