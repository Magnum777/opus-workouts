import sys, json, os
sys.path.insert(0, r"C:\Users\compj\.openclaw\workspace\scripts\content-nova")
from publisher import create_post

with open(r"C:\Users\compj\.openclaw\workspace\article.html", "r", encoding="utf-8") as f:
    content = f.read()

res = create_post(
    "aitoolalliance.com",
    "Top AI Writing Tools of 2026: Features, Pricing & Picks",
    content,
    status="publish",
    excerpt="Compare the best AI writing tools of 2026 including Jasper, Copy.ai, ChatGPT, Claude, and Gemini. Find the right tool for your workflow and budget."
)
print(json.dumps(res, indent=2))
