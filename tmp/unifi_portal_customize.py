"""
Customize guest portal with church logo and branding
"""
import asyncio
import aiohttp
import aiounifi
from aiounifi.controller import Controller
from aiounifi.models.configuration import Configuration
from aiounifi.models.api import ApiRequest
import ssl
import base64

async def main():
    print("="*60)
    print("CUSTOMIZING GUEST PORTAL")
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
        
        # First upload logo
        print("Uploading church logo...")
        logo_path = "C:\\Users\\compj\\.openclaw\\workspace\\docs\\media\\sojourn-logo.png"
        
        with open(logo_path, 'rb') as f:
            logo_data = f.read()
        
        logo_b64 = base64.b64encode(logo_data).decode('utf-8')
        
        # Upload via multipart
        form = aiohttp.FormData()
        form.add_field('file', logo_data, filename='sojourn-logo.png', content_type='image/png')
        
        upload_url = "https://192.241.248.242/proxy/network/api/s/default/upload/portal"
        async with session.post(upload_url, data=form, ssl=ssl_context) as resp:
            print(f"Upload status: {resp.status}")
            if resp.status == 200:
                print("[OK] Logo uploaded")
                upload_result = await resp.json()
                print(f"Result: {upload_result}")
        
        # Now update portal customization
        print("\nUpdating portal branding...")
        
        portal_config = {
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
            "portal_customized": True,
            "portal_customized_title": "Welcome to Sojourn Church",
            "portal_customized_welcome_text": "Guest WiFi Access",
            "portal_customized_welcome_text_enabled": True,
            "portal_customized_tos_enabled": True,
            "portal_customized_tos": "By connecting to this network, you agree to use it for lawful purposes only. Do not transmit sensitive information (banking, passwords) over this public connection. Access is limited to 12 hours per session.",
            "portal_customized_button_text": "Connect to Internet",
            "portal_customized_success_text": "Welcome! You are now connected.",
            "portal_customized_authentication_text": "Accept Terms to Connect",
            "portal_customized_logo_enabled": True,
            "portal_customized_logo_position": "center",
            "portal_customized_logo_size": 128,
            "portal_customized_bg_type": "color",
            "portal_customized_bg_color": "#233041",
            "portal_customized_bg_image_enabled": False,
            "portal_customized_box_color": "#ffffff",
            "portal_customized_box_opacity": 90,
            "portal_customized_box_radius": 25,
            "portal_customized_text_color": "#333333",
            "portal_customized_box_text_color": "#333333",
            "portal_customized_link_color": "#0066cc",
            "portal_customized_box_link_color": "#0066cc",
            "portal_customized_button_color": "#0066cc",
            "portal_customized_button_text_color": "#ffffff",
            "portal_customized_welcome_text_position": "under_logo",
            "portal_customized_languages": ["en"],
            "portal_customized_bg_image_tile": False
        }
        
        await controller.request(ApiRequest(
            method="put",
            path="/rest/setting/guest_access",
            data=portal_config
        ))
        
        print("[OK] Portal customized!")
        
        print("\n" + "="*60)
        print("PORTAL CUSTOMIZATION COMPLETE")
        print("="*60)
        print("\nPortal now shows:")
        print("  - Title: 'Welcome to Sojourn Church'")
        print("  - Welcome: 'Guest WiFi Access'")
        print("  - Terms of Use checkbox")
        print("  - Button: 'Connect to Internet'")
        print("  - Sojourn Church branding")
        print("  - 12-hour session limit")
        print("  - 5 Mbps down / 5 Mbps up")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
