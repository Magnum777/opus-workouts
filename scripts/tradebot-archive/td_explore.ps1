# TorrentDay site exploration - login and scrape structure
# Reads creds from .secrets, no hardcoding

$secretsFile = "C:\Users\compj\.openclaw\workspace\.secrets"
$lines = Get-Content $secretsFile
$section = ""; $tdUser = ""; $tdPass = ""
foreach ($line in $lines) {
    if ($line -match '^\[(\w+)\]') { $section = $Matches[1]; continue }
    if ($line -match '^(\w+)=(.+)$' -and $section -eq "torrentday") {
        switch ($Matches[1]) {
            "username" { $tdUser = $Matches[2] }
            "password" { $tdPass = $Matches[2] }
        }
    }
}

Write-Host "Creds loaded: user=$tdUser pass_len=$($tdPass.Length)"

# Use Invoke-WebRequest with session
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# Step 1: Login to TorrentDay
Write-Host "`n=== Logging into TorrentDay ==="
$loginUrl = "https://torrentday.com/torrents/login.php"
$loginBody = @{
    username = $tdUser
    password = $tdPass
}

try {
    $response = Invoke-WebRequest -Uri $loginUrl -Method Post -Body $loginBody -WebSession $session -UseBasicParsing -ErrorAction Stop
    Write-Host "Login response status: $($response.StatusCode)"
    Write-Host "Cookies: $($session.Cookies.Count) cookies"
    foreach ($cookie in $session.Cookies.GetAllCookies()) {
        Write-Host "  Cookie: $($cookie.Name)=$($cookie.Value.Substring(0, [Math]::Min(20, $cookie.Value.Length)))..."
    }
    
    # Check if login succeeded (look for error indicators)
    $content = $response.Content
    if ($content -match "error|incorrect|invalid|failed") {
        Write-Host "LOGIN MAY HAVE FAILED - error text found in response"
        Write-Host "Response (first 500 chars): $($content.Substring(0, [Math]::Min(500, $content.Length)))"
    } else {
        Write-Host "Login appears successful (no error text in response)"
    }
} catch {
    Write-Host "Login error: $($_.Exception.Message)"
    # Try alternate URL
    Write-Host "`nTrying alternate URL..."
    try {
        $response = Invoke-WebRequest -Uri "https://www.torrentday.com/torrents/login.php" -Method Post -Body $loginBody -WebSession $session -UseBasicParsing
        Write-Host "Alt login status: $($response.StatusCode)"
    } catch {
        Write-Host "Alt login error: $($_.Exception.Message)"
    }
}

# Step 2: Browse the main page / torrent list
Write-Host "`n=== Browsing torrent list ==="
try {
    $browseUrl = "https://torrentday.com/torrents/"
    $response = Invoke-WebRequest -Uri $browseUrl -WebSession $session -UseBasicParsing
    $content = $response.Content
    
    # Extract links and structure
    Write-Host "Page length: $($content.Length) chars"
    
    # Look for category links
    if ($content -match 'cat\[([^]]+)\]') {
        Write-Host "Found category selector"
    }
    
    # Look for torrent table structure
    $linkMatches = [regex]::Matches($content, 'href="([^"]*)"')
    $uniqueLinks = $linkMatches | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
    Write-Host "Unique links on page: $($uniqueLinks.Count)"
    
    # Look for freeleech indicators
    $freeleech = [regex]::Matches($content, '(?i)free(leech|[\s_]?download)')
    Write-Host "Freeleech mentions: $($freeleech.Count)"
    
    # Save page for analysis
    $outFile = "C:\Users\compj\.openclaw\workspace\scripts\td_browse.html"
    $content | Out-File -FilePath $outFile -Encoding UTF8
    Write-Host "Saved browse page to $outFile"
    
    # Show first 2000 chars
    Write-Host "`nPage preview (first 2000 chars):"
    Write-Host $content.Substring(0, [Math]::Min(2000, $content.Length))
} catch {
    Write-Host "Browse error: $($_.Exception.Message)"
}

# Step 3: Check for API/JSON endpoints
Write-Host "`n=== Checking for API endpoints ==="
$apiUrls = @(
    "https://torrentday.com/torrents/api",
    "https://torrentday.com/api/",
    "https://torrentday.com/torrents/browse.php?json=1",
    "https://torrentday.com/torrents/browse.php"
)

foreach ($url in $apiUrls) {
    try {
        $response = Invoke-WebRequest -Uri $url -WebSession $session -UseBasicParsing -ErrorAction Stop
        $contentType = $response.Headers.'Content-Type'
        Write-Host "  $url -> $($response.StatusCode) ($contentType, $($response.Content.Length) chars)"
        if ($contentType -match 'json') {
            Write-Host "    JSON response: $($response.Content.Substring(0, [Math]::Min(500, $response.Content.Length)))"
        }
    } catch {
        Write-Host "  $url -> $($_.Exception.Message.Substring(0, [Math]::Min(100, $_.Exception.Message.Length)))"
    }
}

Write-Host "`nDone"