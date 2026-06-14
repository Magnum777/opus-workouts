"""
Research Context Reader
Loads the daily research brief and extracts actionable signals for TradeBot.
"""

import os
import re

RESEARCH_DIR = os.path.join(os.path.dirname(__file__), "research")

def _find_latest_report():
    """Find most recent research report"""
    if not os.path.exists(RESEARCH_DIR):
        return None
    files = sorted([f for f in os.listdir(RESEARCH_DIR) if f.endswith('.md')], reverse=True)
    if not files:
        return None
    return os.path.join(RESEARCH_DIR, files[0])

def _load_report_text(path):
    """Load report text"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def _extract_section(text, header):
    """Extract content under a markdown header"""
    pattern = rf'##?\s*{re.escape(header)}\s*\n(.*?)(?=\n##|\Z)'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""

def _extract_list_items(text, section_header):
    """Extract bullet list items from a section"""
    section = _extract_section(text, section_header)
    items = []
    for line in section.split('\n'):
        line = line.strip()
        if line.startswith('- ') or line.startswith('* '):
            items.append(line[2:].strip())
        elif re.match(r'^\d+\.\s', line):
            items.append(re.sub(r'^\d+\.\s', '', line).strip())
    return items

def _extract_risk_level(text):
    """Extract overall risk level from report"""
    for line in text.split('\n'):
        if re.search(r'Risk level[:\s]*(High|Medium|Low)', line, re.IGNORECASE):
            match = re.search(r'(High|Medium|Low)', line, re.IGNORECASE)
            if match:
                return match.group(1).lower()
    return "medium"

def _extract_market_mood(text):
    """Extract market mood"""
    for line in text.split('\n'):
        match = re.search(r'Market mood[:\s]*(.*?)(?:$|\|)', line, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return "neutral"

def _extract_priority_sectors(text):
    """Extract priority sectors from Scout Guidance"""
    guidance = _extract_section(text, "Scout Guidance")
    sectors = []
    for line in guidance.split('\n'):
        if 'priority' in line.lower() or 'watch' in line.lower() or 'sectors' in line.lower():
            # Look for keywords after dashes or colons
            parts = re.split(r'[:\-\u2013]', line)
            if len(parts) > 1:
                for part in parts[1:]:
                    sectors.extend([s.strip().lower() for s in part.split(',')])
    return [s for s in sectors if s and len(s) > 2]

def _extract_avoid_tokens(text):
    """Extract tokens/sectors to avoid from Scout Guidance"""
    guidance = _extract_section(text, "Scout Guidance")
    avoids = []
    for line in guidance.split('\n'):
        if 'avoid' in line.lower() or 'red flag' in line.lower() or 'skip' in line.lower():
            parts = re.split(r'[:\-\u2013]', line)
            if len(parts) > 1:
                for part in parts[1:]:
                    avoids.extend([s.strip().lower() for s in part.split(',')])
    return [a for a in avoids if a and len(a) > 2]

def _extract_sizing_adjustment(text):
    """Extract sizing adjustment from Scout Guidance"""
    guidance = _extract_section(text, "Scout Guidance")
    for line in guidance.split('\n'):
        if 'sizing' in line.lower() and ('reduce' in line.lower() or 'increase' in line.lower()):
            if 'reduce' in line.lower():
                return 'reduce'
            elif 'increase' in line.lower():
                return 'increase'
    return None

def _is_ai_token(symbol, fdv=None):
    """Check if a token is AI-related by symbol"""
    ai_keywords = ['ai', 'zai', 'tao', 'neural', 'brain', 'intel', 'mind', 'cortex', 'bot', 'agent', 'gpt', 'llm']
    sym_lower = symbol.lower()
    return any(k in sym_lower for k in ai_keywords)

def _is_metaverse_token(symbol, fdv=None):
    """Check if a token is metaverse-related"""
    meta_keywords = ['meta', 'verse', 'vr', 'ar', 'game', 'nft']
    sym_lower = symbol.lower()
    return any(k in sym_lower for k in meta_keywords)

def load_research_context():
    """
    Load and parse the latest research brief into actionable context.
    Returns dict with:
    - report_date: str
    - market_mood: str (bullish/bearish/neutral)
    - risk_level: str (high/medium/low)
    - priority_sectors: list[str]
    - avoid_sectors: list[str]
    - avoid_tokens: list[str]
    - sizing_adjustment: str (reduce/increase/None)
    - ai_priority: bool
    - metaverse_priority: bool
    - source: str (path to report)
    """
    path = _find_latest_report()
    if not path:
        return {
            "report_date": None,
            "market_mood": "neutral",
            "risk_level": "medium",
            "priority_sectors": [],
            "avoid_sectors": [],
            "avoid_tokens": [],
            "sizing_adjustment": None,
            "ai_priority": False,
            "metaverse_priority": False,
            "source": None
        }

    text = _load_report_text(path)
    if not text:
        return {
            "report_date": None,
            "market_mood": "neutral",
            "risk_level": "medium",
            "priority_sectors": [],
            "avoid_sectors": [],
            "avoid_tokens": [],
            "sizing_adjustment": None,
            "ai_priority": False,
            "metaverse_priority": False,
            "source": path
        }

    priority_sectors = _extract_priority_sectors(text)
    avoid = _extract_avoid_tokens(text)

    # Detect AI priority
    ai_priority = any('ai' in s for s in priority_sectors)
    # Detect metaverse priority
    metaverse_priority = any(k in ' '.join(priority_sectors) for k in ['metaverse', 'vr', 'game'])

    return {
        "report_date": os.path.basename(path).replace('.md', ''),
        "market_mood": _extract_market_mood(text),
        "risk_level": _extract_risk_level(text),
        "priority_sectors": priority_sectors,
        "avoid_sectors": avoid,
        "avoid_tokens": avoid,
        "sizing_adjustment": _extract_sizing_adjustment(text),
        "ai_priority": ai_priority,
        "metaverse_priority": metaverse_priority,
        "source": path,
        "raw_text": text
    }


def matches_sector(symbol, category, context):
    """
    Check if a token matches research priority sectors.
    Returns True if token should be prioritized, False if neutral.
    """
    if not context or not context.get("priority_sectors"):
        return True  # No context = allow all

    sym_lower = symbol.lower()
    cat_lower = (category or "").lower()
    priority = [s.lower() for s in context["priority_sectors"]]

    # AI tokens
    if context.get("ai_priority") and _is_ai_token(symbol):
        return True

    # Metaverse tokens
    if context.get("metaverse_priority") and _is_metaverse_token(symbol):
        return True

    # Meme coin priority (if in research)
    if 'meme' in priority and ('meme' in cat_lower or 'pump' in sym_lower):
        return True

    # Utility/DEX tokens
    if any('util' in p for p in priority) and cat_lower == 'utility':
        return True
    if 'dex' in priority and cat_lower == 'dex':
        return True

    # Default: if we have specific priorities, non-matching tokens get deprioritized
    return len(priority) == 0


def should_avoid(symbol, mint, context):
    """Check if a token should be avoided based on research guidance"""
    if not context:
        return False

    sym_lower = symbol.lower()
    mint_lower = (mint or "").lower()
    avoid = [a.lower() for a in context.get("avoid_tokens", [])]
    avoid_sectors = [a.lower() for a in context.get("avoid_sectors", [])]

    # Check symbol against avoid list
    for a in avoid:
        if a in sym_lower:
            return True, f"Avoid list match: {a}"

    # Check for GO bounty / toxic flags
    if any(k in ' '.join(avoid_sectors) for k in ['bounty', 'toxic', 'go']):
        if 'go' in sym_lower or 'bounty' in sym_lower:
            return True, "GO bounty flagged"

    return False, None


if __name__ == "__main__":
    ctx = load_research_context()
    print(f"Research Context Loaded:")
    print(f"  Date: {ctx['report_date']}")
    print(f"  Mood: {ctx['market_mood']}")
    print(f"  Risk: {ctx['risk_level']}")
    print(f"  Priority Sectors: {ctx['priority_sectors']}")
    print(f"  Avoid: {ctx['avoid_tokens']}")
    print(f"  Sizing: {ctx['sizing_adjustment']}")
    print(f"  AI Priority: {ctx['ai_priority']}")
    print(f"  Source: {ctx['source']}")
