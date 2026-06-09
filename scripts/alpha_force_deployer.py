#!/usr/bin/env python3
"""
Alpha Force Deployment System
Command: "Deploy Alpha Force"

Generates tactical deployment PDFs with:
- Auto-incrementing Alpha Force number
- Random toon names (non-EVE word + 6 digits + ####)
- Random corp names (verified on EveWho)
- Tactical military briefing aesthetic
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER
import random
import json
import os
import sys
from datetime import datetime

# Database file
DB_FILE = 'alpha_force_db.json'

# Word lists for generation
NON_EVE_WORDS = [
    "Mover", "Runner", "Walker", "Driver", "Rider", "Slider", "Cruiser",
    "Drifter", "Glider", "Roller", "Shifter", "Tracker", "Stalker",
    "Sneaker", "Creeper", "Hunter", "Seeker", "Finder", "Watcher",
    "Keeper", "Holder", "Trader", "Dealer", "Broker", "Worker",
    "Helper", "Fixer", "Maker", "Builder", "Grower", "Planter"
]

CORP_WORDS = [
    # Nature/Geography
    "Amber", "Azure", "Crimson", "Cobalt", "Emerald", "Golden", "Ivory", "Jade", "Onyx", "Ruby", "Sapphire", "Silver", "Verdant",
    "Arctic", "Coastal", "Desert", "Forest", "Marine", "Mountain", "Oceanic", "Prairie", "Tundra", "Volcanic",
    "Northern", "Southern", "Eastern", "Western", "Central", "Upper", "Lower",
    
    # Industry/Business (non-space)
    "Atlas", "Beacon", "Bridge", "Cartel", "Catalyst", "Citadel", "Crest", "Crown", "Dynasty", "Empire", "Fortress", 
    "Foundry", "Frontier", "Haven", "Horizon", "Legacy", "Monolith", "Nexus", "Odyssey", "Paragon", "Pinnacle", 
    "Providence", "Sentinel", "Sovereign", "Summit", "Syndicate", "Titan", "Unity", "Vanguard", "Vertex", "Zenith",
    
    # Abstract/Conceptual
    "Apex", "Axis", "Cipher", "Clarity", "Crescent", "Echo", "Element", "Flux", "Harmony", "Helix", "Icon", 
    "Infinity", "Keystone", "Lumen", "Matrix", "Momentum", "Nova", "Origin", "Prime", "Quantum", "Radiant", 
    "Resonance", "Solaris", "Spectrum", "Stratum", "Synchron", "Threshold", "Vector", "Vista", "Zen",
    
    # Suffixes - more creative, no LLC
    "Holdings", "Ventures", "Enterprises", "Industries", "Logistics", "Solutions", "Systems", 
    "Group", "Consortium", "Collective", "Partners", "Alliance", "Guild", "Society", "Association",
    "Trading", "Exchange", "Commerce", "Capital", "Investments", "Assets", "Resources",
    "Works", "Works Co", "Corp", "Company", "Ltd", "International", "Worldwide", "Global",
    "Foundation", "Trust", "Institute", "Agency", "Bureau", "Office", "Department",
    "Division", "Branch", "Unit", "Sector", "Zone", "Region", "District", "Quarter"
]

def load_db():
    """Load Alpha Force database"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {"alpha_forces": [], "next_number": 1}

def save_db(db):
    """Save Alpha Force database"""
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

import random
from datetime import datetime, timedelta

def get_next_alpha_force_number():
    """Generate random Alpha Force number (1-999) and ensure no duplicates within 24 hours"""
    db = load_db()
    
    # Get all recently used numbers (within last 24 hours)
    now = datetime.now()
    recent_numbers = set()
    for record in db.get("alpha_forces", []):
        deployed_time = datetime.fromisoformat(record.get("deployed_date", "2000-01-01"))
        if (now - deployed_time) < timedelta(hours=24):
            recent_numbers.add(record.get("alpha_force_number"))
    
    # Generate random number 1-999 not used recently
    available_numbers = list(set(range(1, 1000)) - recent_numbers)
    
    if not available_numbers:
        # If all numbers used in last 24h, use oldest one
        return random.randint(1, 999)
    
    number = random.choice(available_numbers)
    return number

def generate_toon_name():
    """Generate toon name: Non-EVE word + 6 identical digits + ####"""
    word = random.choice(NON_EVE_WORDS)
    digit = random.choice('0123456789')
    six_digits = digit * 6
    return f"{word}{six_digits}####"

def generate_corp_name():
    """Generate creative corp name from word lists - no LLC"""
    # Choose pattern: Word + Word + Suffix OR Word + Suffix + Suffix
    pattern = random.choice(['word_word_suffix', 'word_suffix_suffix', 'word_word_word'])
    
    if pattern == 'word_word_suffix':
        word1 = random.choice(CORP_WORDS)
        word2 = random.choice(CORP_WORDS)
        suffix = random.choice(["Holdings", "Ventures", "Enterprises", "Industries", 
                               "Solutions", "Systems", "Group", "Consortium", 
                               "Collective", "Partners", "Alliance", "Works"])
        # Ensure words are different
        while word2 == word1:
            word2 = random.choice(CORP_WORDS)
        return f"{word1} {word2} {suffix}"
    
    elif pattern == 'word_suffix_suffix':
        word = random.choice(CORP_WORDS)
        suffix1 = random.choice(["Trading", "Commerce", "Exchange", "Capital"])
        suffix2 = random.choice(["Group", "Co", "Company", "International", 
                                "Worldwide", "Global", "Trust", "Foundation"])
        return f"{word} {suffix1} {suffix2}"
    
    else:  # word_word_word
        word1 = random.choice(CORP_WORDS)
        word2 = random.choice(CORP_WORDS)
        word3 = random.choice(["Corp", "Company", "Ltd", "International", 
                              "Worldwide", "Global", "Works", "Agency"])
        while word2 == word1:
            word2 = random.choice(CORP_WORDS)
        return f"{word1} {word2} {word3}"

def check_corp_on_evewho(corp_name):
    """
    Check if corp name exists on EveWho via web search
    Returns True if available (not found), False if taken
    """
    import urllib.request
    import urllib.parse
    import ssl
    
    # Create SSL context that doesn't verify certificates
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        # Search EveWho directly
        search_name = corp_name.replace(' ', '%20')
        url = f"https://evewho.com/corp/{search_name}"
        
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # Check if page shows "not found" or "no results"
            if 'not found' in html.lower() or 'no results' in html.lower() or '404' in html:
                return True
            
            # Check if it shows actual corp data
            if 'members' in html.lower() and 'ticker' in html.lower():
                return False
                
        return True  # Assume available if check fails
        
    except Exception as e:
        print(f"EveWho check error: {e}")
        return True  # Assume available if check fails

def find_available_corp_name(max_attempts=10):
    """Generate and verify an available corp name"""
    for attempt in range(max_attempts):
        corp_name = generate_corp_name()
        print(f"Checking corp name: {corp_name}...")
        
        if check_corp_on_evewho(corp_name):
            print(f"[OK] {corp_name} appears available!")
            return corp_name
        else:
            print(f"[X] {corp_name} is taken, trying again...")
    
    # Fallback: add random numbers to make it unique
    corp_name = generate_corp_name()
    corp_name = corp_name.replace(" LLC", f" {random.randint(100,999)} LLC")
    print("[Warn] Using fallback name: " + corp_name)
    return corp_name

def create_deployment_pdf(alpha_force_number, toon_name, corp_name):
    """Create the tactical deployment PDF"""
    
    pdf_file = f'alpha_force_{alpha_force_number}_deployment.pdf'
    
    def draw_tactical_background(canvas, doc):
        canvas.saveState()
        # Dark charcoal background
        canvas.setFillColor(colors.HexColor('#1a1a1a'))
        canvas.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
        
        # Red footer bar at bottom
        canvas.setFillColor(colors.HexColor('#e74c3c'))
        canvas.rect(0, 0, letter[0], 40, fill=1, stroke=0)
        
        canvas.restoreState()
    
    doc = SimpleDocTemplate(pdf_file, pagesize=letter,
                            rightMargin=60, leftMargin=60,
                            topMargin=60, bottomMargin=60)
    
    Story = []
    styles = getSampleStyleSheet()
    
    # Styles
    title_style = ParagraphStyle(
        'TacticalTitle', parent=styles['Heading1'],
        fontSize=26, textColor=colors.HexColor('#e74c3c'),
        spaceAfter=6, alignment=TA_CENTER, fontName='Helvetica-Bold'
    )
    
    iteration_style = ParagraphStyle(
        'Iteration', parent=styles['Normal'],
        fontSize=14, textColor=colors.HexColor('#e74c3c'),
        spaceAfter=20, alignment=TA_CENTER, fontName='Helvetica-Bold'
    )
    
    classified_style = ParagraphStyle(
        'Classified', parent=styles['Normal'],
        fontSize=11, textColor=colors.HexColor('#f39c12'),
        spaceAfter=8, alignment=TA_CENTER, fontName='Helvetica-Bold'
    )
    
    section_style = ParagraphStyle(
        'SectionHeader', parent=styles['Heading3'],
        fontSize=13, textColor=colors.HexColor('#f39c12'),
        spaceAfter=12, spaceBefore=20, fontName='Helvetica-Bold'
    )
    
    label_style = ParagraphStyle(
        'DataLabel', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#95a5a6'),
        spaceAfter=2, fontName='Helvetica'
    )
    
    value_style = ParagraphStyle(
        'DataValue', parent=styles['Normal'],
        fontSize=12, textColor=colors.white,
        spaceAfter=8, fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'BodyText', parent=styles['Normal'],
        fontSize=10, textColor=colors.white,
        spaceAfter=10, fontName='Helvetica'
    )
    
    secondary_style = ParagraphStyle(
        'Secondary', parent=styles['Normal'],
        fontSize=9, textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=6, fontName='Helvetica'
    )
    
    # Title
    Story.append(Paragraph('ALPHA FORCE DEPLOYMENT', title_style))
    Story.append(Paragraph(f'ALPHA FORCE {alpha_force_number}', iteration_style))
    
    # Red line
    Story.append(HRFlowable(width="100%", thickness=2, 
                           color=colors.HexColor('#e74c3c'), 
                           spaceBefore=10, spaceAfter=15))
    
    # Classified
    Story.append(Paragraph('[ CLASSIFIED ]', classified_style))
    Story.append(Spacer(1, 0.1*inch))
    
    # Data Box
    data_data = [
        [Paragraph('NAME:', label_style), Paragraph(toon_name, value_style)],
        [Paragraph('RACE:', label_style), Paragraph('Caldari', value_style)],
        [Paragraph('CORP:', label_style), Paragraph(corp_name, value_style)],
    ]
    
    data_table = Table(data_data, colWidths=[1.2*inch, 4*inch])
    data_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2c2c2c')),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#e74c3c')),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    Story.append(data_table)
    Story.append(Spacer(1, 0.25*inch))
    
    # Instructions
    Story.append(Paragraph('DEPLOYMENT INSTRUCTIONS', section_style))
    
    Story.append(Paragraph('<b>1. CREATE ALPHA ACCOUNT:</b>', body_style))
    Story.append(Paragraph('https://www.eveonline.com/signup?invc=66131c9b-1695-44e7-874e-76dd195e4f63', secondary_style))
    Story.append(Paragraph('(or use your own referral)', secondary_style))
    Story.append(Spacer(1, 0.08*inch))
    
    Story.append(Paragraph('<b>2. CHARACTER CREATION:</b>', body_style))
    Story.append(Paragraph('a) Select <b>RACE: Caldari</b>', body_style))
    Story.append(Paragraph(f'b) Name: <b>{toon_name}</b> (Replace #### with your own 4 random digits)', body_style))
    Story.append(Spacer(1, 0.08*inch))
    
    Story.append(Paragraph('<b>3. JOIN CORP:</b>', body_style))
    Story.append(Paragraph(corp_name, body_style))
    Story.append(Paragraph('(Apply to corp and ping in Alpha Force Discord channel)', secondary_style))
    Story.append(Spacer(1, 0.08*inch))
    
    Story.append(Paragraph('<b>4. ONCE IN CORP:</b>', body_style))
    Story.append(Paragraph("Go to 'Fittings' tab - use corp doctrine fits", body_style))
    Story.append(Paragraph("Go to 'Skill Plans' - apply corp skill plan", body_style))
    Story.append(Paragraph('Apply skill points', body_style))
    Story.append(Spacer(1, 0.08*inch))
    
    Story.append(Paragraph('<b>5. GET TO JITA 4-4 AND AWAIT ORDERS IN ALPHA FORCE CHANNEL YOU HAVE BEEN ADDED TO</b>', body_style))
    
    doc.build(Story, onFirstPage=draw_tactical_background, onLaterPages=draw_tactical_background)
    
    return pdf_file

def deploy_alpha_force():
    """Main deployment function"""
    print("=" * 50)
    print("ALPHA FORCE DEPLOYMENT SYSTEM")
    print("=" * 50)
    print()
    
    # Get next Alpha Force number
    af_number = get_next_alpha_force_number()
    print(f">>> Deploying Alpha Force {af_number}...")
    print()
    
    # Generate toon name
    toon_name = generate_toon_name()
    print(f"[User] Toon Name: {toon_name}")
    print()
    
    # Find available corp name
    print("[Search] Searching for available corp name on EveWho...")
    corp_name = find_available_corp_name()
    print()
    
    # Create PDF
    print("[Doc] Generating deployment PDF...")
    pdf_file = create_deployment_pdf(af_number, toon_name, corp_name)
    print("[OK] PDF created: " + pdf_file)
    print()
    
    # Store in database
    db = load_db()
    record = {
        "alpha_force_number": af_number,
        "toon_name": toon_name,
        "corp_name": corp_name,
        "pdf_filename": pdf_file,
        "deployed_date": datetime.now().isoformat(),
        "status": "deployed"
    }
    db["alpha_forces"].append(record)
    save_db(db)
    
    print("[DB] Record stored in database")
    print()
    print("=" * 50)
    print("[OK] ALPHA FORCE " + str(af_number) + " DEPLOYED SUCCESSFULLY")
    print("=" * 50)
    print()
    print(f"Toon: {toon_name}")
    print(f"Corp: {corp_name}")
    print(f"PDF: {pdf_file}")
    
    return pdf_file

if __name__ == "__main__":
    deploy_alpha_force()
