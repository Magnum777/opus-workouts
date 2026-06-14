import requests
from bs4 import BeautifulSoup
import os

url = 'https://pxhere.com/en/photo/1710422'
r = requests.get(url, timeout=10)
print(f'Status: {r.status_code}')

soup = BeautifulSoup(r.text, 'html.parser')
img = soup.find('img', {'class': 'photo-image'})
if img:
    img_url = img.get('src')
    print(f'Image URL: {img_url}')
    img_r = requests.get(img_url, timeout=15)
    if img_r.status_code == 200:
        temp_dir = r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\temp_images'
        os.makedirs(temp_dir, exist_ok=True)
        img_path = os.path.join(temp_dir, 'privacy_1710422.jpg')
        with open(img_path, 'wb') as f:
            f.write(img_r.content)
        print(f'Saved: {img_path} ({len(img_r.content)} bytes)')
    else:
        print(f'Download failed: {img_r.status_code}')
else:
    print('Image not found on page')
    for i, img in enumerate(soup.find_all('img')[:10]):
        src = img.get('src', 'no src')
        print(f'  img {i}: {src[:80]}')
