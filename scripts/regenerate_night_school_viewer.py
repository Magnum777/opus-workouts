#!/usr/bin/env python3
"""Regenerate night-school-viewer.html with embedded playbook index + search."""
import json, os

BASE_DIR = r"C:\Users\compj\.openclaw\workspace\docs\night-school"
OUTPUT = r"C:\Users\compj\.openclaw\workspace\docs\night-school-viewer.html"
OUTPUT_NAS = "//192.168.68.82/web/night-school-viewer.html"

def discover(base_dir):
    pbs = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.lower() == "playbook.md":
                rel = os.path.relpath(os.path.join(root, f), base_dir).replace("\\", "/")
                folder = os.path.basename(os.path.dirname(rel))
                pbs.append({"name": folder.replace("-", " "), "path": rel})
    pbs.sort(key=lambda x: x["name"])
    return pbs

def build_search_index(base_dir, pbs):
    index = {}
    for pb in pbs:
        filepath = os.path.join(base_dir, pb["path"])
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            lines = content.split("\n")
            headings = []
            body_snippets = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("#"):
                    headings.append(stripped.lstrip("# ").strip())
                elif stripped and len(body_snippets) < 25:
                    body_snippets.append(stripped)
            index[pb["path"]] = {
                "name": pb["name"],
                "headings": headings[:8],
                "text": " ".join(body_snippets)[:600]
            }
        except Exception:
            index[pb["path"]] = {"name": pb["name"], "headings": [], "text": ""}
    return index

def build_html(pbs, search_index):
    playbooks_json = json.dumps(pbs, indent=2)
    search_json = json.dumps(search_index, indent=2)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Night School Playbooks</title>
    <script src="https://cdn.jsdelivr.net/npm/marked@9/marked.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a0a0f; color: #e0e0e0; display: flex; height: 100vh; overflow: hidden; }}
        .sidebar {{ width: 300px; background: #12121a; border-right: 1px solid #2a2a3a; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; }}
        .sidebar h1 {{ font-size: 1.3rem; color: #4fc3f7; margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #2a2a3a; flex-shrink: 0; }}
        .search-box {{ width: 100%; padding: 8px 12px; border: 1px solid #2a2a3a; border-radius: 6px; background: #1a1a2e; color: #e0e0e0; font-size: 0.85rem; margin-bottom: 12px; outline: none; flex-shrink: 0; }}
        .search-box:focus {{ border-color: #4fc3f7; }}
        .search-box::placeholder {{ color: #666; }}
        .search-results {{ flex-shrink: 0; margin-bottom: 10px; }}
        .search-result-item {{ padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; color: #b0b0c0; transition: all 0.2s; }}
        .search-result-item:hover {{ background: #1e3a5f; color: #4fc3f7; }}
        .search-result-category {{ font-size: 0.7rem; color: #4fc3f7; margin-left: 8px; }}
        .no-results {{ padding: 8px 12px; color: #666; font-size: 0.8rem; }}
        .sidebar h2 {{ font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 1px; margin: 15px 0 8px; }}
        .sidebar ul {{ list-style: none; }}
        .sidebar li {{ margin: 3px 0; }}
        .sidebar a {{ color: #b0b0c0; text-decoration: none; display: block; padding: 7px 12px; border-radius: 6px; font-size: 0.85rem; transition: all 0.2s; }}
        .sidebar a:hover, .sidebar a.active {{ background: #1e3a5f; color: #4fc3f7; }}
        .content {{ flex: 1; overflow-y: auto; padding: 40px; }}
        .content-inner {{ max-width: 900px; margin: 0 auto; }}
        .content h1 {{ color: #4fc3f7; margin-bottom: 20px; }}
        .content h2 {{ color: #81d4fa; margin: 30px 0 15px; border-bottom: 1px solid #2a2a3a; padding-bottom: 10px; }}
        .content h3 {{ color: #a5d6fa; margin: 25px 0 10px; }}
        .content p {{ margin-bottom: 15px; line-height: 1.7; }}
        .content a {{ color: #81d4fa; }}
        .content code {{ background: #1a1a2e; padding: 2px 6px; border-radius: 3px; font-family: 'SF Mono', Monaco, monospace; font-size: 0.9em; }}
        .content pre {{ background: #1a1a2e; padding: 15px; border-radius: 8px; overflow-x: auto; margin: 15px 0; }}
        .content pre code {{ background: transparent; padding: 0; }}
        .content ul, .content ol {{ margin: 15px 0; padding-left: 25px; }}
        .content li {{ margin: 8px 0; }}
        .content blockquote {{ border-left: 3px solid #4fc3f7; padding-left: 20px; margin: 20px 0; color: #b0b0c0; }}
        .content table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .content th, .content td {{ border: 1px solid #2a2a3a; padding: 10px; text-align: left; }}
        .content th {{ background: #1a1a2e; color: #4fc3f7; }}
        .content img {{ max-width: 100%; border-radius: 8px; margin: 20px 0; }}
        .loading {{ text-align: center; color: #666; padding: 50px; }}
        .edit-btn {{ position: fixed; bottom: 20px; right: 20px; background: #4fc3f7; color: #0a0a0f; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; box-shadow: 0 4px 12px rgba(79, 195, 247, 0.3); transition: transform 0.2s; }}
        .edit-btn:hover {{ transform: translateY(-2px); }}
        .count-badge {{ float: right; background: #2a2a3a; color: #888; font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; }}
    </style>
</head>
<body>
    <aside class="sidebar">
        <h1>&#129437; Night School <span id="total-count" class="count-badge">{len(pbs)}</span></h1>
        <input type="text" class="search-box" id="searchBox" placeholder="Search playbooks...">
        <div id="searchResults" class="search-results"></div>
        <nav id="nav" style="flex:1;overflow-y:auto;"></nav>
    </aside>
    <main class="content">
        <div class="content-inner" id="viewer"><div class="loading">Select a playbook from the sidebar</div></div>
        <a href="#" class="edit-btn" id="editLink" style="display:none">&#9999;&#65039; Edit Markdown</a>
    </main>

    <script>
        const playbooks = {playbooks_json};
        const searchIndex = {search_json};

        function titleCase(str) {{ return str.replace(/\\b\\w/g, c => c.toUpperCase()); }}

        function getCategory(pb) {{
            const p = pb.path.toLowerCase();
            if (p.includes('/n8n/')) return 'Automation';
            if (p.includes('automation') || p.includes('cron') || p.includes('modelrelay') || p.includes('subagent')) return 'AI & Automation';
            if (p.includes('ai-') || p.includes('ml') || p.includes('nova-') || p.includes('openclaw') || p.includes('mem0')) return 'AI & Automation';
            if (p.includes('business') || p.includes('income') || p.includes('agency')) return 'Income & Business';
            if (p.includes('99design') || p.includes('freelancer') || p.includes('guru') || p.includes('toptal') || p.includes('workana') || p.includes('linkedin') || p.includes('remote')) return 'Freelance Platforms';
            if (p.includes('aws') || p.includes('bluesky') || p.includes('coinbase') || p.includes('eleven') || p.includes('mixpost') || p.includes('postiz') || p.includes('rss') || p.includes('solana') || p.includes('stripe') || p.includes('uptime') || p.includes('wordpress')) return 'Tech & Infrastructure';
            if (p.includes('creative') || p.includes('affiliate') || p.includes('print') || p.includes('web-design') || p.includes('ga-')) return 'Creative & Marketing';
            if (p.includes('eve') || p.includes('lore')) return 'Gaming & Lore';
            if (p.includes('ham') || p.includes('antenna') || p.includes('radio')) return 'Radio & Communications';
            return 'Other';
        }}

        function buildNav() {{
            const nav = document.getElementById('nav'); nav.innerHTML = '';
            const cats = {{}};
            playbooks.forEach(pb => {{ const c = getCategory(pb); if (!cats[c]) cats[c] = []; cats[c].push(pb); }});
            ['AI & Automation', 'Income & Business', 'Freelance Platforms', 'Tech & Infrastructure', 'Creative & Marketing', 'Gaming & Lore', 'Radio & Communications', 'Other'].forEach(cat => {{
                if (!cats[cat]) return;
                cats[cat].sort((a, b) => a.name.localeCompare(b.name));
                const h2 = document.createElement('h2'); h2.textContent = cat; nav.appendChild(h2);
                const ul = document.createElement('ul');
                cats[cat].forEach(file => {{
                    const li = document.createElement('li');
                    const a = document.createElement('a');
                    a.href = '#'; a.textContent = titleCase(file.name); a.dataset.path = file.path;
                    a.onclick = (e) => {{ e.preventDefault(); loadPlaybook(file.path, titleCase(file.name)); highlightActive(file.name); }};
                    li.appendChild(a); ul.appendChild(li);
                }});
                nav.appendChild(ul);
            }});
        }}

        function highlightActive(name) {{
            document.querySelectorAll('.sidebar a').forEach(l => l.classList.remove('active'));
            document.querySelectorAll('.sidebar a').forEach(a => {{ if (a.textContent.toLowerCase() === name.toLowerCase()) a.classList.add('active'); }});
        }}

        function doSearch(query) {{
            const resultsDiv = document.getElementById('searchResults');
            if (!query || query.length < 2) {{ resultsDiv.innerHTML = ''; resultsDiv.classList.remove('active'); return; }}
            const q = query.toLowerCase();
            const hits = [];
            for (const path in searchIndex) {{
                const entry = searchIndex[path];
                let score = 0;
                if (entry.name.toLowerCase().includes(q)) score += 10;
                if (entry.text.toLowerCase().includes(q)) score += 3;
                entry.headings.forEach(h => {{ if (h.toLowerCase().includes(q)) score += 5; }});
                if (score > 0) hits.push({{ path: path, name: entry.name, score: score, cat: getCategory({{path: path, name: entry.name}}) }});
            }}
            hits.sort((a, b) => b.score - a.score);
            if (hits.length === 0) {{
                resultsDiv.innerHTML = '<div class="no-results">No results found</div>';
                resultsDiv.classList.add('active');
            }} else {{
                resultsDiv.innerHTML = hits.slice(0, 8).map(h =>
                    `<div class="search-result-item" onclick="loadPlaybook('${{h.path}}', titleCase('${{h.name}}')); highlightActive('${{h.name}}');">${{titleCase(h.name)}}<span class="search-result-category">${{h.cat}}</span></div>`
                ).join('');
                resultsDiv.classList.add('active');
            }}
        }}

        document.getElementById('searchBox').addEventListener('input', (e) => doSearch(e.target.value));
        document.getElementById('searchBox').addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') {{ e.target.value = ''; doSearch(''); }}
        }});

        async function loadPlaybook(path, name) {{
            const viewer = document.getElementById('viewer');
            viewer.innerHTML = '<div class="loading">Loading...</div>';
            document.getElementById('searchBox').value = '';
            doSearch('');
            const [filePath, fragment] = path.split('#');
            try {{
                const basePath = location.pathname.includes('/night-school/') ? '' : 'night-school/';
                const response = await fetch(`${{basePath}}${{filePath}}`);
                if (!response.ok) throw new Error('Failed to load');
                const markdown = await response.text();
                viewer.innerHTML = marked.parse(markdown);
                document.title = `${{name}} - Night School`;
                viewer.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(h => {{
                    if (!h.id) {{ h.id = h.textContent.toLowerCase().replace(/[\\u2014\\u2013]/g, ' ').replace(/[^\\w\\s-]/g, '').trim().replace(/\\s+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, ''); }}
                }});
                if (fragment) {{ setTimeout(() => {{ const el = document.getElementById(fragment); if (el) {{ el.scrollIntoView({{ behavior: 'smooth', block: 'start' }}); el.style.background = '#1e3a5f'; setTimeout(() => el.style.background = '', 2000); }} }}, 100); }}
                viewer.querySelectorAll('a').forEach(a => {{
                    const href = a.getAttribute('href'); if (!href) return;
                    const pathPart = href.split('#')[0];
                    if (pathPart.endsWith('.md') && !href.startsWith('http') && !href.startsWith('//')) {{
                        a.setAttribute('href', '#' + href);
                        a.onclick = (e) => {{ e.preventDefault(); loadPlaybook(href, a.textContent); }};
                    }}
                }});
                if (history.replaceState) {{ history.replaceState(null, null, '#' + path); }}
                const editLink = document.getElementById('editLink');
                if (location.protocol === 'file:') {{ editLink.href = `file:///C:/Users/compj/.openclaw/workspace/docs/night-school/${{filePath}}`; editLink.style.display = 'block'; }}
                else {{ editLink.style.display = 'none'; }}
            }} catch (err) {{ viewer.innerHTML = `<div class="loading">Error loading playbook: ${{err.message}}</div>`; }}
        }}

        function handleHash() {{
            const hash = location.hash.slice(1);
            if (!hash) {{ if (playbooks.length > 0) {{ loadPlaybook(playbooks[0].path, titleCase(playbooks[0].name)); highlightActive(playbooks[0].name); }} return; }}
            for (const pb of playbooks) {{
                if (pb.path === hash || hash.startsWith(pb.path + '#')) {{
                    loadPlaybook(hash, titleCase(pb.name)); highlightActive(pb.name); return;
                }}
            }}
        }}

        window.addEventListener('hashchange', handleHash);
        buildNav(); handleHash();
    </script>
</body>
</html>"""

pbs = discover(BASE_DIR)
search_idx = build_search_index(BASE_DIR, pbs)
html = build_html(pbs, search_idx)

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Wrote {len(pbs)} playbooks + search to {OUTPUT}")

with open(OUTPUT_NAS, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Wrote {len(pbs)} playbooks + search to NAS {OUTPUT_NAS}")
