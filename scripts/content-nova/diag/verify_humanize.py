"""Quick verification of the humanize pass + cross-poster builders."""
import sys
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\scripts\content-nova')
import prompt_pack_crossposter as c

# Test 1: humanize on AI-tell copy
test = "In today's fast-paced landscape, this comprehensive guide serves as a testament to the pivotal role AI plays."
print('BEFORE:', test)
print('AFTER: ', c.humanize(test))
print()

# Test 2: X post with domain-only body + first_comment
prompts = [
    '[Claude] Rewrite this draft for clarity. Output the rewrite and the 3 sentences you cut.',
    '[ChatGPT] Turn this outline into a 600-word article. Match the source tone. Skip the intro.',
    '[Cursor] Find the 5 weakest sentences in this markdown and rewrite each in place. Preserve voice.'
]
sample_url = 'https://www.aitoolalliance.com/daily-prompt-pack-writing-assistants-test/'
x_body = c._build_x_text('Daily Prompt Pack: writing assistants', 'writing assistants', sample_url, prompts)
x_comment = c._build_x_first_comment(sample_url)
print(f'X BODY ({len(x_body)} chars):')
print(x_body)
print()
print('X FIRST_COMMENT:')
print(x_comment)
print()
bsky = c._build_bluesky_text('Daily Prompt Pack: writing assistants', 'writing assistants', sample_url, prompts)
print(f'BLUESKY ({len(bsky)} chars):')
print(bsky)
print()
pin = c._build_pin_text('Daily Prompt Pack: writing assistants', 'writing assistants', sample_url, prompts)
print(f'PINTEREST ({len(pin)} chars):')
print(pin)
