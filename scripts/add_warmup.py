import re

filepath = r'C:\Users\compj\.openclaw\workspace\workout-tracker\index.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Wednesday insert
weds_marker = '''    <table class="exercise-table">
      <tr><th>Exercise</th><th>Sets x Reps/Time</th><th>Note</th></tr>'''
weds_insert = '''    <table class="exercise-table">
      <tr><th>Exercise</th><th>Sets x Reps/Time</th><th>Note</th></tr>
      <tr>
        <td>
          <div class="exercise-name">🔥 Sauna Warm-up</div>
          <div class="exercise-note">10-15 minutes to loosen up joints and get blood flowing.</div>
        </td>
        <td>1 x 15 min</td>
        <td>Hydrate before and after.</td>
      </tr>
      <tr>
        <td>
          <div class="exercise-name">Elliptical Cardio</div>
          <div class="exercise-note">Low-impact warm-up. Moderate pace.</div>
        </td>
        <td>1 x 15 min</td>
        <td>Low resistance, steady pace.</td>
      </tr>'''
content = content.replace(weds_marker, weds_insert)

# Thursday
thu_pattern = r'(  <!-- THURSDAY: PULL -->.*?)(<table class="exercise-table">\s*<tr><th>Exercise</th><th>Sets x Reps</th><th>Note</th></tr>)'
thu_insert = r'''\1\2
      <tr>
        <td>
          <div class="exercise-name">🔥 Sauna Warm-up</div>
          <div class="exercise-note">10-15 minutes to loosen up joints and get blood flowing.</div>
        </td>
        <td>1 x 15 min</td>
        <td>Hydrate before and after.</td>
      </tr>
      <tr>
        <td>
          <div class="exercise-name">Elliptical Cardio</div>
          <div class="exercise-note">Low-impact warm-up. Moderate pace.</div>
        </td>
        <td>1 x 10 min</td>
        <td>Low resistance, steady pace.</td>
      </tr>'''
content = re.sub(thu_pattern, thu_insert, content, flags=re.DOTALL)

# Friday
fri_pattern = r'(  <!-- FRIDAY: FULL BODY -->.*?)(<table class="exercise-table">\s*<tr><th>Exercise</th><th>Sets x Reps</th><th>Note</th></tr>)'
fri_insert = r'''\1\2
      <tr>
        <td>
          <div class="exercise-name">🔥 Sauna Warm-up</div>
          <div class="exercise-note">10-15 minutes to loosen up joints and get blood flowing.</div>
        </td>
        <td>1 x 15 min</td>
        <td>Hydrate before and after.</td>
      </tr>
      <tr>
        <td>
          <div class="exercise-name">Elliptical Cardio</div>
          <div class="exercise-note">Low-impact warm-up. Moderate pace.</div>
        </td>
        <td>1 x 10 min</td>
        <td>Low resistance, steady pace.</td>
      </tr>'''
content = re.sub(fri_pattern, fri_insert, content, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done - added sauna/elliptical to Wed/Thu/Fri display')
