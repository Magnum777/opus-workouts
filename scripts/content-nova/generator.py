"""
Content-Nova Content Generator v2
AI-powered article generator with web research for WordPress publishing.
Uses web search + AI writing to produce fresh, SEO-friendly content.
"""

import json, os, sys
from datetime import datetime

# Topic queues per site -- each site gets a tailored rotation
TOPIC_QUEUES = {
    'aitoolalliance.com': [
        'best AI tools for productivity',
        'AI writing tools comparison',
        'AI image generators ranked',
        'AI automation workflows',
        'free AI tools for small business',
        'AI meeting assistants',
        'AI voice synthesis tools',
        'AI code assistants',
        'AI video creation tools',
        'no-code AI platforms'
    ],
    'aibusinessinsider.org': [
        'AI adoption in enterprise',
        'AI ROI case studies',
        'AI regulation updates',
        'generative AI market trends',
        'AI startup funding news',
        'AI replacing jobs data',
        'AI in healthcare business',
        'AI customer service automation',
        'AI data privacy concerns',
        'AI competitive advantage'
    ],
    'aicofounderstack.com': [
        'AI cofounder tools for startups',
        'building a business with AI',
        'AI side hustle ideas',
        'solopreneur AI toolkit',
        'AI content creation for founders',
        'AI-powered marketing automation',
        'affordable AI tools for startups',
        'AI business model ideas',
        'AI product validation methods',
        'AI tools for one-person companies'
    ]
}

def pick_next_topic(site_key, state_file='content-nova-state.json'):
    """Rotate through topics so we don't repeat."""
    import os
    state_path = os.path.join(os.path.dirname(__file__), state_file)
    state = {}
    if os.path.exists(state_path):
        with open(state_path, 'r') as f:
            state = json.load(f)

    topics = TOPIC_QUEUES.get(site_key, [])
    if not topics:
        return None

    idx = state.get(site_key, 0)
    topic = topics[idx % len(topics)]
    state[site_key] = (idx + 1) % len(topics)

    with open(state_path, 'w') as f:
        json.dump(state, f)

    return topic


def generate_article(topic, site_focus, model='deep'):
    """Generate a full article with research + writing. Returns dict with title, content, excerpt."""
    # This function is designed to be called from an OpenClaw agent turn
    # where the agent performs web_search and AI writing.
    # For standalone use, it returns a template that the caller fills in.

    return {
        'topic': topic,
        'site_focus': site_focus,
        'instructions': f"""
Write a 1,200-1,800 word article for a WordPress blog focused on: {site_focus}.

Topic: {topic}

Requirements:
- Start with a compelling hook in the first paragraph
- Use H2 subheadings every 300-400 words
- Include bullet lists where appropriate
- End with a clear CTA (comment, subscribe, check tool)
- SEO-friendly title under 60 characters
- Meta description under 160 characters
- Include at least 2-3 relevant tool/product mentions (can include affiliate mentions)
- Keep tone informative but accessible
- Use bold for key terms and takeaways
- Include a "Key Takeaways" or "Bottom Line" section near the end

Output format (JSON):
{{
    "title": "...",
    "excerpt": "...",
    "content": "<h2>...</h2><p>...</p>..."
}}
"""
    }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('site', choices=list(TOPIC_QUEUES.keys()))
    parser.add_argument('--topic', help='Override auto-selected topic')
    args = parser.parse_args()

    topic = args.topic or pick_next_topic(args.site)
    if not topic:
        print('No topics configured for this site')
        sys.exit(1)

    result = generate_article(topic, 'general')
    print(json.dumps(result, indent=2))
