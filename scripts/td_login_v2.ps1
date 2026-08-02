# TorrentDay login with proper cookie handling and redirect following
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

# Use www.torrentday.com (the 308 redirect target)
$baseUrl = "https://www.torrentday.com"

# Create session with proper headers
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

# Step 1: GET the login page first to get any CSRF/cookies
Write-Host "=== Step 1: Get login page ==="
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/torrents/login.php" -WebSession $session -UseBasicParsing -ErrorAction Stop
    Write-Host "Status: $($response.StatusCode), Length: $($response.Content.Length)"
    Write-Host "Cookies after GET: $($session.Cookies.GetAllCookies().Count)"
    foreach ($c in $session.Cookies.GetAllCookies()) {
        Write-Host "  $($c.Name)=$($c.Value.Substring(0,[Math]::Min(20,$c.Value.Length)))..."
    }
    
    # Check for Cloudflare challenge
    if ($response.Content -match "Cloudflare|challenge-platform|turnstile") {
        Write-Host "CLOUDFLARE DETECTED - needs browser automation"
    }
    
    # Check for CSRF token
    $csrfMatches = [regex]::Matches($response.Content, '(?i)(csrf|token|_token).*?value=["\']([^"\']+)')
    if ($csrfMatches.Count -gt 0) {
        Write-Host "CSRF token found: $($csrfMatches[0].Groups[2].Value)"
    }
    
    # Save for analysis
    $response.Content | Out-File "C:\Users\compj\.openclaw\workspace\scripts\td_login_page.html" -Encoding UTF8
    
    # Show form fields
    $formMatches = [regex]::Matches($response.Content, '<input[^>]*name=["\']([^"\']+)["\'][^>]*>')
    Write-Host "`nForm fields found:"
    foreach ($m in $formMatches) {
        Write-Host "  $($m.Groups[1].Value)"
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}

# Step 2: Try POST login with cookies from GET
Write-Host "`n=== Step 2: POST login ==="
$loginBody = "username=$([System.Uri]::EscapeDataString($tdUser))&password=$([System.Uri]::EscapeDataString($tdPass))"
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/torrents/login.php" -Method Post -Body $loginBody -WebSession $session -UseBasicParsing -ContentType "application/x-www-form-urlencoded" -ErrorAction Stop
    Write-Host "Login status: $($response.StatusCode), Length: $($response.Content.Length)"
    Write-Host "Cookies after POST: $($session.Cookies.GetAllCookies().Count)"
    foreach ($c in $session.Cookies.GetAllCookies()) {
        Write-Host "  $($c.Name)=$($c.Value.Substring(0,[Math]::Min(30,$c.Value.Length)))..."
    }
    
    # Check response for success/failure indicators
    if ($response.Content -match "error|incorrect|invalid|failed|banned|disabled") {
        Write-Host "LOGIN FAILED - error text found"
    } elseif ($response.Content -match "welcome|dashboard|browse|logout") {
        Write-Host "LOGIN APPEARS SUCCESSFUL"
    } else {
        Write-Host "Login result unclear - saving response"
        $response.Content | Out-File "C:\Users\compj\.openclaw\workspace\scripts\td_login_response.html" -Encoding UTF8
    }
    
    # Check if we got redirected to browse page
    if ($response.BaseResponse.ResponseUri -match "login") {
        Write-Host "Still on login page - auth may have failed"
    } else {
        Write-Host "Redirected to: $($response.BaseResponse.ResponseUri)"
    }
} catch {
    Write-Host "Login error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        Write-Host "Status: $($_.Exception.Response.StatusCode)"
    }
}

# Step 3: Try authenticated browse
Write-Host "`n=== Step 3: Try browse with session ==="
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/torrents/browse.php" -WebSession $session -UseBasicParsing -ErrorAction Stop
    Write-Host "Browse status: $($response.StatusCode), Length: $($response.Content.Length)"
    
    if ($response.Content.Length -gt 10000) {
        Write-Host "Got substantial content - likely authenticated!"
        # Look for torrent data
        $torrentRows = [regex]::Matches($response.Content, '<tr[^>]*class=["\']([^"\']*)')
        Write-Host "Table rows found: $($torrentRows.Count)"
        
        # Look for freeleech
        $freeMatches = [regex]::Matches($response.Content, '(?i)free')
        Write-Host "'free' mentions: $($freeMatches.Count)"
        
        # Save for analysis
        $response.Content | Out-File "C:\Users\compj\.openclaw\workspace\scripts\td_browse_authed.html" -Encoding UTF8
    } else {
        Write-Host "Short response - probably still login page"
        Write-Host "First 500: $($response.Content.Substring(0, [Math]::Min(500, $response.Content.Length)))"
    }
} catch {
    Write-Host "Browse error: $($_.Exception.Message)"
}

Write-Host "`nDone"