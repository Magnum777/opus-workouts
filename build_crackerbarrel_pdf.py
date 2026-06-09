from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
from reportlab.lib import colors
import os

# Data from crackerbarrelmenuwithprices.com (June 2026)
# Lunch & Dinner Buffet Style Meals (serves 10)
BUFFET_MEALS = [
    {
        "name": "Country Fried Shrimp",
        "description": "Buttermilk breaded fried shrimp served with hushpuppies plus choice of 2 or 3 sides and choice of bread.",
        "price_2sides": "$134.99",
        "price_3sides": "$149.99",
        "calories": "8,550 cal (860/serving)",
        "image": None
    },
    {
        "name": "Pot Roast",
        "description": "Slow-braised rib roast, carrots, onions, and celery in a savory, homestyle gravy. Comes with choice of 2 or 3 sides and choice of bread.",
        "price_2sides": "$154.99",
        "price_3sides": "$169.99",
        "calories": "5,200 cal (520/serving)",
        "image": None
    },
    {
        "name": "Crispy Tender Dippers",
        "description": "Hand-breaded tenders with your choice of 3 sauces for dipping. Served with choice of 2 or 3 sides and choice of bread.",
        "price_2sides": "$107.99",
        "price_3sides": "$125.99",
        "calories": "4,010 cal (400/serving)",
        "image": "crackerbarrel_images/tenders.jpg"
    },
    {
        "name": "Sirloin Steak Tips",
        "description": "A hearty portion of Steak Tips with buttery garlic sauce. Comes with choice of 2 or 3 sides and choice of bread.",
        "price_2sides": "$127.99",
        "price_3sides": "$142.99",
        "calories": "3,010 cal (300/serving)",
        "image": None
    },
    {
        "name": "Homestyle Chicken n' French Toast",
        "description": "Homestyle Chicken with special-recipe French Toast. Served with your choice of breakfast sides.",
        "price_2sides": "$108.99",
        "price_3sides": "$123.99",
        "calories": "10,500 cal (1,050/serving)",
        "image": None
    },
    {
        "name": "Southern Fried Chicken Meal",
        "description": "Bone-in chicken hand-breaded using our special recipe seasoning, fried 'til golden and crispy. Served with choice of 2 or 3 sides and bread.",
        "price_2sides": "$119.99",
        "price_3sides": "$134.99",
        "calories": "8,220 cal (820/serving)",
        "image": None
    },
    {
        "name": "Homestyle Chicken Meal",
        "description": "Boneless chicken breasts hand-dipped in our special buttermilk batter, breaded and deep fried. Served with choice of 2 or 3 sides and bread.",
        "price_2sides": "$119.99",
        "price_3sides": "$134.99",
        "calories": "5,310 cal (530/serving)",
        "image": None
    },
    {
        "name": "U.S. Farm-Raised Fried Catfish",
        "description": "U.S. farm-raised fillets hand breaded with cornmeal breading and fried. Served with hushpuppies, tartar sauce, choice of 2 or 3 sides and bread.",
        "price_2sides": "$121.99",
        "price_3sides": "$136.99",
        "calories": "5,410 cal (540/serving)",
        "image": None
    },
    {
        "name": "Chicken Pot Pie",
        "description": "Creamy chicken pot pie with a flaky top crust. Sides not included with this catering entree.",
        "price_2sides": "$39.99",
        "price_3sides": "$39.99",
        "calories": "6,800 cal (680/serving)",
        "image": None
    },
    {
        "name": "Grilled Chicken Tenders",
        "description": "Seasoned and grilled chicken tenders. Served with choice of 2 or 3 sides and bread.",
        "price_2sides": "$58.99",
        "price_3sides": "$73.99",
        "calories": "2,400 cal (240/serving)",
        "image": None
    },
    {
        "name": "Fried Chicken Tenders",
        "description": "Hand-breaded fried chicken tenders. Served with choice of 2 or 3 sides and bread. Plus two dipping sauces: BBQ, Honey Mustard, or Ranch.",
        "price_2sides": "$58.99",
        "price_3sides": "$73.99",
        "calories": "5,800 cal (580/serving)",
        "image": None
    },
    {
        "name": "Chicken n' Dumplins",
        "description": "Made-from-scratch dumplins slow simmered in our rich chicken stock. Served with choice of 2 or 3 sides and bread.",
        "price_2sides": "$56.99",
        "price_3sides": "$71.99",
        "calories": "3,000 cal (300/serving)",
        "image": None
    },
    {
        "name": "Meatloaf",
        "description": "Classic meatloaf with a savory tomato glaze. Served with choice of 2 or 3 sides and bread.",
        "price_2sides": "$58.29",
        "price_3sides": "$73.29",
        "calories": "5,200 cal (520/serving)",
        "image": None
    },
    {
        "name": "Roast Beef",
        "description": "Slow-roasted beef with rich brown gravy. Served with choice of 2 or 3 sides and bread.",
        "price_2sides": "$74.99",
        "price_3sides": "$89.99",
        "calories": "4,800 cal (480/serving)",
        "image": None
    },
    {
        "name": "Chicken Fried Chicken",
        "description": "Crispy fried chicken with Sawmill Gravy. Served with choice of 2 or 3 sides and bread.",
        "price_2sides": "$62.99",
        "price_3sides": "$77.99",
        "calories": "5,300 cal (530/serving)",
        "image": None
    },
    {
        "name": "Sunday Homestyle Chicken",
        "description": "Our signature Sunday chicken, available every day. Hand-breaded and fried to golden perfection. Served with choice of 2 or 3 sides and bread.",
        "price_2sides": "$59.99",
        "price_3sides": "$74.99",
        "calories": "5,300 cal (530/serving)",
        "image": None
    },
    {
        "name": "Smoky Southern Grilled Chicken Breasts",
        "description": "Grilled chicken breasts with broccoli. Served with choice of 2 or 3 sides and bread.",
        "price_2sides": "$54.99",
        "price_3sides": "$69.99",
        "calories": "1,600 cal (160/serving)",
        "image": None
    },
    {
        "name": "Country Fried Steak",
        "description": "Country fried steak with Sawmill Gravy. Served with choice of 2 or 3 sides and bread.",
        "price_2sides": "$64.99",
        "price_3sides": "$79.99",
        "calories": "5,200 cal (520/serving)",
        "image": None
    },
    {
        "name": "Smothered Hamburger Steak",
        "description": "Hamburger steak smothered in onions and gravy. Served with choice of 2 or 3 sides and bread.",
        "price_2sides": "$58.29",
        "price_3sides": "$73.29",
        "calories": "5,100 cal (510/serving)",
        "image": None
    },
    {
        "name": "Sugar Ham",
        "description": "Sweet sugar-cured ham. Served with choice of 2 or 3 sides and bread.",
        "price_2sides": "$69.99",
        "price_3sides": "$84.99",
        "calories": "4,400 cal (440/serving)",
        "image": "crackerbarrel_images/ham.jpg"
    },
    {
        "name": "Country Ham",
        "description": "Hickory-smoked country ham. Served with choice of 2 or 3 sides and bread.",
        "price_2sides": "$69.99",
        "price_3sides": "$84.99",
        "calories": "2,700 cal (270/serving)",
        "image": None
    },
    {
        "name": "Fried Catfish",
        "description": "U.S. farm-raised catfish fillets hand-breaded with cornmeal breading and fried. Served with hushpuppies and tartar sauce. Choice of 2 or 3 sides and bread.",
        "price_2sides": "$59.29",
        "price_3sides": "$74.29",
        "calories": "2,500 cal (250/serving)",
        "image": None
    },
]

# Sides (one quart each, serves 6)
SIDES = [
    ("Whole Kernel Corn", "$32.99", "190 cal/serving"),
    ("Dumplins", "$32.99", "140 cal/serving"),
    ("Turnip Greens", "$32.99", "100 cal/serving"),
    ("Mixed Green Salad", "$32.99", "25 cal/serving"),
    ("Macaroni n' Cheese", "$32.99", "270 cal/serving"),
    ("Steamed Broccoli", "$32.99", "30 cal/serving"),
    ("Mashed Potatoes", "$32.99", "160 cal/serving"),
    ("Mashed Potatoes w/ Brown Gravy", "$32.99", "180 cal/serving"),
    ("Mashed Potatoes w/ Sawmill Gravy", "$32.99", "200 cal/serving"),
    ("Fried Apples", "$32.99", "170 cal/serving"),
    ("Hashbrown Casserole", "$32.99", "190 cal/serving"),
    ("Cole Slaw", "$32.99", "220 cal/serving"),
    ("Sweet Whole Baby Carrots", "$32.99", "80 cal/serving"),
    ("Pinto Beans", "$32.99", "180 cal/serving"),
    ("Country Green Beans", "$32.99", "70 cal/serving"),
    ("Sweet Potato Casserole*", "$32.99", "230 cal/serving"),
    ("Cornbread Dressing", "$32.99", "260 cal/serving"),
]

# Breads
BREADS = [
    ("Dozen Homemade Buttermilk Biscuits", "$5.99", "160 cal each"),
    ("Dozen Corn Muffins", "$5.99", "210 cal each"),
    ("Loaf of Sourdough Bread", "$5.49", "1,670 cal"),
]

# Party Platters
PLATTERS = [
    ("Crispy Tender Dippers Platter", "30 or 60 hand-breaded crispy chicken tender dippers with choice of 3 sauces for dipping.", "Custom"),
    ("Barrel Cheeseburger Slider Platter", "10 mini burgers topped with American cheese, served with ketchup, mayo, mustard, and pickle.", "$32.99"),
    ("Build Your Own Fried Saucy Chicken Sandwich Bar", "Fried chicken, lettuce, tomato, pickles, and 3 sauce choices.", "$90.99"),
    ("Build Your Own Grilled Saucy Chicken Sandwich Bar", "Grilled chicken, lettuce, tomato, pickles, and 3 sauce choices.", "$90.99"),
]

# Desserts
DESSERTS = [
    ("Double Chocolate Fudge Coca-Cola Cake (Serves 12)", "$24.99", "680 cal/serving"),
    ("Blackberry or Peach Fruit Cobbler (Serves 12)", "$17.99", "340-370 cal/serving"),
    ("Homestyle Chocolate Chip Cookies (12)", "$12.99", "240 cal each"),
    ("Family Size Coca-Cola Cake (Serves 6)", "$12.99", "680 cal/serving"),
    ("Family Size Fruit Cobbler (Serves 6)", "$11.99", "340-370 cal/serving"),
]

# Beverages
BEVERAGES = [
    ("Freshly Brewed Premium Coffee (96 oz)", "$15.99", "30 cal/container"),
    ("Freshly Brewed Decaf Coffee (96 oz)", "$15.99", "30 cal/container"),
    ("Florida Orange Juice (Half Gallon)", "$8.39", "1,530 cal"),
    ("Freshly Brewed Sweet Iced Tea (Half Gallon)", "$5.49", "520 cal"),
    ("Freshly Brewed Unsweetened Iced Tea (Half Gallon)", "$5.49", "0 cal"),
    ("Old-Fashioned Lemonade (Half Gallon)", "$6.29", "1,040 cal"),
]

def build_pdf():
    doc = SimpleDocTemplate(
        "crackerbarrel_catering_buffet.pdf",
        pagesize=letter,
        rightMargin=0.6*inch,
        leftMargin=0.6*inch,
        topMargin=0.6*inch,
        bottomMargin=0.6*inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c5f2d'),
        spaceAfter=6,
        alignment=TA_CENTER,
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c5f2d'),
        spaceBefore=12,
        spaceAfter=6,
        borderWidth=0,
        borderColor=colors.HexColor('#2c5f2d'),
        borderPadding=4,
        leftIndent=0,
    )

    item_name_style = ParagraphStyle(
        'ItemName',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#333333'),
        spaceAfter=2,
    )

    item_desc_style = ParagraphStyle(
        'ItemDesc',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#555555'),
        spaceAfter=2,
        leftIndent=8,
    )

    price_style = ParagraphStyle(
        'Price',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2c5f2d'),
        spaceAfter=2,
        leftIndent=8,
    )

    story = []

    # Title
    story.append(Paragraph("Cracker Barrel Catering", title_style))
    story.append(Paragraph("Lunch & Dinner — Buffet Style Options", title_style))
    story.append(Paragraph("Prices and menu items as of June 2026 | Serves 10 per meal unless noted", subtitle_style))
    story.append(Spacer(1, 0.1*inch))

    # --- BUFFET STYLE MEALS ---
    story.append(Paragraph("Buffet Style Meals (Serves 10)", heading_style))
    story.append(Paragraph("Each meal includes your choice of 2 or 3 sides and bread. Available starting at 11 AM.", subtitle_style))

    for item in BUFFET_MEALS:
        # Try to add image if available
        if item["image"] and os.path.exists(item["image"]):
            try:
                img = RLImage(item["image"], width=2.2*inch, height=1.47*inch)
                story.append(img)
            except Exception:
                pass

        story.append(Paragraph(item["name"], item_name_style))
        story.append(Paragraph(item["description"], item_desc_style))
        price_text = f"2 Sides: {item['price_2sides']}  |  3 Sides: {item['price_3sides']}  |  {item['calories']}"
        story.append(Paragraph(price_text, price_style))
        story.append(Spacer(1, 0.05*inch))

    story.append(PageBreak())

    # --- SIDES ---
    story.append(Paragraph("Country Sides (One Quart Each, Serves 6)", heading_style))
    story.append(Paragraph("Add these homestyle sides to any meal or order them a la carte.", subtitle_style))

    sides_data = [["Side", "Price", "Calories"]]
    for side in SIDES:
        sides_data.append([side[0], side[1], side[2]])

    sides_table = Table(sides_data, colWidths=[3.2*inch, 1.2*inch, 1.8*inch])
    sides_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5f2d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f8f8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sides_table)
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph("*Sweet Potato Casserole and Cornbread Dressing available Thursday only.", item_desc_style))

    # --- BREADS ---
    story.append(Paragraph("Breads", heading_style))
    bread_data = [["Bread", "Price", "Calories"]]
    for bread in BREADS:
        bread_data.append([bread[0], bread[1], bread[2]])

    bread_table = Table(bread_data, colWidths=[3.2*inch, 1.2*inch, 1.8*inch])
    bread_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5f2d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f8f8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(bread_table)
    story.append(Spacer(1, 0.15*inch))

    # --- PARTY PLATTERS ---
    story.append(Paragraph("Party Platters", heading_style))
    for platter in PLATTERS:
        story.append(Paragraph(platter[0], item_name_style))
        story.append(Paragraph(platter[1], item_desc_style))
        story.append(Paragraph(f"Price: {platter[2]}", price_style))
        story.append(Spacer(1, 0.05*inch))

    story.append(PageBreak())

    # --- DESSERTS ---
    story.append(Paragraph("Desserts", heading_style))
    dessert_data = [["Dessert", "Price", "Calories"]]
    for d in DESSERTS:
        dessert_data.append([d[0], d[1], d[2]])

    dessert_table = Table(dessert_data, colWidths=[3.6*inch, 1.0*inch, 1.6*inch])
    dessert_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5f2d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f8f8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(dessert_table)
    story.append(Spacer(1, 0.15*inch))

    # --- BEVERAGES ---
    story.append(Paragraph("Beverages", heading_style))
    bev_data = [["Beverage", "Price", "Calories"]]
    for b in BEVERAGES:
        bev_data.append([b[0], b[1], b[2]])

    bev_table = Table(bev_data, colWidths=[3.6*inch, 1.0*inch, 1.6*inch])
    bev_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5f2d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f8f8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(bev_table)
    story.append(Spacer(1, 0.15*inch))

    # Footer note
    story.append(Paragraph("—", subtitle_style))
    story.append(Paragraph("Prices and availability may vary by location. Visit CrackerBarrel.com to start your order.", subtitle_style))
    story.append(Paragraph("Source: crackerbarrelmenuwithprices.com (June 2026) | Official PDF: crackerbarrel.com/catering", subtitle_style))

    doc.build(story)
    print("PDF built successfully: crackerbarrel_catering_buffet.pdf")

if __name__ == '__main__':
    build_pdf()
