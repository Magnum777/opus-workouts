import re

filepath = r'C:\Users\compj\.openclaw\workspace\workout-tracker\index.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: Remove from EXERCISES array (lines like { name: "...Sauna...", sets: 1, reps: 15, unit: "min" },)
content = re.sub(
    r'\s*\{\s*name:\s*"[^"]*(?:Sauna|Elliptical)[^"]*".*?\},?',
    '',
    content,
    flags=re.DOTALL
)

# Step 2: Remove HTML table rows for sauna/elliptical
# Pattern matches: <tr> through </tr> containing Sauna or Elliptical
content = re.sub(
    r'\s*<tr>\s*<td>\s*<div class="exercise-name">(?:🔥\s*)?(?:Sauna Warm-up|Elliptical Cardio)</div>.*?</td>\s*</tr>\s*',
    '\n',
    content,
    flags=re.DOTALL
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done - removed sauna and elliptical from tracker')
