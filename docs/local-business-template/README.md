# Local Business Website Template

## How to Customize

### 1. Replace Placeholders

Search and replace these in index.html:

| Placeholder | Replace With |
|-------------|-------------|
| `[Business]` | Your business name (e.g., "Whitco") |
| `[Service]` | Your main service (e.g., "Roofing", "HVAC") |
| `[Service Type]` | Service category (e.g., "roofing", "heating & cooling") |
| `[City]` | Your city (e.g., "Warner Robins") |
| `[X]` | Years in business / number of projects |
| `(478) 000-0000` | Your phone number |
| `YOUR_FORM_ID` | Your Formspree ID |

### 2. Update Services Section

Edit the services-grid div to match your actual services:

```html
<div class="service-card">
    <div class="service-icon">🏠</div>
    <h3>Your Service</h3>
    <p>Description of this service.</p>
</div>
```

### 3. Add Your Images

Replace `[Your Company Photo Here]` with:
```html
<img src="your-image.jpg" alt="Our team" style="width:100%;height:100%;object-fit:cover;border-radius:20px;">
```

### 4. Update Service Areas

Edit the areas-grid div to list your actual service cities.

### 5. Add Real Testimonials

Replace the testimonial placeholders with actual customer reviews.

### 6. Form Setup

1. Go to https://formspree.io
2. Create free account
3. Create a form
4. Replace `YOUR_FORM_ID` in the form action URL

---

## Quick Start Checklist

- [ ] Business name
- [ ] Phone number
- [ ] Service type
- [ ] City/area
- [ ] Years experience
- [ ] Services offered
- [ ] Service areas
- [ ] Testimonials
- [ ] Formspree ID
- [ ] Your photo/images

---

## Files

| File | Purpose |
|------|---------|
| `index.html` | Main template |
| `README.md` | This file |

---

## Deploy Options

### Option 1: WordPress
Upload HTML or use as design reference

### Option 2: Netlify/Vercel
Drag and drop the folder

### Option 3: GitHub Pages
Free hosting with custom domain
