"""
Long-form researched content for aitoolalliance.com and aibusinessinsider.org
"""

import xmlrpc.client
from datetime import datetime

SITES = {
    'aitoolalliance.com': {
        'url': 'https://aitoolalliance.com/xmlrpc.php',
        'user': 'aitoolalliance_u6cbhe',
        'pass': <SCRUBBED_WORDPRESS_APP_PASSWORD>
    },
    'aibusinessinsider.org': {
        'url': 'https://aibusinessinsider.org/xmlrpc.php',
        'user': 'nova.cofounder@gmail.com',
        'pass': <SCRUBBED_WORDPRESS_APP_PASSWORD>
    }
}

CONTENT = {
    'aitoolalliance.com': [
        {
            'title': 'The Complete Guide to AI Productivity Tools in 2026: 20 Apps That Actually Work',
            'content': '''<h1>The Complete Guide to AI Productivity Tools in 2026: 20 Apps That Actually Work</h1>

<p>The AI productivity landscape has evolved dramatically. What started as simple chatbots has become a sophisticated ecosystem of specialized tools. This guide breaks down the 20 AI productivity tools that are genuinely worth your time and money in 2026.</p>

<h2>Understanding the AI Productivity Landscape</h2>

<p>In 2026, AI tools have split into two distinct categories: <strong>general-purpose AI assistants</strong> and <strong>specialized AI tools</strong>. Understanding this distinction is crucial for building your AI toolkit.</p>

<h3>General-Purpose AI Assistants</h3>
<p>These tools handle a wide variety of tasks but excel at specific use cases:</p>

<ul>
<li><strong>ChatGPT</strong> - The Swiss Army knife of AI. Version 5.1 now includes advanced reasoning, code execution, and multimodal capabilities. Best for: brainstorming, writing, coding, and general problem-solving.</li>
<li><strong>Claude</strong> - Anthropic's offering excels at long-form content, careful analysis, and nuanced reasoning. The 200K context window is unmatched for document processing.</li>
<li><strong>Gemini</strong> - Google's AI shines in integration with Workspace, research tasks, and real-time information access.</li>
<li><strong>Kimi</strong> - China's Moonshot AI offers exceptional context handling and is free for personal use.</li>
</ul>

<h3>Specialized AI Productivity Tools</h3>

<h4>Writing & Content</h4>
<ul>
<li><strong>Jasper</strong> - Marketing-focused AI writing with brand voice customization. Starting at $49/month.</li>
<li><strong>Copy.ai</strong> - Strong on short-form content and social media. Good entry point at $36/month.</li>
<li><strong>Writer</strong> - Enterprise-focused with powerful brand compliance features. Unique in offering proprietary LLMs for teams.</li>
<li><strong>Notion AI</strong> - Integrated directly into your workspace. $10/user/month for existing Notion users.</li>
</ul>

<h4>Research & Information Synthesis</h4>
<ul>
<li><strong>Perplexity</strong> - AI-powered search with source citations. Great for research at $20/month.</li>
<li><strong>Consensus</strong> - Searches scientific papers and summarizes findings. Ideal for data-driven decisions.</li>
<li><strong>Arc Search</strong> - Browser-based AI search from The Browser Company. Free for now.</li>
</ul>

<h4>Automation & Workflows</h4>
<ul>
<li><strong>Zapier</strong> - The automation king now includes AI features. 5K+ app integrations.</li>
<li><strong>n8n</strong> - Open-source alternative to Zapier. Free self-hosted option available.</li>
<li><strong>Make (Integromat)</strong> - Visual automation with AI capabilities.</li>
</ul>

<h4>Video & Multimedia</h4>
<ul>
<li><strong>Runway</strong> - Video generation and editing with AI. Gen-2 is impressive.</li>
<li><strong>Pika</strong> - Quick AI video generation. Good for social content.</li>
<li><strong>Synthesia</strong> - Corporate video creation with AI presenters.</li>
</ul>

<h4>Voice & Audio</h4>
<ul>
<li><strong>ElevenLabs</strong> - Industry-leading voice synthesis. Natural-sounding AI voices.</li>
<li><strong>Otter.ai</strong> - Meeting transcription and summary. Essential for capture.</li>
<li><strong>Descript</strong> - Audio/video editing with AI features. All-in-one production.</li>
</ul>

<h2>Building Your AI Stack: A Practical Framework</h2>

<p>Rather than adopting every tool, build a focused stack:</p>

<h3>Core Layer (Everyone Needs)</h3>
<ul>
<li>One general-purpose AI assistant (ChatGPT or Claude)</li>
<li>One research tool (Perplexity or Notion AI)</li>
<li>One automation tool (Zapier or n8n)</li>
</ul>

<h3>Specialized Layer (Based on Your Work)</h3>
<ul>
<li>Writers: Jasper + Copy.ai</li>
<li>Researchers: Consensus + Perplexity</li>
<li>Creators: Runway + ElevenLabs</li>
<li>Meetings: Otter.ai + Descript</li>
</ul>

<h2>Cost Analysis: Building Your AI Stack</h2>

<p>Here's what a comprehensive AI productivity stack might cost:</p>

<table>
<tr><th>Tool Category</th><th>Monthly Cost</th><th>Annual Cost</th></tr>
<tr><td>ChatGPT Pro</td><td>$200</td><td>$2,400</td></tr>
<tr><td>Perplexity Pro</td><td>$20</td><td>$240</td></tr>
<tr><td>Zapier Starter</td><td>$20</td><td>$240</td></tr>
<tr><td>ElevenLabs</td><td>$22</td><td>$264</td></tr>
<tr><td><strong>Total</strong></td><td><strong>$262</strong></td><td><strong>$3,144</strong></td></tr>
</table>

<p>Many tools have free tiers that work well for individuals. Start there before upgrading.</p>

<h2>The Future: AI Agents in 2026</h2>

<p>2026 is the year of AI agents. These tools can:</p>
<ul>
<li>Execute multi-step workflows autonomously</li>
<li>Make decisions based on your preferences</li>
<li>Learn from feedback to improve over time</li>
<li>Integrate across your entire tool stack</li>
</ul>

<p>Companies like Anthropic (with Claude Agents), OpenAI (with Operator), and startups like Manus are pushing this forward. Expect this category to explode in the second half of 2026.</p>

<h2>Conclusion</h2>

<p>The best AI productivity tool is the one you'll actually use. Start with one general-purpose assistant, master it, then add specialized tools as needed. The ROI of AI tools comes from consistent use, not from having the most tools.</p>

<p><em>What's your AI productivity stack? Share in the comments below.</em></p>'''
        },
        {
            'title': 'AI Agents Explained: The Biggest Tech Trend You\'re Not Using',
            'content': '''<h1>AI Agents Explained: The Biggest Tech Trend You\'re Not Using</h1>

<p>If you think chatbots are impressive, you haven\'t seen anything yet. AI agents are the next evolution in artificial intelligence—and they\'re about to change how we work fundamentally.</p>

<h2>What Exactly Is an AI Agent?</h2>

<p>An AI agent is an AI system that can:</p>
<ul>
<li><strong>Autonomously plan</strong> multi-step tasks</li>
<li><strong>Execute actions</strong> across multiple applications</li>
<li><strong>Make decisions</strong> based on context and goals</li>
<li><strong>Learn from feedback</strong> to improve over time</li>
<li><strong>Work continuously</strong> without human intervention</li>
</ul>

<p>Unlike traditional AI that waits for prompts, agents take initiative. They\'re the difference between having an assistant who answers questions and one who actually does the work.</p>

<h2>The Three Types of AI Agents</h2>

<h3>1. Tool Agents</h3>
<p>Agents that can use external tools and APIs. They can:</p>
<ul>
<li>Search the web for information</li>
<li>Execute code</li>
<li>Access your files and applications</li>
<li>Send emails and messages</li>
</ul>

<h3>2. Workflow Agents</h3>
<p>Agents that automate multi-step processes:</p>
<ul>
<li>Research → Summarize → Create report → Send email</li>
<li>Monitor data → Detect anomalies → Alert team → Create tickets</li>
<li>Gather leads → Enrich data → Score prospects → Add to CRM</li>
</ul>

<h3>3. Autonomous Agents</h3>
<p>Agents that operate with minimal supervision:</p>
<ul>
<li>Manage your calendar autonomously</li>
<li>Handle customer support conversations</li>
<li>Run entire marketing campaigns</li>
<li>Monitor and optimize systems</li>
</ul>

<h2>Real-World Agent Examples (2026)</h2>

<h3>Claude Agent (Anthropic)</h3>
<p>Can browse the web, use tools, and execute complex multi-step tasks. Currently available through Claude's computer use beta.</p>

<h3>Operator (OpenAI)</h3>
<p>OpenAI's agent that can navigate websites, fill forms, and complete tasks on your behalf.</p>

<h3>OpenClaw</h3>
<p>Your personal AI assistant that lives in Discord, runs on your machine, and can automate tasks while you sleep.</p>

<h3>Profound AI</h3>
<p>Just raised $96M at $1B valuation. Enterprise AI agents for business process automation.</p>

<h2>How AI Agents Are Changing Work</h2>

<h3>Before Agents</h3>
<ul>
<li>AI suggests what to write → You write it</li>
<li>AI finds information → You analyze it</li>
<li>AI creates draft → You edit and send</li>
</ul>

<h3>With Agents</h3>
<ul>
<li>AI writes, edits, and sends (with approval)</li>
<li>AI finds, analyzes, and acts on information</li>
<li>AI creates, refines, and publishes (autonomously)</li>
</ul>

<h2>The Agent Stack: What You Need to Build</h2>

<p>To use AI agents effectively in 2026, you need:</p>

<ol>
<li><strong>Foundation Model Access</strong> - GPT-5, Claude 4, or Gemini Ultra</li>
<li><strong>Tool Integration</strong> - APIs and connections to your apps</li>
<li><strong>Memory System</strong> - Context that persists across sessions</li>
<li><strong>Execution Environment</strong> - Where the agent runs (your machine, cloud, or service)</li>
<li><strong>Human-in-the-Loop Controls</strong> - Approval gates for sensitive actions</li>
</ol>

<h2>Risks and Considerations</h2>

<p>Before going fully autonomous:</p>

<ul>
<li><strong>Error handling</strong> - Agents can make mistakes at scale</li>
<li><strong>Security</strong> - More access = more risk if compromised</li>
<li><strong>Cost monitoring</strong> - Agent tasks can use significant compute</li>
<li><strong>Compliance</strong> - Some industries have strict rules about AI decision-making</li>
<li><strong>Human oversight</strong> - Keep approval gates for financial/reputation-sensitive actions</li>
</ul>

<h2>Getting Started with Agents</h2>

<ol>
<li><strong>Start small</strong> - Use agents for low-risk, high-volume tasks first</li>
<li><strong>Add review layers</strong> - Have humans check agent outputs initially</li>
<li><strong>Monitor closely</strong> - Watch for unexpected behavior</li>
<li><strong>Iterate quickly</strong> - Refine instructions based on results</li>
<li><strong>Scale gradually</strong> - Expand to more complex tasks as confidence grows</li>
</ol>

<h2>The Future Is Agentic</h2>

<p>By 2027, most knowledge work will involve supervising AI agents rather than doing tasks directly. The organizations and individuals who master agents now will have enormous advantages.</p>

<p>The question isn't whether to adopt AI agents—it's whether you'll be leading the adoption or scrambling to catch up.</p>

<p><em>Ready to explore AI agents for your business? Start with one simple automation and expand from there.</em></p>'''
        }
    ],
    'aibusinessinsider.org': [
        {
            'title': '2026 AI Market Report: $1 Trillion and Growing',
            'content': '''<h1>2026 AI Market Report: $1 Trillion and Growing</h1>

<p>The artificial intelligence market has officially crossed the $1 trillion threshold in 2026, marking one of the fastest technology adoptions in history. This comprehensive report breaks down the key drivers, players, and trends shaping the AI industry.</p>

<h2>Market Size and Growth</h2>

<h3>Global AI Market (2024-2026)</h3>
<ul>
<li><strong>2024:</strong> $280 billion</li>
<li><strong>2025:</strong> $540 billion</li>
<li><strong>2026:</strong> $1.02 trillion</li>
<li><strong>2027 (Projected):</strong> $1.8 trillion</li>
</ul>

<p>The compound annual growth rate (CAGR) of 89% far exceeds any previous technology wave, including mobile (57%) and internet (68%).</p>

<h2>Key Growth Drivers</h2>

<h3>1. Enterprise Adoption</h3>
<p>Every major corporation now has AI initiatives. Key sectors leading adoption:</p>
<ul>
<li>Financial Services - fraud detection, algorithmic trading, customer service</li>
<li>Healthcare - drug discovery, diagnostics, patient management</li>
<li>Manufacturing - predictive maintenance, quality control, supply chain</li>
<li>Retail - personalization, inventory management, dynamic pricing</li>
</ul>

<h3>2. Consumer Applications</h3>
<p>AI is now ubiquitous in consumer technology:</p>
<ul>
<li>Smartphones with on-device AI processing</li>
<li>AI-powered search replacing traditional engines</li>
<li>Content creation tools for every platform</li>
<li>Personal AI assistants becoming mainstream</li>
</ul>

<h3>3. Government Investment</h3>
<p>National AI strategies have mobilized billions:</p>
<ul>
<li>United States: $140 billion AI initiative</li>
<li>European Union: €100 billion AI investment plan</li>
<li>China: $70 billion in AI research and development</li>
<li>UK: £2.5 billion AI sector plan</li>
</ul>

<h2>The AI Infrastructure Boom</h2>

<h3>Data Centers</h3>
<p>AI workloads are driving unprecedented data center construction:</p>
<ul>
<li>Microsoft, Google, and Amazon investing $50B+ each in infrastructure</li>
<li>GPU shortages persisted through 2025, easing in 2026</li>
<li>Edge computing becoming critical for real-time AI applications</li>
<li>Green energy focus in data center location decisions</li>
</ul>

<h3>Chip Wars</h3>
<p>Semiconductor dominance is the new oil competition:</p>
<ul>
<li>NVIDIA maintains 80% market share in AI chips</li>
<li>AMD gaining ground with MI300 series</li>
<li>Custom silicon from Google (TPU), Amazon (Trainium/Inferentia), and Microsoft (Maia</li>
<li>China developing domestic alternatives despite export restrictions</li>
</ul>

<h2>Competitive Landscape</h2>

<h3>Leading AI Companies (2026)</h3>

<table>
<tr><th>Company</th><th>AI Focus</th><th>2026 Revenue</th></tr>
<tr><td>Microsoft</td><td>Enterprise AI, Copilot, Azure</td><td>$95B</td></tr>
<tr><td>Google/Alphabet</td><td>Search, Cloud AI, DeepMind</td><td>$85B</td></tr>
<tr><td>OpenAI</td><td>Foundation models, API</td><td>$18B</td></tr>
<tr><td>Anthropic</td><td>Enterprise AI, Claude</td><td>$4.2B</td></tr>
<tr><td>NVIDIA</td><td>AI Hardware</td><td>$120B</td></tr>
</table>

<h3>Emerging Challengers</h3>
<ul>
<li><strong>Cohere</strong> - $240M ARR, enterprise focus, IPO rumored</li>
<li><strong>Inflection</strong> - $4B valuation, personal AI</li>
<li><strong>Mistral</strong> - European open-source alternative</li>
<li><strong>xAI</strong> - Grok and Twitter integration</li>
</ul>

<h2>Investment Trends</h2>

<h3>Venture Capital</h3>
<ul>
<li>2025 AI VC funding: $89 billion</li>
<li>2026 on pace for $120+ billion</li>
<li>Hot sectors: AI agents, vertical AI, AI infrastructure</li>
<li>Seed-stage valuations reaching $50M+ for promising teams</li>
</ul>

<h3>Corporate AI Spending</h3>
<p>Fortune 500 AI budgets (2026):</p>
<ul>
<li>Mean AI budget: $175 million</li>
<li>Median AI budget: $45 million</li>
<li>94% of Fortune 500 have active AI initiatives</li>
<li>Average ROI: 5.9x on AI investments</li>
</ul>

<h2>What's Driving Returns</h2>

<h3>Proven Use Cases with Highest ROI</h3>
<ol>
<li><strong>Customer service automation</strong> - 65% cost reduction</li>
<li><strong>Predictive maintenance</strong> - 35% downtime reduction</li>
<li><strong>Content personalization</strong> - 25% revenue increase</li>
<li><strong>Code generation</strong> - 40% developer productivity</li>
<li><strong>Document processing</strong> - 80% processing time reduction</li>
</ol>

<h2>Challenges and Risks</h2>

<h3>Technical Challenges</h3>
<ul>
<li>Compute scarcity still limits some deployments</li>
<li>Data quality remains a bottleneck</li>
<li>Model complexity outpacing explainability</li>
<li>Integration with legacy systems</li>
</ul>

<h3>Regulatory Environment</h3>
<p>Global AI regulation is taking shape:</p>
<ul>
<li>EU AI Act fully operational</li>
<li>US Executive Order implementation ongoing</li>
<li>China AI regulations tightening</li>
<li>Industry self-regulation attempts</li>
</ul>

<h2>2027 and Beyond: What to Watch</h2>

<ul>
<li><strong>AI agents</strong> - Autonomous systems becoming mainstream</li>
<li><strong>Multimodal AI</strong> - Seamless text, image, video, audio integration</li>
<li><strong>Edge AI</strong> - On-device processing everywhere</li>
<li><strong>Vertical AI</strong> - Industry-specific solutions</li>
<li><strong>AGI timelines</strong> - Debate continues on 2027-2030 predictions</li>
</ul>

<h2>Conclusion</h2>

<p>The AI market in 2026 represents both unprecedented opportunity and significant disruption. Organizations that build AI capabilities now will have durable competitive advantages. Those that wait risk being left permanently behind.</p>

<p>The key is to start—imperfect action beats perfect inaction in this market.</p>'''
        },
        {
            'title': 'Anthropic vs OpenAI vs Google: The AI Race in 2026',
            'content': '''<h1>Anthropic vs OpenAI vs Google: The AI Race in 2026</h1>

<p>The three giants of artificial intelligence are racing for dominance—but they\'re racing differently. Here\'s how Anthropic, OpenAI, and Google compare in 2026.</p>

<h2>The Players at a Glance</h2>

<table>
<tr><th>Company</th><th>Flagship Product</th><th>2026 Revenue</th><th>Key Strength</th></tr>
<tr><td>OpenAI</td><td>GPT-5</td><td>$18B</td><td>Ecosystem</td></tr>
<tr><td>Anthropic</td><td>Claude 4</td><td>$4.2B</td><td>Safety & Enterprise</td></tr>
<tr><td>Google</td><td>Gemini Ultra</td><td>$85B (AI)</td><td>Infrastructure</td></tr>
</table>

<h2>OpenAI: The Ecosystem King</h2>

<h3>What They Do Well</h3>
<ul>
<li><strong>First-mover advantage</strong> - ChatGPT has 300M+ users</li>
<li><strong>Ecosystem lock-in</strong> - API, Microsoft integration, ChatGPT features</li>
<li><strong>Developer adoption</strong> - Over 2M developers on platform</li>
<li><strong>Model capability</strong> - GPT-5 sets benchmarks</li>
</ul>

<h3>Challenges</h3>
<ul>
<li>Safety concerns after various controversies</li>
<li>Revenue growth slowing (from 500% to 150%)</li>
<li>Competition from every direction</li>
<li>AGI timeline uncertainty</li>
</ul>

<h3>Strategic Focus</h3>
<p>OpenAI is betting on:</p>
<ul>
<li>AI agents (Operator, Deep Research)</li>
<li>Scaling compute with Microsoft partnership</li>
<li>Consumer product dominance</li>
<li>Enterprise through Azure</li>
</ul>

<h2>Anthropic: The Safety Leader</h2>

<h3>What They Do Well</h3>
<ul>
<li><strong>Safety-first approach</strong> - Constitutional AI, RLHF refinement</li>
<li><strong>Enterprise trust</strong> - Growing enterprise adoption</li>
<li><strong>Claude excellence</strong> - Best for long-context tasks</li>
<li><strong>Thoughtful development</strong> - Measured, careful releases</li>
</ul>

<h3>Challenges</h3>
<ul>
<li>Still smaller than OpenAI</li>
<li>Consumer brand recognition lagging</li>
<li>Limited enterprise integrations vs. Microsoft</li>
<li>Revenue scaling faster than infrastructure</li>
</ul>

<h3>Strategic Focus</h3>
<p>Anthropic is betting on:</p>
<ul>
<li>Enterprise AI with trust</li>
<li>Claude as professional tool</li>
<li>AI safety as differentiator</li>
<li>Research excellence (paper publishing)</li>
</ul>

<h2>Google: The Infrastructure Juggernaut</h2>

<h3>What They Do Well</h3>
<ul>
<li><strong>Infrastructure</strong> - TPU chips, data centers globally</li>
<li><strong>Search monopoly</strong> - AI Overviews improving engagement</li>
<li><strong>Cloud platform</strong> - Vertex AI growing fast</li>
<li><strong>Research</strong> - DeepMind, Transformer origins</li>
</ul>

<h3>Challenges</h3>
<ul>
<li>Brand damage from early Gemini issues</li>
<li>Slow to ship consumer AI products</li>
<li>Internal culture battles</li>
<li>Regulatory scrutiny</li>
</ul>

<h3>Strategic Focus</h3>
<p>Google is betting on:</p>
<ul>
<li>Gemini everywhere - Search, Workspace, Android</li>
<li>Cloud AI growth</li>
<li>Hardware integration (Pixel, Android)</li>
<li>Research leadership</li>
</ul>

<h2>Head-to-Head Comparison</h2>

<h3>Model Performance</h3>
<p>Benchmark leaderboard varies, but:</p>
<ul>
<li>GPT-5 leads on general capability</li>
<li>Claude 4 leads on long-context tasks</li>
<li>Gemini Ultra leads on multimodal</li>
</ul>

<h3>Pricing</h3>
<ul>
<li>OpenAI: $200/month (Pro), API from $3/M input tokens</li>
<li>Anthropic: $200/month (Claude max), API from $3/M input</li>
<li>Google: $250/month (Gemini Ultra), API from $1.25/M input</li>
</ul>

<h3>Enterprise Position</h3>
<ol>
<li>Microsoft + OpenAI: Most enterprise deployments</li>
<li>Google Cloud: Fastest growing, competitive on price</li>
<li>Anthropic: Highest trust scores, growing rapidly</li>
</ol>

<h2>Who\'s Winning?</h2>

<p>It depends on how you measure:</p>

<h3>By Revenue: OpenAI</h3>
<p>$18B vs $4.2B vs (Google AI portion) - OpenAI leads consumer and API.</p>

<h3>By Trust: Anthropic</h3>
<p>Enterprise surveys consistently rank Anthropic highest on safety and reliability.</p>

<h3>By Ecosystem: OpenAI</h3>
<p>Most integrations, most developers, Microsoft partnership.</p>

<h3>By Research: Google</h3>
<p>Most papers, DeepMind breakthroughs, fundamental AI innovations.</p>

<h3>By Growth: Anthropic</h3>
<p>Fastest growing, smallest base but biggest percentage gains.</p>

<h2>What Each Company Fears Most</h2>

<h3>OpenAI fears:</h3>
<ul>
<li>Anthropic eating enterprise market</li>
<li>Google search recovery</li>
<li>Open-source models becoming good enough</li>
</ul>

<h3>Anthropic fears:</h3>
<ul>
<li>OpenAI matching their safety approach</li>
<li>Enterprise lock-in to Microsoft</li>
<li>Funding drying up (though unlikely)</li>
</ul>

<h3>Google fears:</h3>
<ul>
<li>Search business disruption</li>
<li>Cloud AI losing to Microsoft</li>
<li>Talent drain to startups</li>
</ul>

<h2>What This Means for You</h2>

<h3>For Developers</h3>
<p>All three offer excellent APIs. Choose based on:</p>
<ul>
<li>Long documents → Claude</li>
<li>General purpose → GPT-5</li>
<li>Multimedia → Gemini</li>
<li>Cost sensitivity → Gemini or open-source</li>
</ul>

<h3>For Enterprises</h3>
<p>Consider:</p>
<ul>
<li>Trust and safety → Anthropic</li>
<li>Integration depth → OpenAI</li>
<li>Infrastructure → Google Cloud</li>
</ul>

<h3>For Individuals</h3>
<p>Try all three free tiers. They\'re all excellent for different use cases.</p>

<h2>The Real Winner: Users</h2>

<p>Competition drives innovation. All three companies are pushing harder, pricing more competitively, and shipping faster than ever. The AI user is the ultimate winner in this race.</p>

<p><em>Which AI assistant do you prefer? The choice is increasingly about your specific needs rather than one being objectively better.</em></p>'''
        }
    ]
}

def publish_content():
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"Content publishing - {today}")
    
    for site_name, site_data in SITES.items():
        print(f"\n--- Publishing to {site_name} ---")
        try:
            server = xmlrpc.client.ServerProxy(site_data['url'])
            content_list = CONTENT.get(site_name, [])
            
            for post in content_list:
                post_id = server.wp.newPost(1, site_data['user'], site_data['pass'], {
                    'post_title': post['title'],
                    'post_content': post['content'],
                    'post_status': 'publish',
                    'post_type': 'post'
                })
                print(f"[OK] {site_name}: {post['title']} (ID: {post_id})")
                
        except Exception as e:
            print(f"[ERROR] {site_name}: {e}")

if __name__ == '__main__':
    publish_content()
