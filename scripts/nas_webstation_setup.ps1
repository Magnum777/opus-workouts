# Set up Synology Web Station via API to serve night-school viewer
# DSM API approach

# First, try to login to DSM API
$nas = "MND"
$user = "Nova"
$pass = "D0ngaYHRuthV93qD"

# Ignore cert errors for self-signed
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}

# Step 1: Login
try {
    $loginUrl = "https://${nas}:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=login&account=$user&passwd=$([System.Uri]::EscapeDataString($pass))&format=sid"
    $response = Invoke-RestMethod -Uri $loginUrl -Method Get -SkipCertificateCheck -ErrorAction Stop
    if ($response.success) {
        $sid = $response.data.sid
        Write-Host "Login OK, SID: $sid"
    } else {
        Write-Host "Login failed: $($response.error | ConvertTo-Json)"
        exit 1
    }
} catch {
    Write-Host "Login error: $($_.Exception.Message)"
    exit 1
}

# Step 2: Check if Web Station is installed
try {
    $pkgUrl = "https://${nas}:5001/webapi/entry.cgi?api=SYNO.Core.Package&version=1&method=list&additional=%5B%22installed%22%5D&_sid=$sid"
    $response = Invoke-RestMethod -Uri $pkgUrl -SkipCertificateCheck
    $webStation = $response.data.packages | Where-Object { $_.package -eq "com.synology.webstation" -or $_.package -eq "WebStation" }
    if ($webStation) {
        Write-Host "Web Station found: $($webStation.package) v$($webStation.version)"
    } else {
        Write-Host "Web Station not found in installed packages"
        # List all packages for reference
        Write-Host "Installed packages:"
        $response.data.packages | ForEach-Object { Write-Host "  $($_.package) - $($_.version)" }
    }
} catch {
    Write-Host "Package check error: $($_.Exception.Message)"
}

# Step 3: Check current shared folders
try {
    $shareUrl = "https://${nas}:5001/webapi/entry.cgi?api=SYNO.Core.Share&version=1&method=list&_sid=$sid"
    $response = Invoke-RestMethod -Uri $shareUrl -SkipCertificateCheck
    Write-Host "`nShared folders:"
    $response.data.shares | ForEach-Object { Write-Host "  $($_.name) - $($_.volume_path)" }
} catch {
    Write-Host "Share check error: $($_.Exception.Message)"
}

# Step 4: Logout
try {
    $logoutUrl = "https://${nas}:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=logout&_sid=$sid"
    Invoke-RestMethod -Uri $logoutUrl -SkipCertificateCheck | Out-Null
    Write-Host "`nLogged out"
} catch {}