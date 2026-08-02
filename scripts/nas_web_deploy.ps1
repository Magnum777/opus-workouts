# Copy night-school viewer + content to NAS web share
$cred = New-Object System.Management.Automation.PSCredential("Nova", (ConvertTo-SecureString 'D0ngaYHRuthV93qD' -AsPlainText -Force))
Remove-PSDrive -Name "Z" -Force -ErrorAction SilentlyContinue
New-PSDrive -Name "Z" -PSProvider FileSystem -Root "\\MND\web" -Credential $cred -ErrorAction Stop | Out-Null
Write-Host "Connected to \\MND\web"

# Check existing contents
Write-Host "`nCurrent web share contents:"
Get-ChildItem "Z:\" -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "  $($_.Name)" }

# Create night-school directory
New-Item -Path "Z:\night-school" -ItemType Directory -Force | Out-Null
Write-Host "`nCreated Z:\night-school"

# Copy viewer HTML to web root
Copy-Item "C:\Users\compj\.openclaw\workspace\night-school-viewer.html" "Z:\night-school-viewer.html" -Force
Write-Host "Copied night-school-viewer.html to web root"

# Copy all night-school content
$src = "C:\Users\compj\.openclaw\workspace\night-school"
$dst = "Z:\night-school"
$count = 0
Get-ChildItem $src -Directory | ForEach-Object {
    $destPath = Join-Path $dst $_.Name
    Copy-Item $_.FullName -Destination $destPath -Recurse -Force
    $count++
}
Write-Host "Copied $count topic folders to web share"

# Also copy root-level .md files
$mdCount = 0
Get-ChildItem $src -Filter "*.md" | ForEach-Object {
    Copy-Item $_.FullName -Destination (Join-Path $dst $_.Name) -Force
    $mdCount++
}
Write-Host "Copied $mdCount root-level md files"

# Verify
$viewer = Get-Item "Z:\night-school-viewer.html"
$topicDirs = (Get-ChildItem "Z:\night-school" -Directory).Count
Write-Host "`nVerification:"
Write-Host "  Viewer: $([math]::Round($viewer.Length/1KB, 1)) KB"
Write-Host "  Topic dirs: $topicDirs"

Remove-PSDrive -Name "Z" -Force
Write-Host "`nDone!"