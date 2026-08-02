# Check Synology NAS web server status and config
$cred = New-Object System.Management.Automation.PSCredential("Nova", (ConvertTo-SecureString 'D0ngaYHRuthV93qD' -AsPlainText -Force))
Remove-PSDrive -Name "Z" -Force -ErrorAction SilentlyContinue
New-PSDrive -Name "Z" -PSProvider FileSystem -Root "\\MND\home" -Credential $cred -ErrorAction Stop | Out-Null

# Check if web folder exists
$webFolder = Get-Item "Z:\web" -ErrorAction SilentlyContinue
if ($webFolder) {
    Write-Host "Web folder exists: $($webFolder.FullName)"
    Get-ChildItem "Z:\web" -Recurse -ErrorAction SilentlyContinue | Select-Object FullName, Length | Format-Table -AutoSize
} else {
    Write-Host "No 'web' folder found on home share"
}

# Check for existing web-shared folders
foreach ($folder in @("www", "web_shared", "http", "html", "public_html", "web")) {
    $item = Get-Item "Z:\$folder" -ErrorAction SilentlyContinue
    if ($item) { Write-Host "Found: $folder" }
}

# Check if port 80/443 is responding on NAS
try {
    $tcp80 = New-Object System.Net.Sockets.TcpClient
    $tcp80.Connect("MND", 80)
    Write-Host "Port 80: OPEN (web server running)"
    $tcp80.Close()
} catch { Write-Host "Port 80: CLOSED (no web server)" }

try {
    $tcp443 = New-Object System.Net.Sockets.TcpClient
    $tcp443.Connect("MND", 443)
    Write-Host "Port 443: OPEN (HTTPS running)"
    $tcp443.Close()
} catch { Write-Host "Port 443: CLOSED" }

try {
    $tcp5000 = New-Object System.Net.Sockets.TcpClient
    $tcp5000.Connect("MND", 5000)
    Write-Host "Port 5000: OPEN (DSM)"
    $tcp5000.Close()
} catch { Write-Host "Port 5000: CLOSED" }

# Try a quick HTTP request
try {
    $response = Invoke-WebRequest -Uri "http://MND/" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    Write-Host "HTTP response: $($response.StatusCode) - $($response.StatusDescription)"
    Write-Host "Content length: $($response.Content.Length)"
    Write-Host "First 200 chars: $($response.Content.Substring(0, [Math]::Min(200, $response.Content.Length)))"
} catch {
    Write-Host "HTTP request failed: $($_.Exception.Message)"
}

Remove-PSDrive -Name "Z" -Force