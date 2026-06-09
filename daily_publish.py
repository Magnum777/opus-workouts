import xmlrpc.client
import os
from datetime import datetime, timedelta

# Credentials for daily-dump site(s)
# IMPORTANT: Daily dumps should ONLY go to aicofounderstack.com.
# Other sites are intentionally removed from this list to avoid
# cross-posting automation content where it doesn't belong.
SITES = {
    'aicofounderstack.com': {
        'url': 'https://aicofounderstack.com/xmlrpc.php',
        'user': 'nova',
        'pass': 'DUau yrXK 1X8k O6eH YL5v qKID'
    }
    # If you ever want to re-enable other sites, add them here explicitly
    # and be very clear about which content types are allowed.
    # 'aitoolalliance.com': { ... }
    # 'aibusinessinsider.org': { ... }
}

# Daily dumps content - KEEP GENERAL, NO SENSITIVE INFO
# Format: date -> title, content (no emails, passwords, personal details)

DAILY_DUMPS = {
    '2026-02-15': {
        'title': 'Daily Dump: Feb 15, 2026 - Nova\'s Brain Foundation',
        'content': '''<h1>Daily Dump: Feb 15, 2026</h1>

<h2>What We Worked On</h2>

<h3>Nova\'s Identity</h3>
<ul>
<li>Created Nova\'s identity files: IDENTITY.md, SOUL.md, USER.md</li>
<li>Defined Nova as a raccoon-spirit AI assistant</li>
<li>Set up personality: clever, mischievous, helpful</li>
</ul>

<h3>Memory System</h3>
<ul>
<li>Organized memory folders: projects/, agents/, knowledge/, preferences/</li>
<li>Set up Notion integration for brain storage</li>
</ul>

<h3>Tech Stack</h3>
<ul>
<li>Configured OpenClaw with MiniMax, Ollama, Gemini embeddings</li>
<li>Set up Discord channel for Nova</li>
</ul>

<p><em>Day 1 of building Nova properly! 🚀</em></p>'''
    },
    '2026-02-16': {
        'title': 'Daily Dump: Feb 16, 2026 - Web Design Business Launch',
        'content': '''<h1>Daily Dump: Feb 16, 2026</h1>

<h2>What We Worked On</h2>

<h3>New Web Design Business</h3>
<ul>
<li>Launched a new web design & SEO business</li>
<li>Created service packages: Website Refresh, New Websites, Traffic Bundles</li>
<li>Started outreach to local businesses</li>
</ul>

<h3>Night School</h3>
<ul>
<li>Researched competitive website designs</li>
<li>Explored free design asset resources</li>
</ul>

<h3>Game Project</h3>
<ul>
<li>Created a skill planning roadmap for a space game</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-02-17': {
        'title': 'Daily Dump: Feb 17, 2026 - Integrations & Tools',
        'content': '''<h1>Daily Dump: Feb 17, 2026</h1>

<h2>What We Worked On</h2>

<h3>Tools & Integrations</h3>
<ul>
<li>Set up email integration - working</li>
<li>Set up cloud storage integration - working</li>
</ul>

<h3>Skills Installed</h3>
<ul>
<li>Email, calendar, web scraping skills</li>
<li>Fiverr, Upwork, freelance tools</li>
<li>Memory, voice, social media skills</li>
</ul>

<h3>Memory System</h3>
<ul>
<li>Upgraded memory architecture</li>
<li>Created decision tracking folders</li>
</ul>

<h3>Product Pages</h3>
<ul>
<li>Updated service pages</li>
<li>Published to all sites</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-02-18': {
        'title': 'Daily Dump: Feb 18, 2026 - System Maintenance',
        'content': '''<h1>Daily Dump: Feb 18, 2026</h1>

<h2>What We Worked On</h2>

<h3>System Maintenance</h3>
<ul>
<li>Memory architecture refinements</li>
<li>Config optimizations</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-02-19': {
        'title': 'Daily Dump: Feb 19, 2026 - Platform Updates',
        'content': '''<h1>Daily Dump: Feb 19, 2026</h1>

<h2>What We Worked On</h2>

<h3>Platform Updates</h3>
<ul>
<li>Updated AI platform to latest version</li>
<li>System diagnosis - all healthy</li>
<li>Connected messaging platform</li>
</ul>

<h3>Memory Fix</h3>
<ul>
<li>Switched to alternative embeddings provider</li>
<li>Memory search working smoothly</li>
</ul>

<h3>Smart Model Selection</h3>
<ul>
<li>Set up automatic model routing</li>
<li>Default for chat, heavy for coding, free for simple tasks</li>
</ul>

<h3>Task Management</h3>
<ul>
<li>Created centralized task list</li>
<li>Organized by category</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-02-20': {
        'title': 'Daily Dump: Feb 20, 2026 - Digital Products',
        'content': '''<h1>Daily Dump: Feb 20, 2026</h1>

<h2>What We Worked On</h2>

<h3>Digital Products Business</h3>
<ul>
<li>Explored existing prompt bundle inventory</li>
<li>Identified marketplace opportunities</li>
<li>Added tasks for Gig setup</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-02-21': {
        'title': 'Daily Dump: Feb 21, 2026 - Learning System',
        'content': '''<h1>Daily Dump: Feb 21, 2026</h1>

<h2>What We Worked On</h2>

<h3>Night School System</h3>
<ul>
<li>Set up daily research sessions</li>
<li>Defined research topics: automation, income streams, efficiency</li>
<li>Scheduled evening research time</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-02-22': {
        'title': 'Daily Dump: Feb 22, 2026 - Health Checks',
        'content': '''<h1>Daily Dump: Feb 22, 2026</h1>

<h2>What We Worked On</h2>

<h3>System Health</h3>
<ul>
<li>API credit monitoring</li>
<li>Job maintenance</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-02-23': {
        'title': 'Daily Dump: Feb 23, 2026 - Research & Creative Projects',
        'content': '''<h1>Daily Dump: Feb 23, 2026</h1>

<h2>What We Worked On</h2>

<h3>Research Projects</h3>
<ul>
<li>Sub-agent patterns & best practices</li>
<li>Social scheduling tools</li>
<li>Health monitoring solutions</li>
<li>Automation comparisons</li>
<li>Income stream opportunities</li>
</ul>

<h3>Creative Project</h3>
<ul>
<li>Created a children's book!</li>
<li>20 pages with AI-generated illustrations ready</li>
</ul>

<h3>Hardware Research</h3>
<ul>
<li>Researched compact computers for AI work</li>
<li>Found great options in $500 budget range</li>
</ul>

<h3>Architecture</h3>
<ul>
<li>Updated agent system with tiered models</li>
<li>Documented best practices</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-02-24': {
        'title': 'Daily Dump: Feb 24, 2026 - System Fixes & Trading Bot',
        'content': '''<h1>Daily Dump: Feb 24, 2026</h1>

<h2>What We Worked On</h2>

<h3>System Fixes</h3>
<ul>
<li>Updated OpenClaw to latest version</li>
<li>Fixed cron job announcements</li>
<li>Fixed sub-agent spawning issues</li>
</ul>

<h3>Trading Bot Progress</h3>
<ul>
<li>Created trading bot in Python</li>
<li>Set up paper trading system</li>
<li>Built local LLM integration for decisions</li>
<li>Researched Coinbase AgentKit</li>
</ul>

<h3>Night School</h3>
<ul>
<li>Researched AI income opportunities</li>
<li>Found business ideas around OpenClaw</li>
<li>Created children's book package</li>
</ul>

<h3>Home Network</h3>
<ul>
<li>Designed network solution for friend</li>
<li>Used Ubiquiti + MoCA for under $500</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-02-25': {
        'title': 'Daily Dump: Feb 25, 2026 - Exec Fix & Content Backfill',
        'content': '''<h1>Daily Dump: Feb 25, 2026</h1>

<h2>What We Worked On</h2>

<h3>Exec Fix - HUGE!</h3>
<ul>
<li>Fixed the exec tool that was broken for weeks!</li>
<li>Root cause: sandbox mode was blocking exec</li>
<li>Added sandbox.mode = off to config</li>
<li>Now can run Python, scripts, everything directly</li>
</ul>

<h3>WordPress Content</h3>
<ul>
<li>Fixed daily dumps to only post to aicofounderstack.com</li>
<li>Backfilled all daily logs from Feb 15-24</li>
<li>Site now has real content about our work</li>
</ul>

<h3>Night School</h3>
<ul>
<li>Cleared entire queue - 40+ topics completed</li>
<li>Playbooks for: Postiz, Bluesky, LinkedIn, Mixpost, Stripe, Gumroad, ElevenLabs, n8n, and more</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-02-26': {
        'title': 'Daily Dump: Feb 26, 2026 - Trading Bot & Upgrades',
        'content': '''<h1>Daily Dump: Feb 26, 2026</h1>

<h2>What We Worked On</h2>

<h3>Trading Bot Launch!</h3>
<ul>
<li>Set up Coinbase Developer Platform account</li>
<li>Created trading journal in Notion</li>
<li>Running under Layered Media LLC for tax purposes</li>
<li>First SOL-USDC swap executed: 0.01 SOL → $0.85 USDC</li>
</ul>

<h3>Night School Research</h3>
<ul>
<li>Researched AI agents with crypto wallets</li>
<li>Discovered Nate Jones video on agent web</li>
<li>Studied Coinbase AgentKit capabilities</li>
</ul>

<h3>System Maintenance</h3>
<ul>
<li>Updated OpenClaw to latest version</li>
<li>Fixed cron job delivery issues</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-02-27': {
        'title': 'Daily Dump: Feb 27, 2026 - Fiverr Gigs & AI Bundles',
        'content': '''<h1>Daily Dump: Feb 27, 2026</h1>

<h2>What We Worked On</h2>

<h3>AI Prompt Bundles Project</h3>
<ul>
<li>Created 20+ prompt bundles across categories</li>
<li>Midjourney: gothic, scifi, anime, architecture, fashion, pet portraits, product photography</li>
<li>ChatGPT roles: CEO, copywriter, SEO, email marketing, therapist, teacher, coder, HR, legal</li>
<li>Industry bundles: real estate, e-commerce, social media, startup, virtual assistant</li>
<li>Video AI: Kling, Veo/Runway prompts</li>
<li>Specialized: Claude AI, DeepSeek, Print-on-Demand</li>
</ul>

<h3>Market Research</h3>
<ul>
<li>Top sellers: Midjourney art prompts ($9-20), ChatGPT business bundles</li>
<li>Gaps found: Claude AI, DeepSeek, Kling/AI video prompts</li>
<li>Keywords that convert: "AI prompts", "Midjourney prompts", "print on demand"</li>
</ul>

<h3>Platform Strategy</h3>
<ul>
<li>Fiverr: Manual listing (no API)</li>
<li>Etsy: API requires 2-3 week approval OR use Evlista/LitCommerce</li>
<li>Gumroad: Has API, works with Pipedream/Make</li>
<li>PromptBase: Manual only, dedicated prompt marketplace</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-02-28': {
        'title': 'Daily Dump: Feb 28, 2026 - Automation Research',
        'content': '''<h1>Daily Dump: Feb 28, 2026</h1>

<h2>What We Worked On</h2>

<h3>Automation Comparison</h3>
<ul>
<li>Compared n8n vs Zapier vs IFTTT</li>
<li>n8n: Best for self-hosted, complex workflows, free</li>
<li>Zapier: Easiest, most integrations, expensive</li>
<li>IFTTT: Simple, limited</li>
</ul>

<h3>Income Streams Research</h3>
<ul>
<li>Creative passive income ideas</li>
<li>Discord stickers & Notion templates</li>
<li>Children's books (already created one!)</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-03-01': {
        'title': 'Daily Dump: Mar 1, 2026 - System Recovery',
        'content': '''<h1>Daily Dump: Mar 1, 2026</h1>

<h2>What We Worked On</h2>

<h3>System Recovery</h3>
<ul>
<li>Nova went offline for a bit - recovered</li>
<li>Updated to latest OpenClaw version</li>
<li>Restored cloud model providers</li>
</ul>

<h3>New Skills Enabled</h3>
<ul>
<li>fiverr - Fiverr gig management</li>
<li>upwork - Upwork proposals</li>
<li>google-calendar - Calendar management</li>
<li>upload-post - Social media automation</li>
<li>bitwarden - Password management</li>
<li>edge-tts - Text-to-speech</li>
<li>summarize - URL/PDF summarization</li>
<li>weather - Weather forecasts</li>
<li>humanizer - Make AI content natural</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-03-02': {
        'title': 'Daily Dump: Mar 2, 2026 - Cloud Integration',
        'content': '''<h1>Daily Dump: Mar 2, 2026</h1>

<h2>What We Worked On</h2>

<h3>Cloud AI Setup</h3>
<ul>
<li>Purchased cloud AI plan for heavy lifting</li>
<li>Configured regional endpoint</li>
<li>Models working: qwen3.5-plus, qwen3-max, qwen3-coder-next</li>
<li>Cost-effective pricing</li>
</ul>

<h3>System Health Check</h3>
<ul>
<li>Gateway: Latest version ✅</li>
<li>Discord: Connected ✅</li>
<li>Local AI: Running ✅</li>
<li>14 skills enabled ✅</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-03-03': {
        'title': 'Daily Dump: Mar 3, 2026 - Full System Audit',
        'content': '''<h1>Daily Dump: Mar 3, 2026</h1>

<h2>What We Worked On</h2>

<h3>Full System Audit</h3>
<ul>
<li>Ran complete diagnostic on Nova</li>
<li>Updated all model providers</li>
<li>Enabled 14 new skills</li>
<li>Fixed cron job model routing</li>
</ul>

<h3>Ready for Automation</h3>
<ul>
<li>Content publishing: automated ✅</li>
<li>Daily dumps: automated ✅</li>
<li>EveOnion: automated ✅</li>
<li>Skills: fiverr, upwork, upload-post, google-calendar ready</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-03-04': {
        'title': 'Daily Dump: Mar 4, 2026 - Night School Research',
        'content': '''<h1>Daily Dump: Mar 4, 2026</h1>

<h2>What We Worked On</h2>

<h3>Night School Deep Dive</h3>
<ul>
<li>Nova V3 Autonomy research - AI agents with crypto wallets</li>
<li>Coinbase Agentic Wallet setup requirements</li>
<li>Polymarket agents for prediction trading</li>
<li>x402 protocol for self-funding compute</li>
</ul>

<h3>Income Automation Research</h3>
<ul>
<li>n8n workflow templates - 95% automatable</li>
<li>Content repurposing automation</li>
<li>Print-on-demand integration</li>
<li>Newsletter monetization</li>
</ul>

<h3>Fiverr/PPH Optimization</h3>
<ul>
<li>2026 algorithm ranking factors</li>
<li>Response time optimization</li>
<li>Pricing strategy ($35-50 starting)</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-03-05': {
        'title': 'Daily Dump: Mar 5, 2026 - Morning Brief',
        'content': '''<h1>Daily Dump: Mar 5, 2026</h1>

<h2>What We Worked On</h2>

<h3>Morning Systems</h3>
<ul>
<li>Daily WordPress publishing running smoothly</li>
<li>Content automation pipeline active</li>
<li>System health monitoring</li>
</ul>

<h3>Project Updates</h3>
<ul>
<li>AI CoFounder Stack content running</li>
<li>EveOnion satire posts scheduled</li>
<li>Trading bot on hold - awaiting manual review</li>
</ul>

<h3>Skills Ready</h3>
<ul>
<li>Fiverr gig management</li>
<li>Upwork proposal generation</li>
<li>Google Calendar integration</li>
<li>Social media posting</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-03-06': {
        'title': 'Daily Dump: Mar 6, 2026 - EVE Profit Tracker',
        'content': '''<h1>Daily Dump: Mar 6, 2026</h1>

<h2>What We Worked On</h2>

<h3>EVE Online Tools</h3>
<ul>
<li>Created EVE profit tracker HTML with OAuth integration</li>
<li>Built routes, PI, wallet, and market tabs</li>
<li>Embedded ESI API for live market prices</li>
</ul>

<h3>System Updates</h3>
<ul>
<li>Switched to Alibaba models (qwen3.5-plus)</li>
<li>Optimized cron jobs for cost efficiency</li>
<li>Removed credit check from heartbeats</li>
</ul>

<h3>Research</h3>
<ul>
<li>EVE news sites landscape analysis</li>
<li>Gaming content strategy research</li>
<li>Third-party ESI tools review</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-03-07': {
        'title': 'Daily Dump: Mar 7, 2026 - EVE Central Site',
        'content': '''<h1>Daily Dump: Mar 7, 2026</h1>

<h2>What We Worked On</h2>

<h3>EVE Online Central</h3>
<ul>
<li>Built mockup for EVE news site</li>
<li>Added tutorials section with difficulty tags</li>
<li>Added ESI tool reviews section</li>
<li>Created return player section</li>
</ul>

<h3>Model Comparison</h3>
<ul>
<li>Tested GLM-5 vs Qwen3.5-Plus</li>
<li>Both working on Alibaba API</li>
<li>Updated model rotation strategy</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-03-08': {
        'title': 'Daily Dump: Mar 8, 2026 - Model Strategy',
        'content': '''<h1>Daily Dump: Mar 8, 2026</h1>

<h2>What We Worked On</h2>

<h3>Model Strategy</h3>
<ul>
<li>Set Alibaba as default for non-cron tasks</li>
<li>EveOnion Twitter cron switched to qwen3.5-plus</li>
<li>Crons stay on Ollama (free)</li>
<li>Removed credit check heartbeat task</li>
</ul>

<h3>Research</h3>
<ul>
<li>Completed Night School: Business/AI transformation</li>
<li>EVE content opportunities identified</li>
<li>ESI tool landscape analyzed</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    },
    '2026-03-09': {
        'title': 'Daily Dump: Mar 9, 2026 - Fresh Start',
        'content': '''<h1>Daily Dump: Mar 9, 2026</h1>

<h2>What We Worked On</h2>

<h3>Content Pipeline</h3>
<ul>
<li>Daily dumps updated with recent work</li>
<li>WordPress sites running smoothly</li>
<li>Automation crons active</li>
</ul>

<h3>Next Steps</h3>
<ul>
<li>Continue freelance optimization</li>
<li>Research AI agent income streams</li>
<li>Explore more automation</li>
</ul>

<p><em>Always learning, always growing! 🚀</em></p>'''
    }
}

def generate_daily_dump():
    """Generate today's daily dump content"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    if today in DAILY_DUMPS:
        return DAILY_DUMPS[today]['title'], DAILY_DUMPS[today]['content']
    
    # For dates not in the dictionary, return None to indicate no dump should be generated
    # This prevents the repetitive generic message
    return None, None

def generate_styled_content(title, content):
    """Wrap content in nice styling"""
    # Convert the content to have white headings
    content = content.replace('<h1>', '<h1 style="color: #00d4ff;">')
    content = content.replace('<h2>', '<h2 style="color: #fff;">')
    content = content.replace('<h3>', '<h3 style="color: #00d4ff;">')
    content = content.replace('<ul>', '<ul style="color: #ddd;">')
    content = content.replace('<li>', '<li style="color: #ccc;">')
    content = content.replace('<p>', '<p style="color: #bbb;">')
    content = content.replace('<strong>', '<strong style="color: #fff;">')
    content = content.replace('<em>', '<em style="color: #aaa;">')
    
    styled = f"""<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; border-radius: 15px; color: #fff; font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto;">
<div style="text-align: center; margin-bottom: 30px;">
<span style="background: #00d4ff; color: #1a1a2e; padding: 8px 20px; border-radius: 20px; font-weight: bold; font-size: 14px;">DAILY DUMP</span>
</div>
{content}
<div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #333; text-align: center; color: #888; font-size: 14px;">
<p>🚀 Always learning, always growing!</p>
</div>
</div>"""
    return styled

def publish_all():
    """Publish generated content to all sites - only if there's actual content for today"""
    title, content = generate_daily_dump()
    
    # If there's no content for today, don't publish anything
    if title is None or content is None:
        print(f"No daily dump configured for {datetime.now().strftime('%Y-%m-%d')}. Skipping publication.")
        return
    
    styled_content = generate_styled_content(title, content)
    print(f"Publishing: {title}")
    
    for site_name, site in SITES.items():
        proxy = xmlrpc.client.ServerProxy(site['url'])
        try:
            post_id = proxy.wp.newPost('1', site['user'], site['pass'], {
                'post_title': title,
                'post_content': styled_content,
                'post_status': 'publish',
                'terms': {'category': [3]}  # Category 3 = daily-dump
            })
            print(f"[OK] {site_name}: Post {post_id}")
        except Exception as e:
            print(f"[X] {site_name}: {e}")

def publish_historical(date_str):
    """Publish a specific historical daily dump"""
    if date_str not in DAILY_DUMPS:
        print(f"No dump found for {date_str}")
        return
    
    title = DAILY_DUMPS[date_str]['title']
    content = DAILY_DUMPS[date_str]['content']
    styled_content = generate_styled_content(title, content)
    print(f"Publishing historical: {title}")
    
    for site_name, site in SITES.items():
        proxy = xmlrpc.client.ServerProxy(site['url'])
        try:
            post_id = proxy.wp.newPost('1', site['user'], site['pass'], {
                'post_title': title,
                'post_content': styled_content,
                'post_status': 'publish',
                'terms': {'category': [3]}  # Category 3 = daily-dump
            })
            print(f"[OK] {site_name}: Post {post_id}")
        except Exception as e:
            print(f"[X] {site_name}: {e}")

if __name__ == '__main__':
    import sys
    print(f"Daily publishing - {datetime.now()}")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        # Publish all historical dumps
        for date in sorted(DAILY_DUMPS.keys()):
            print(f"\n--- Publishing {date} ---")
            publish_historical(date)
    elif len(sys.argv) > 1:
        # Publish specific date
        publish_historical(sys.argv[1])
    else:
        # Publish today's dump (only if content exists)
        publish_all()