# Sojourn Church — Guest WiFi Portal Content

## Landing Page Text

### Header
**Welcome to Sojourn Church**
*Guest WiFi Access*

### Body
Thank you for visiting Sojourn Church. Free WiFi access is provided as a courtesy for guests and visitors during church services and events.

By connecting to this network, you agree to the following terms:

**Acceptable Use**
- This network is for lawful purposes only
- Do not use for illegal downloads, streaming copyrighted content, or malicious activity
- Be respectful of bandwidth — others are also using this connection

**Privacy & Security**
- This is a public, unsecured network. Do not transmit sensitive information (banking, passwords) over this connection.
- The church does not monitor individual browsing activity, but reserves the right to block abusive usage.
- Use of this network is at your own risk.

**Time Limits**
- Guest access is limited to 12 hours per session
- Bandwidth is shared fairly among all users

**Support**
Having trouble connecting? Email: sojournchurchtech@gmail.com

### Checkbox
[ ] I have read and agree to the Terms of Use above.

### Button
**Connect to Internet**

---

## UniFi Guest Portal Settings (when configuring)

| Setting | Value |
|---------|-------|
| Authentication | Hotspot (Terms of Use) |
| Landing Page | External (use custom HTML if available, or UniFi built-in) |
| Session Timeout | 12 hours (720 minutes) |
| Bandwidth Limit (down) | 10 Mbps |
| Bandwidth Limit (up) | 5 Mbps |
| VLAN | 30 (sojourn-guest) |
| Password | None (open) |
| Encryption | None (open — portal handles acceptance) |
| Access Point Restriction | All APs |

---

## Custom HTML (if UniFi supports full portal customization)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Sojourn Church Guest WiFi</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; text-align: center; }
        .logo { margin-bottom: 20px; }
        .terms { text-align: left; background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .terms h3 { margin-top: 0; }
        .terms ul { padding-left: 20px; }
        .checkbox { margin: 20px 0; }
        button { background: #2c5aa0; color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        button:disabled { background: #999; }
        button:hover:not(:disabled) { background: #1a3d70; }
    </style>
</head>
<body>
    <div class="logo">
        <img src="sojourn-logo.png" alt="Sojourn Church Logo" width="200">
        <h1>Welcome to Sojourn Church</h1>
        <p>Free Guest WiFi</p>
    </div>
    
    <p>Thank you for visiting! WiFi access is provided as a courtesy for guests and visitors.</p>
    
    <div class="terms">
        <h3>Terms of Use</h3>
        <p><strong>Acceptable Use:</strong></p>
        <ul>
            <li>This network is for lawful purposes only</li>
            <li>Do not use for illegal downloads, streaming copyrighted content, or malicious activity</li>
            <li>Be respectful of bandwidth — others are also using this connection</li>
        </ul>
        
        <p><strong>Privacy &amp; Security:</strong></p>
        <ul>
            <li>This is a public, unsecured network. Do not transmit sensitive information.</li>
            <li>The church reserves the right to block abusive usage.</li>
            <li>Use of this network is at your own risk.</li>
        </ul>
        
        <p><strong>Time Limits:</strong> Guest access is limited to 12 hours per session. Bandwidth is shared fairly.</p>
        
        <p><strong>Support:</strong> Having trouble? Email sojournchurchtech@gmail.com</p>
    </div>
    
    <form method="post" action="$auth_action">
        <input type="hidden" name="mac" value="$mac">
        <input type="hidden" name="ip" value="$ip">
        <input type="hidden" name="ap" value="$ap_mac">
        <input type="hidden" name="t" value="$token">
        
        <div class="checkbox">
            <label>
                <input type="checkbox" name="accept_terms" required>
                I have read and agree to the Terms of Use above.
            </label>
        </div>
        
        <button type="submit">Connect to Internet</button>
    </form>
</body>
</html>
```

---

## Notes
- Logo file: `docs/media/sojourn-logo.png` (ready for upload to UniFi portal)
- Colors can be adjusted to match church branding
- The HTML above is a template — UniFi's built-in portal editor may have limitations
- If full HTML isn't supported, use UniFi's basic terms-of-use text field with the body text above
- For UniFi portal: upload logo under Settings → Guest Control → Upload Custom Logo
