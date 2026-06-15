"""
Configure guest portal without VLANs -- use existing network
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
    print("GUEST PORTAL CONFIGURATION")
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
        
        # Configure guest portal settings
        print("Configuring guest portal...")
        
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
            "template_engine": "angular",
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
        
        await controller.request(ApiRequest(
            method="put",
            path="/rest/setting/guest_access",
            data=guest_config
        ))
        
        print("[OK] Guest portal configured!")
        print("\nSettings applied:")
        print("  - Session timeout: 12 hours")
        print("  - Download limit: 5 Mbps")
        print("  - Upload limit: 5 Mbps")
        print("  - Terms of service: enabled")
        print("  - Portal page: enabled")
        
        # Now enable hotspot on sojourn-guest WLAN
        print("\nEnabling hotspot on sojourn-guest...")
        await controller.wlans.update()
        wlans = list(controller.wlans.values())
        
        for wlan in wlans:
            if wlan.name == 'sojourn-guest':
                wlan.raw['enabled'] = True
                wlan.raw['wpa_mode'] = 'none'
                wlan.raw['wpa_enc'] = 'none'
                wlan.raw['security'] = 'open'
                
                await controller.request(ApiRequest(
                    method="put",
                    path=f"/rest/wlanconf/{wlan.id}",
                    data=wlan.raw
                ))
                print(f"[OK] sojourn-guest configured as open + portal")
                break
        
        print("\n" + "="*60)
        print("GUEST PORTAL COMPLETE")
        print("="*60)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
