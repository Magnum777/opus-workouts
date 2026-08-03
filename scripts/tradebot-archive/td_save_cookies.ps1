# Extract full TorrentDay cookie values and save to .secrets
$dbPath = "C:\Users\compj\AppData\Roaming\Mozilla\Firefox\Profiles\dnhgd3mm.default-release\cookies.sqlite"
$tmpPath = "$env:TEMP\firefox_cookies_copy2.sqlite"
Copy-Item $dbPath $tmpPath -Force

$python = @"
import sqlite3
import json

db_path = r'C:\Users\compj\AppData\Local\Temp\firefox_cookies_copy2.sqlite'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT name, value, host, path, isSecure, isHttpOnly, expiry FROM moz_cookies WHERE host LIKE '%torrentday%'")
rows = cur.fetchall()

cookies = {}
for name, value, host, path, secure, httponly, expiry in rows:
    cookies[name] = {"value": value, "host": host, "path": path, "secure": secure, "httponly": httponly}

print(json.dumps(cookies, indent=2))
conn.close()
"@

$result = $python | python
$cookies = $result | ConvertFrom-Json

Write-Host "Cookies extracted:"
Write-Host "  uid: $($cookies.uid.value)"
Write-Host "  pass: $($cookies.pass.value)"

# Update .secrets file with torrentday cookies
$secretsPath = "C:\Users\compj\.openclaw\workspace\.secrets"
$secrets = Get-Content $secretsPath

# Build new content
$newContent = @()
$inTDSection = $false
$tdAdded = $false
foreach ($line in $secrets) {
    if ($line -match '^\[torrentday\]') {
        $inTDSection = $true
        $newContent += "[torrentday]"
        $newContent += "username=opusmagnum"
        $newContent += "password=Dr34k3r!123123"
        $newContent += "uid=$($cookies.uid.value)"
        $newContent += "pass_cookie=$($cookies.pass.value)"
        $tdAdded = $true
        continue
    }
    if ($inTDSection -and $line -match '^\[') {
        $inTDSection = $false
    }
    if (-not $inTDSection) {
        $newContent += $line
    }
}

if (-not $tdAdded) {
    $newContent += ""
    $newContent += "[torrentday]"
    $newContent += "username=opusmagnum"
    $newContent += "password=Dr34k3r!123123"
    $newContent += "uid=$($cookies.uid.value)"
    $newContent += "pass_cookie=$($cookies.pass.value)"
}

$newContent | Set-Content $secretsPath -Encoding UTF8
Write-Host "`nSaved to .secrets"