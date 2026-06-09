# Home Network Solution for Two-Story Home
## By Nova (AI Assistant) 🦝

---

## The Problem

Your friend's new home has:
- ✅ Fiber internet installed on 2nd floor (opposite side of house from office)
- ✅ No existing ethernet wiring between floors
- ✅ Coax cables running throughout the house

---

## The Solution: Ubiquiti + MoCA

This solution uses Ubiquiti equipment for WiFi and MoCA adapters to use existing coax cables for hardwired internet.

---

## Option 1: Budget-Friendly (~$350)

| Item | Product | Price | Link |
|------|---------|-------|------|
| **Router/AP** | Ubiquiti UniFi Dream Machine SE | ~$180 | [Amazon](https://www.amazon.com/Ubiquiti-Networks-UDM-SE-Dream/dp/B0FKDY5YXH) |
| **WiFi AP** | Ubiquiti UniFi 6 Long-Range | ~$80 | [Amazon](https://www.amazon.com/Ubiquiti-U6-Long-Range-US/dp/B09HX2XQBS) |
| **MoCA Adapters** | goCoax MoCA 2.5 (2-pack) | ~$90 | [Amazon](https://www.amazon.com/goCoax-Ethernet-Adapter-2-5Gbps/dp/B0BZMXG8T6) |
| **Total** | | **~$350** | |

---

## Option 2: Pro-Grade (~$450)

| Item | Product | Price | Link |
|------|---------|-------|------|
| **Router/AP** | Ubiquiti UniFi Dream Machine Pro | ~$280 | [Amazon](https://www.amazon.com/Ubiquiti-UDM-PRO-Integrated-Security-Rack-Mount/dp/B0DVC9233C) |
| **WiFi AP** | Ubiquiti UniFi 6 Long-Range | ~$80 | [Amazon](https://www.amazon.com/Ubiquiti-U6-Long-Range-US/dp/B09HX2XQBS) |
| **MoCA Adapters** | goCoax MoCA 2.5 (2-pack) | ~$90 | [Amazon](https://www.amazon.com/goCoax-Ethernet-Adapter-2-5Gbps/dp/B0BZMXG8T6) |
| **Total** | | **~$450** | |

---

## How It Works

```
                    2nd Floor
    ┌─────────────────────────────────────┐
    │  Fiber ISP → Modem → UDM Router    │
    │                                     │
    │  Coax → MoCA Adapter ───────────────┘
    │              │
    │              │ Existing Coax Wiring
    │              │
    └──────────────┘
                    1st Floor
    ┌─────────────────────────────────────┐
    │  MoCA Adapter → Ethernet → Office  │
    │                                     │
    │  UniFi 6 LR → WiFi Coverage       │
    └─────────────────────────────────────┘
```

---

## Why This Works

1. **Ubiquiti** = Professional-grade WiFi, mesh network capable
2. **MoCA** = Uses existing coax cables (no new wires needed!)
3. **2.5Gbps** = Fast enough for most uses
4. **Scalable** = Add more APs if needed

---

## HOW TO SET UP - Step by Step

### Step 1: Install Ubiquiti Dream Machine (2nd Floor)
1. Unbox the Dream Machine
2. Connect to your fiber modem via ethernet cable
3. Plug in power cable
4. Download "UniFi Network" app from App Store or Google Play
5. Open app and follow setup instructions
6. Create a UniFi account (free)

### Step 2: Install UniFi 6 Long-Range (1st Floor)
1. Find a good central location for the AP (ceiling mount is best)
2. Connect the AP to power (or use PoE if you have a PoE switch)
3. The AP will automatically appear in your UniFi app
4. Name your WiFi network and set a password

### Step 3: Install MoCA Adapters
**Adapter 1 (Near Router - 2nd Floor):**
1. Plug MoCA adapter into power outlet
2. Connect MoCA adapter to router using ethernet cable
3. Connect MoCA adapter to any coax outlet using coax cable

**Adapter 2 (In Office - 1st Floor):**
1. Plug second MoCA adapter into power outlet in office
2. Connect MoCA adapter to coax outlet in office
3. Connect your computer/device to the MoCA adapter via ethernet cable

### Step 4: Configure WiFi (Via UniFi App)
1. Open UniFi Network app
2. Go to "WiFi" section
3. Create your network name (SSID)
4. Set a strong password
5. Optionally set up a guest network

---

## Troubleshooting Tips

**No internet on MoCA?**
- Check that both MoCA adapters are connected to coax and powered on
- Verify the coax connection is secure
- Try a different coax outlet

**WiFi not reaching?**
- Move the UniFi 6 LR to a more central location
- Add another access point
- Check for interference from other devices

**Slow speeds?**
- MoCA 2.5 supports up to 2.5Gbps (your internet may be slower)
- Check ethernet cables are Cat5e or better

---

## Need Help?

This was designed by **Nova** - an AI assistant! 🦝

Questions? Reach out and I can help troubleshoot!

---

## What You'll Need to Buy

### For Option 1 (~$350):
- [ ] Ubiquiti UniFi Dream Machine SE ($180)
- [ ] Ubiquiti UniFi 6 Long-Range ($80)
- [ ] goCoax MoCA 2.5 Adapters 2-pack ($90)

### For Option 2 (~$450):
- [ ] Ubiquiti UniFi Dream Machine Pro ($280)
- [ ] Ubiquiti UniFi 6 Long-Range ($80)
- [ ] goCoax MoCA 2.5 Adapters 2-pack ($90)

---

*Created by Nova - AI Assistant* 🦝
