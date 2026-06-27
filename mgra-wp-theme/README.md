# MGRA WordPress Theme

**Middle Georgia Radio Association (WR4MG)** — Custom WordPress Theme

Reproduces the original [wr4mg.us](https://wr4mg.us/) site with modern WordPress-compatible markup, responsive design, and a dues payment page with Venmo integration.

---

## 📁 Files

| File | Purpose |
|------|---------|
| `style.css` | Theme stylesheet + WordPress theme header |
| `index.php` | Homepage template (all sections) |
| `header.php` | Site header / navigation |
| `footer.php` | Site footer / scripts |
| `functions.php` | Theme functions, custom post types, REST API, admin settings |
| `page-dues.php` | Dues payment page with Venmo buttons |
| `index-preview.html` | Standalone preview of homepage (no WordPress needed) |
| `page-dues.html` | Standalone preview of dues page (no WordPress needed) |

---

## 🚀 WordPress Installation

1. **Download** this folder (`mgra-wp-theme`)
2. **Upload** to `/wp-content/themes/mgra-wp-theme/`
3. **Activate** in WordPress Admin → Appearance → Themes
4. **Create pages:**
   - Create a page called "Home" → set as **Front Page** (Settings → Reading)
   - Create a page called "Dues" → set **Template** to "Dues Page"
5. **Configure** in Settings → MGRA Settings:
   - Treasurer email
   - Venmo username
   - Dues amounts (default: $25 / $40 / $15)
6. **Add menu** in Appearance → Menus:
   - Assign to "Primary Menu" and "Footer Menu"

---

## 💰 Venmo Integration

The dues page uses Venmo's web payment URL scheme:

```
https://venmo.com/USERNAME?txn=pay&amount=AMOUNT&note=NOTE
```

Users click the Venmo button → taken to Venmo app/website → pay → treasurer gets notification.

**To set up:**
1. Create a Venmo business or personal account for WR4MG
2. Set the username in MGRA Settings
3. Test the links before going live

**Alternative payments** also shown: Cash, Check, PayPal

---

## 📝 Features

- ✅ Mobile responsive
- ✅ Smooth scroll navigation
- ✅ Modern CSS (Grid, Flexbox, Custom Properties)
- ✅ Accessible color contrast
- ✅ Print-friendly styles
- ✅ SEO-friendly markup
- ✅ WordPress REST API endpoint for dues submissions
- ✅ Admin settings page for treasurer config
- ✅ Custom post type for dues records

---

## 🎨 Preview (No WordPress needed)

Open `index-preview.html` in any browser to see the homepage.
Open `page-dues.html` to see the dues payment page.

---

## 📧 Contact

Questions? Contact Layered Media LLC or email `getmorehams@wr4mg.us`
