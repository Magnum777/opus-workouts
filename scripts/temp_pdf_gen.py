from fpdf import FPDF
import os

class KybernautsPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('DejaVu', '', r'C:\Users\compj\AppData\Roaming\Python\Python314\site-packages\fpdf\font\DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', r'C:\Users\compj\AppData\Roaming\Python\Python314\site-packages\fpdf\font\DejaVuSans-Bold.ttf', uni=True)
        self.add_font('DejaVu', 'I', r'C:\Users\compj\AppData\Roaming\Python\Python314\site-packages\fpdf\font\DejaVuSans-Oblique.ttf', uni=True)
        self.add_font('DejaVuMono', '', r'C:\Users\compj\AppData\Roaming\Python\Python314\site-packages\fpdf\font\DejaVuSansMono.ttf', uni=True)
    
    def header(self):
        self.set_fill_color(13, 2, 8)
        self.rect(0, 0, self.w, 35, 'F')
        self.set_xy(15, 10)
        self.set_font('DejaVu', 'B', 22)
        self.set_text_color(0, 212, 170)
        self.cell(0, 12, 'KYBERNAUTS CLADE', new_x='RIGHT', new_y='TOP')
        self.set_xy(15, 22)
        self.set_font('DejaVu', '', 11)
        self.set_text_color(180, 180, 200)
        self.cell(0, 8, 'OmniTorpid Vedmak Modular Fits  |  Pochven Operations', new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(0, 212, 170)
        self.set_line_width(0.8)
        self.line(15, 34, self.w - 15, 34)
        self.ln(12)
    
    def footer(self):
        self.set_y(-20)
        self.set_fill_color(13, 2, 8)
        self.rect(0, self.h - 20, self.w, 20, 'F')
        self.set_font('DejaVu', '', 9)
        self.set_text_color(100, 100, 120)
        self.set_xy(15, -12)
        self.cell(0, 10, 'join.kybernauts.today  |  Clade Is All', align='L')
        self.set_xy(-15, -12)
        self.cell(0, 10, f'Page {self.page_no()}', align='R')
    
    def section_title(self, title):
        self.set_font('DejaVu', 'B', 16)
        self.set_text_color(0, 212, 170)
        self.cell(0, 10, title, new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(0, 212, 170)
        self.set_line_width(0.4)
        self.line(15, self.get_y(), self.w - 15, self.get_y())
        self.ln(4)
    
    def subsection_title(self, title):
        self.set_font('DejaVu', 'B', 13)
        self.set_text_color(220, 220, 240)
        self.cell(0, 8, title, new_x='LMARGIN', new_y='NEXT')
        self.ln(1)
    
    def body_text(self, text):
        self.set_font('DejaVu', '', 10)
        self.set_text_color(200, 200, 220)
        self.multi_cell(0, 5.5, text)
        self.ln(2)
    
    def fit_block(self, text):
        self.set_fill_color(26, 10, 46)
        self.set_draw_color(0, 212, 170)
        self.set_line_width(0.3)
        lines = text.strip().split('\n')
        line_count = len(lines)
        box_h = line_count * 4.5 + 8
        start_y = self.get_y()
        self.rect(15, start_y, self.w - 30, box_h, 'FD')
        self.set_xy(18, start_y + 3)
        self.set_font('DejaVuMono', '', 8)
        self.set_text_color(200, 200, 220)
        for line in lines:
            self.cell(0, 4.5, line, new_x='LMARGIN', new_y='NEXT')
            self.set_x(18)
        self.set_y(start_y + box_h + 4)
    
    def bullet_text(self, text):
        self.set_font('DejaVu', '', 10)
        self.set_text_color(200, 200, 220)
        self.set_x(20)
        self.cell(5, 5.5, chr(149), new_x='RIGHT', new_y='TOP')
        self.multi_cell(0, 5.5, text)
        self.ln(1)

# Create PDF
pdf = KybernautsPDF()
pdf.set_auto_page_break(auto=True, margin=25)
pdf.add_page()

# Overview
pdf.section_title('OVERVIEW')
overview = (
    'The Vedmak is the cornerstone Triglavian cruiser - a versatile platform that '
    'excels in both PvE site-running and small-gang PvP within Pochven. '
    'The OmniTorpid modular fit system provides maximum flexibility: a single '
    'OmniTorpid.Base hull can be reconfigured on-demand into any specialized variant.'
)
pdf.body_text(overview)

pdf.subsection_title('How Modularity Works')
mod = (
    'OmniTorpid.Base contains every module needed for all variants in its cargohold. '
    'Strip to hull (keep rigs), then import any variant fit via "Fit To Active Ship". '
    'Want to switch from PvE to PvP? Strip and re-import. All variants can also be '
    'purchased directly if you prefer dedicated hulls.'
)
pdf.body_text(mod)

pdf.ln(3)

# --- BASE FIT ---
pdf.section_title('OMNITORPID.BASE')
base_desc = (
    'The foundational fit. Purchase this hull and import once. '
    'All variant modules live in cargo. Includes extra meta modules '
    'for lower skill levels or performance tweaks.'
)
pdf.body_text(base_desc)

pdf.subsection_title('Usage')
pdf.bullet_text('Purchase Vedmak and import OmniTorpid.Base (or Buy All + Multifit)')
pdf.bullet_text('Strip fitting while keeping rigs intact; ensure drone bay and cargo are empty')
pdf.bullet_text('Import desired variant via "Fit To Active Ship"')
pdf.ln(2)

pdf.subsection_title('Fit')
base_fit = """[Vedmak, OmniTorpid.Base]
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

[In cargo: all variant modules - see page 2]"""
pdf.fit_block(base_fit)

# Page break for more fits
pdf.add_page()

# --- PvE FIT ---
pdf.section_title('OMNITORPID.PVE')
pve_desc = (
    'Remote-rep focused for small-gang Torpid site running. '
    'Maximum survivability with strong capacitor stability. '
    'All Vedmaks form a repair chain - everyone reps everyone.'
)
pdf.body_text(pve_desc)

pdf.subsection_title('Usage Notes')
pdf.bullet_text('Pre-undock: Form repair chain. Watchlist all Vedmaks. Color-code buddy.')
pdf.bullet_text('Site arrival: Lock targets; apply all remote reps to buddy + launch armor repair drones')
pdf.bullet_text('Position behind sleeper array (max distance from warp-in)')
pdf.bullet_text('Kill smallest NPCs first; spread fire. AB cap-stable for damage mitigation.')
pdf.bullet_text('If cap tight: use only 2 of 3 repairers when repairs not critical')
pdf.bullet_text('Wave 3 finish: prioritize unseen BS for max standing payout')
pdf.ln(2)

pdf.subsection_title('Fit')
pve_fit = """[Vedmak, OmniTorpid.PvE]
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
Cladistic-5 'Krai Perun' Filament x5"""
pdf.fit_block(pve_fit)

pdf.add_page()

# --- INCIPIENT PvE ---
pdf.section_title('OMNITORPID.INCIPIENT.PVE')
incip_desc = (
    'Smartbomb-equipped for Incipient Drone Swarms. '
    'Trades one battery for drone-clearing smartbomb capability '
    'while keeping strong remote-rep support.'
)
pdf.body_text(incip_desc)

pdf.subsection_title('Usage Notes')
pdf.bullet_text('Tight anchor on regroup. Engage smartbombs immediately as first drone wave lands.')
pdf.bullet_text('Afterburn toward BS spawn; disengage smartbombs on spawn, apply disintegrators.')
pdf.bullet_text('Repair chain as normal (no logistics drones). Pre-lock and dynamically shift repairs.')
pdf.bullet_text('Maximize movement with AB - more cap stable while pre-locking gang.')
pdf.ln(2)

pdf.subsection_title('Fit')
incip_fit = """[Vedmak, OmniTorpid.Incip.PvE]
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
Cladistic-5 'Krai Perun' Filament x5"""
pdf.fit_block(incip_fit)

pdf.add_page()

# --- PvP FIT ---
pdf.section_title('OMNITORPID.PVP')
pvp_desc = (
    'Cap-boosted PvP using cap boosters, energy neutralizer, and max Tech 2 modules. '
    'Optimized for Chinese Finger Torpid Trap setups and general PvP engagements. '
    'Contains 1 of each T2 PvP module in cargo - fit choice on initial load.'
)
pdf.body_text(pvp_desc)

pdf.subsection_title('Chinese Finger Torpid Trap')
pdf.bullet_text('Cloaked PvP Rodiva on beacon decloaks and engages target')
pdf.bullet_text('Cloaked Blackbird / Falcon / Rook decloaks for ramping Mutadaptive reps')
pdf.bullet_text('Vedmaks converge on Rodiva for repairs + focused damage')
pdf.ln(2)

pdf.subsection_title('Fit')
pvp_fit = """[Vedmak, OmniTorpid.PvP]
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
Cladistic-5 'Krai Perun' Filament x5"""
pdf.fit_block(pvp_fit)

pdf.ln(4)

pdf.set_font('DejaVu', 'I', 10)
pdf.set_text_color(120, 120, 140)
pdf.multi_cell(0, 6, (
    'More fits (Chinese Finger Torpid Trap variants, Drekavac fits) coming soon. '
    'Feedback appreciated via Kybernauts channels.'
))

# Output
out_path = r'C:\Users\compj\.openclaw\workspace\media\kybernauts\OmniTorpid_Vedmak_Fits_Kybernauts.pdf'
os.makedirs(os.path.dirname(out_path), exist_ok=True)
pdf.output(out_path)
print(f"PDF created: {out_path}")
