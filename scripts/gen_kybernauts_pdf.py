import fitz  # PyMuPDF
import os

# Kybernauts colors
VOID_BLACK = (13/255, 2/255, 8/255)
DARK_PURPLE = (26/255, 10/255, 46/255)
TEAL = (0/255, 212/255, 170/255)
LIGHT_GRAY = (200/255, 200/255, 220/255)
MED_GRAY = (180/255, 180/255, 200/255)
DIM_GRAY = (100/255, 100/255, 120/255)
WHITE = (1, 1, 1)

def add_header(page, rect):
    """Draw header bar with title and subtitle."""
    header_h = 50
    header_rect = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y0 + header_h)
    page.draw_rect(header_rect, color=VOID_BLACK, fill=VOID_BLACK)
    
    # Title
    page.insert_text(
        (rect.x0 + 20, rect.y0 + 25),
        "KYBERNAUTS CLADE",
        fontsize=22,
        fontname="Helvetica-Bold",
        color=TEAL
    )
    # Subtitle
    page.insert_text(
        (rect.x0 + 20, rect.y0 + 40),
        "OmniTorpid Vedmak Modular Fits  |  Pochven Operations",
        fontsize=11,
        fontname="Helvetica",
        color=MED_GRAY
    )
    # Teal line
    line_y = rect.y0 + header_h - 2
    page.draw_line(
        (rect.x0 + 20, line_y),
        (rect.x1 - 20, line_y),
        color=TEAL,
        width=2
    )
    return header_h

def add_footer(page, rect, page_num):
    """Draw footer bar."""
    footer_h = 25
    footer_y = rect.y1 - footer_h
    footer_rect = fitz.Rect(rect.x0, footer_y, rect.x1, rect.y1)
    page.draw_rect(footer_rect, color=VOID_BLACK, fill=VOID_BLACK)
    
    page.insert_text(
        (rect.x0 + 20, footer_y + 15),
        "join.kybernauts.today  |  Clade Is All",
        fontsize=9,
        fontname="Helvetica",
        color=DIM_GRAY
    )
    # Right-aligned page number - calculate position
    page_text = f"Page {page_num}"
    page.insert_text(
        (rect.x1 - 20 - (len(page_text) * 5), footer_y + 15),
        page_text,
        fontsize=9,
        fontname="Helvetica",
        color=DIM_GRAY
    )

def draw_section_title(page, x, y, title, max_w):
    """Draw a teal section title with underline."""
    page.insert_text(
        (x, y),
        title,
        fontsize=16,
        fontname="Helvetica-Bold",
        color=TEAL
    )
    line_y = y + 4
    page.draw_line((x, line_y), (x + max_w - 40, line_y), color=TEAL, width=1)
    return y + 18

def draw_subsection_title(page, x, y, title):
    """Draw a white subsection title."""
    page.insert_text(
        (x, y),
        title,
        fontsize=13,
        fontname="Helvetica-Bold",
        color=WHITE
    )
    return y + 16

def draw_body_text(page, x, y, text, max_w):
    """Draw wrapped body text."""
    text_rect = fitz.Rect(x, y, x + max_w, y + 200)
    result = page.insert_textbox(
        text_rect,
        text,
        fontsize=10,
        fontname="Helvetica",
        color=LIGHT_GRAY,
        align=fitz.TEXT_ALIGN_LEFT
    )
    # estimate height used
    lines = text.count('\n') + 1
    return y + lines * 12 + 4

def draw_bullet(page, x, y, text, max_w):
    """Draw a bullet point."""
    page.insert_text((x, y), chr(0x2022), fontsize=10, fontname="Helvetica", color=TEAL)
    text_rect = fitz.Rect(x + 12, y - 10, x + max_w, y + 50)
    page.insert_textbox(
        text_rect,
        text,
        fontsize=10,
        fontname="Helvetica",
        color=LIGHT_GRAY,
        align=fitz.TEXT_ALIGN_LEFT
    )
    # rough height
    words = len(text.split())
    lines = max(1, (words * 6) // max_w + 1)
    return y + 14

def draw_fit_block(page, x, y, text, max_w):
    """Draw fit text in a dark purple box."""
    lines = text.strip().split('\n')
    line_h = 11
    box_h = len(lines) * line_h + 16
    
    box_rect = fitz.Rect(x, y, x + max_w, y + box_h)
    page.draw_rect(box_rect, color=TEAL, fill=DARK_PURPLE, width=1)
    
    ty = y + 12
    for line in lines:
        page.insert_text(
            (x + 8, ty),
            line,
            fontsize=8,
            fontname="Courier",
            color=LIGHT_GRAY
        )
        ty += line_h
    
    return y + box_h + 10

# ---- BUILD PDF ----
doc = fitz.open()
margin = 20
content_w = 595 - 2 * margin  # A4 width

# Helper to make a new page with header/footer
class PageBuilder:
    def __init__(self, doc):
        self.doc = doc
        self.page_num = 0
        self.page = None
        self.rect = None
        self.y = 0
        self.content_bottom = 0
        self._new_page()
    
    def _new_page(self):
        self.page = self.doc.new_page(width=595, height=842)
        self.rect = self.page.rect
        self.page_num += 1
        header_h = add_header(self.page, self.rect)
        add_footer(self.page, self.rect, self.page_num)
        self.y = header_h + 15
        self.content_bottom = self.rect.y1 - 35
    
    def check_space(self, needed):
        if self.y + needed > self.content_bottom:
            self._new_page()
    
    def section(self, title):
        self.check_space(30)
        self.y = draw_section_title(self.page, margin, self.y, title, content_w)
    
    def subsection(self, title):
        self.check_space(20)
        self.y = draw_subsection_title(self.page, margin, self.y, title)
    
    def text(self, txt):
        self.check_space(60)
        self.y = draw_body_text(self.page, margin, self.y, txt, content_w)
    
    def bullet(self, txt):
        self.check_space(20)
        self.y = draw_bullet(self.page, margin + 5, self.y, txt, content_w - 10)
    
    def fit(self, txt):
        lines = txt.strip().split('\n')
        needed = len(lines) * 11 + 20
        self.check_space(needed)
        self.y = draw_fit_block(self.page, margin, self.y, txt, content_w)

pb = PageBuilder(doc)

# ===== PAGE 1: OVERVIEW + BASE =====
pb.section("OVERVIEW")
pb.text(
    "The Vedmak is the cornerstone Triglavian cruiser - a versatile platform that excels in "
    "both PvE site-running and small-gang PvP within Pochven. The OmniTorpid modular fit "
    "system provides maximum flexibility: a single OmniTorpid.Base hull can be reconfigured "
    "on-demand into any specialized variant."
)

pb.subsection("How Modularity Works")
pb.text(
    "OmniTorpid.Base contains every module needed for all variants in its cargohold. "
    "Strip to hull (keep rigs), then import any variant fit via 'Fit To Active Ship'. "
    "Want to switch from PvE to PvP? Strip and re-import. All variants can also be "
    "purchased directly if you prefer dedicated hulls."
)

pb.section("OMNITORPID.BASE")
pb.text(
    "The foundational fit. Purchase this hull and import once. All variant modules live "
    "in cargo. Includes extra meta modules for lower skill levels or performance tweaks."
)

pb.subsection("Usage")
pb.bullet("Purchase Vedmak and import OmniTorpid.Base (or Buy All + Multifit)")
pb.bullet("Strip fitting while keeping rigs intact; ensure drone bay and cargo are empty")
pb.bullet("Import desired variant via 'Fit To Active Ship'")

pb.subsection("Fit")
pb.fit("""[Vedmak, OmniTorpid.Base]
Damage Control II
Entropic Radiation Sink II
Multispectrum Energized Membrane II
Corelum C-Type Thermal Energized Membrane
Corelum C-Type Kinetic Energized Membrane
True Sansha Explosive Energized Membrane
Medium Remote Armor Repairer II
Medium Remote Armor Repairer II

Heavy Entropic Disintegrator II

Medium Remote Repair Augmentor I
Medium Remote Repair Augmentor I
Medium EM Armor Reinforcer II

Warrior II x5
Medium Armor Maintenance Bot I x5
Navy Cap Booster 400 x15
Tetryon Exotic Plasma M x3000
Baryon Exotic Plasma M x3000
Meson Exotic Plasma M x3000
Occult M x5000
Mystic M x5000

[In cargo: all variant modules - see next pages]""")

# ===== PAGE 2: PvE =====
pb.section("OMNITORPID.PVE")
pb.text(
    "Remote-rep focused for small-gang Torpid site running. Maximum survivability with "
    "strong capacitor stability. All Vedmaks form a repair chain - everyone reps everyone."
)

pb.subsection("Usage Notes")
pb.bullet("Pre-undock: Form repair chain. Watchlist all Vedmaks. Color-code buddy.")
pb.bullet("Site arrival: Lock targets; apply all remote reps to buddy + launch armor repair drones")
pb.bullet("Position behind sleeper array (max distance from warp-in)")
pb.bullet("Kill smallest NPCs first; spread fire. AB cap-stable for damage mitigation.")
pb.bullet("If cap tight: use only 2 of 3 repairers when repairs not critical")
pb.bullet("Wave 3 finish: prioritize unseen BS for max standing payout")

pb.subsection("Fit")
pb.fit("""[Vedmak, OmniTorpid.PvE]
Damage Control II
Entropic Radiation Sink II
Multispectrum Energized Membrane II
Corelum C-Type Thermal Energized Membrane
Corelum C-Type Kinetic Energized Membrane
True Sansha Explosive Energized Membrane
Cap Recharger II
10MN Monopropellant Enduring Afterburner

Medium Cap Battery II
Medium Cap Battery II
Medium Remote Armor Repairer II
Medium Remote Armor Repairer II
Heavy Entropic Disintegrator II
Medium Remote Armor Repairer II

Medium Remote Repair Augmentor I
Medium Remote Repair Augmentor I
Medium EM Armor Reinforcer II

Warrior II x5
Medium Armor Maintenance Bot I x5
Baryon Exotic Plasma M x3000
Meson Exotic Plasma M x3000
Occult M x5000
Mystic M x5000
Tetryon Exotic Plasma M x3000

Cladistic-5 'Krai Veles' Filament x5
Glorification-1 'Devana' Filament x10
Glorification-5 'Devana' Filament x15
Cladistic-5 'Krai Svarog' Filament x5
Cladistic-5 'Krai Perun' Filament x5""")

# ===== PAGE 3: INCIPIENT =====
pb.section("OMNITORPID.INCIPIENT.PVE")
pb.text(
    "Smartbomb-equipped for Incipient Drone Swarms. Trades one battery for drone-clearing "
    "smartbomb capability while keeping strong remote-rep support."
)

pb.subsection("Usage Notes")
pb.bullet("Tight anchor on regroup. Engage smartbombs immediately as first drone wave lands.")
pb.bullet("Afterburn toward BS spawn; disengage smartbombs on spawn, apply disintegrators.")
pb.bullet("Repair chain as normal (no logistics drones). Pre-lock and dynamically shift repairs.")
pb.bullet("Maximize movement with AB - more cap stable while pre-locking gang.")

pb.subsection("Fit")
pb.fit("""[Vedmak, OmniTorpid.Incip.PvE]
Damage Control II
Entropic Radiation Sink II
Multispectrum Energized Membrane II
Corelum C-Type Thermal Energized Membrane
Corelum C-Type Kinetic Energized Membrane
True Sansha Explosive Energized Membrane
Cap Recharger II
10MN Monopropellant Enduring Afterburner

Medium Cap Battery II
Medium Compact Pb-Acid Cap Battery
Medium Remote Armor Repairer II
Medium Remote Armor Repairer II
Heavy Entropic Disintegrator II
'YF-12a' Compact Medium Plasma Smartbomb

Medium Remote Repair Augmentor I
Medium Remote Repair Augmentor I
Medium EM Armor Reinforcer II

Warrior II x5
Medium Armor Maintenance Bot I x5
Baryon Exotic Plasma M x3000
Meson Exotic Plasma M x3000
Occult M x5000
Mystic M x5000
Tetryon Exotic Plasma M x3000

Cladistic-5 'Krai Veles' Filament x5
Glorification-1 'Devana' Filament x10
Cladistic-5 'Krai Svarog' Filament x5
Glorification-5 'Devana' Filament x15
Cladistic-5 'Krai Perun' Filament x5""")

# ===== PAGE 4: PvP =====
pb.section("OMNITORPID.PVP")
pb.text(
    "Cap-boosted PvP using cap boosters, energy neutralizer, and max Tech 2 modules. "
    "Optimized for Chinese Finger Torpid Trap setups and general PvP engagements. "
    "Contains 1 of each T2 PvP module in cargo - fit choice on initial load."
)

pb.subsection("Chinese Finger Torpid Trap")
pb.bullet("Cloaked PvP Rodiva on beacon decloaks and engages target")
pb.bullet("Cloaked Blackbird / Falcon / Rook decloaks for ramping Mutadaptive reps")
pb.bullet("Vedmaks converge on Rodiva for repairs + focused damage")

pb.subsection("Fit")
pb.fit("""[Vedmak, OmniTorpid.PvP]
Damage Control II
Entropic Radiation Sink II
Multispectrum Energized Membrane II
Corelum C-Type Thermal Energized Membrane
Corelum C-Type Kinetic Energized Membrane
True Sansha Explosive Energized Membrane
[Empty Med slot]
10MN Afterburner II

Small Capacitor Booster II
Medium Cap Battery II
Medium Remote Armor Repairer II
Medium Remote Armor Repairer II
Heavy Entropic Disintegrator II
Medium Energy Neutralizer II

Medium Remote Repair Augmentor I
Medium Remote Repair Augmentor I
Medium EM Armor Reinforcer II

Warrior II x5
Medium Armor Maintenance Bot I x5
Navy Cap Booster 400 x27
Tetryon Exotic Plasma M x3000
Baryon Exotic Plasma M x3000
Meson Exotic Plasma M x3000
Occult M x5000
Mystic M x5000

[In cargo:]
Warp Scrambler II x1
Warp Disruptor II x1
Stasis Webifier II x1
Cladistic-5 'Krai Veles' Filament x5
Glorification-1 'Devana' Filament x10
Cladistic-5 'Krai Svarog' Filament x5
Glorification-5 'Devana' Filament x15
Cladistic-5 'Krai Perun' Filament x5""")

pb.text(
    "More fits (Chinese Finger Torpid Trap variants, Drekavac fits) coming soon. "
    "Feedback appreciated via Kybernauts channels."
)

# Save
out_dir = r'C:\Users\compj\.openclaw\workspace\media\kybernauts'
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'OmniTorpid_Vedmak_Fits_Kybernauts.pdf')
doc.save(out_path)
doc.close()
print(f"PDF created: {out_path}")
