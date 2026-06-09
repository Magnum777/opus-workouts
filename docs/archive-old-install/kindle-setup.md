# Kindle Unlimited to EPUB Setup

## Step 1: Install Plugins (Manual)

### DeDRM Plugin
1. Download: https://github.com/noDRM/DeDRM_tools/releases/latest
2. Extract to a folder
3. Calibre → Preferences → Advanced → Plugins → Load plugin from file
4. Select `DeDRM_plugin.zip`

### KFX Input Plugin
1. Calibre → Preferences → Get plugins to enhance Calibre
2. Search "KFX" → Install

## Step 2: Download Kindle for PC 2.8
- Version 2.3.70682 or 2.8 (older versions work better)
- https://www.download3k.com/Install-Kindle-for-PC.html
- Login and download your Kindle Unlimited books

## Step 3: Automation Setup
Run: `powershell -ExecutionPolicy Bypass -File kindle-auto.ps1`
