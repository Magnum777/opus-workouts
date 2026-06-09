import re, json

with open('crackerbarrel_raw.html','r',encoding='utf-8') as f:
    html = f.read()

# Look for dollar signs / prices
prices = re.findall(r'\$[\d,]+\.\d{2}', html)
print(f'Prices found: {len(prices)}')
print('First 30:', prices[:30])

# Look for food item patterns in alt/title attributes
items = re.findall(r'(?:alt=|title=|name=|aria-label=)"([^"]{10,80})"', html)
food_items = [i for i in items if any(w in i.lower() for w in ['chicken','tender','dumplin','meatloaf','roast','beef','pork','fish','shrimp','mac','cheese','green','bean','mashed','potato','cole','slaw','corn','biscuit','roll','cornbread','plate','platter','buffet'])]
print(f'\nFood items: {len(food_items)}')
for item in food_items[:30]:
    print(item)

# Look for Next.js data more carefully
# The data is likely in a script tag
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
for i, s in enumerate(scripts):
    if len(s) > 100000:
        try:
            data = json.loads(s)
            # Save to file for inspection
            with open('crackerbarrel_data.json','w',encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f'\nSaved large JSON script to crackerbarrel_data.json ({len(s)} chars)')
        except:
            pass
