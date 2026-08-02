# Synology DSM API - check Web Station & shares
$nas = "MND"
$user = "Nova"
$pass = "D0ngaYHRuthV93qD"

# Ignore cert errors
add-type @"
using System.Net;
using System.Security.Cryptography.X509Certificates;
public class TrustAll : ICertificatePolicy {
    public bool CheckValidationResult(ServicePoint srv, X509Certificate cert, WebRequest req, int prob) { return true; }
}
"@
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAll

# Login
$loginUrl = "https://${nas}:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=login&account=$user&passwd=$([System.Uri]::EscapeDataString($pass))&format=sid"
$resp = Invoke-RestMethod -Uri $loginUrl -ErrorAction Stop
if ($resp.success) {
    $sid = $resp.data.sid
    Write-Host "Login OK, SID: $sid"
} else {
    Write-Host "Login failed: $($resp | ConvertTo-Json -Compress)"
    exit 1
}

# Check packages
$pkgUrl = "https://${nas}:5001/webapi/entry.cgi?api=SYNO.Core.Package&version=1&method=list&_sid=$sid"
$resp = Invoke-RestMethod -Uri $pkgUrl
$ws = $resp.data.packages | Where-Object { $_.package -like "*webstation*" -or $_.package -like "*WebStation*" -or $_.package -like "*web_station*" }
if ($ws) { Write-Host "Web Station: $($ws.package) v$($ws.version)" }
else { Write-Host "Web Station NOT installed" }

# List relevant packages
Write-Host "`nAll packages:"
$resp.data.packages | Sort-Object package | ForEach-Object { Write-Host "  $($_.package) v$($_.version)" }

# Check shares
$shareUrl = "https://${nas}:5001/webapi/entry.cgi?api=SYNO.Core.Share&version=1&method=list&_sid=$sid"
$resp = Invoke-RestMethod -Uri $shareUrl
Write-Host "`nShares:"
$resp.data.shares | ForEach-Object { Write-Host "  $($_.name) -> $($_.volume_path)" }

# Logout
$logoutUrl = "https://${nas}:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=logout&_sid=$sid"
Invoke-RestMethod -Uri $logoutUrl | Out-Null