# Nova's Stable Diffusion Control Module
# Control SD WebUI programmatically

import subprocess
import time
import os
import requests
from pathlib import Path

SD_PATH = r"C:\Users\compj\.openclaw\workspace\stable-diffusion-webui"
SD_URL = "http://127.0.0.1:7860"
SD_VENV = r"venv310-directml"
SD_LAUNCH_BAT = "webui-user.bat"

def is_running():
    """Check if SD WebUI is running"""
    try:
        response = requests.get(f"{SD_URL}/sdapi/v1/progress", timeout=2)
        return response.status_code == 200
    except:
        return False

def start():
    """Start SD WebUI"""
    if is_running():
        print("Stable Diffusion is already running!")
        print(f"Open: {SD_URL}")
        return True
    
    print("Starting Stable Diffusion WebUI...")
    os.chdir(SD_PATH)
    
    # Launch with DirectML AMD GPU support
    cmd = [
        "cmd", "/c", 
        SD_LAUNCH_BAT
    ]
    
    subprocess.Popen(
        cmd,
        cwd=SD_PATH,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    
    print("Launching... wait 30-60 seconds for models to load")
    
    # Wait for it to be ready
    for i in range(60):
        time.sleep(1)
        if is_running():
            print(f"Ready! Open: {SD_URL}")
            return True
        if i % 10 == 0:
            print(f"Loading... {i}s")
    
    print("Timeout waiting for SD to start")
    return False

def stop():
    """Stop SD WebUI"""
    if not is_running():
        print("Stable Diffusion is not running")
        return True
    
    print("Stopping Stable Diffusion...")
    subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq Stable Diffusion WebUI"], 
                   capture_output=True)
    
    time.sleep(2)
    
    if is_running():
        print("Force stopping remaining processes...")
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"], capture_output=True)
    
    print("Stopped. GPU memory freed.")
    return True

def generate_image(prompt: str, negative: str = "", width: int = 512, height: int = 512, 
                   steps: int = 20, cfg: float = 7.0) -> str:
    """Generate image via API"""
    if not is_running():
        print("SD not running. Starting it first...")
        if not start():
            return None
    
    payload = {
        "prompt": prompt,
        "negative_prompt": negative,
        "width": width,
        "height": height,
        "steps": steps,
        "cfg_scale": cfg,
        "sampler_name": "Euler a"
    }
    
    try:
        response = requests.post(
            f"{SD_URL}/sdapi/v1/txt2img",
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        
        data = response.json()
        images = data.get('images', [])
        
        if not images:
            print("No images returned")
            return None
        
        # Save image
        import base64
        from datetime import datetime
        
        img_data = base64.b64decode(images[0])
        output_dir = Path(__file__).parent / "media" / "generated"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"sd-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
        output_path = output_dir / filename
        
        with open(output_path, 'wb') as f:
            f.write(img_data)
        
        print(f"Image saved: {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"Generation error: {e}")
        return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python sd_control.py [start|stop|status|generate \"prompt\"]")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "start":
        start()
    elif cmd == "stop":
        stop()
    elif cmd == "status":
        if is_running():
            print("[OK] Stable Diffusion is RUNNING")
            print(f"   URL: {SD_URL}")
        else:
            print("[X] Stable Diffusion is NOT running")
    elif cmd == "generate":
        if len(sys.argv) < 3:
            print("Usage: python sd_control.py generate \"your prompt here\"")
        else:
            prompt = sys.argv[2]
            generate_image(prompt)
    else:
        print(f"Unknown command: {cmd}")
