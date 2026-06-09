# Convert all .md files to HTML and PDF
# Usage: .\convert-docs.ps1

$ErrorActionPreference = "Stop"
$DocDir = "$PSScriptRoot\..\docs"
$StyleSheet = "$DocDir\nova-style.css"

# Check pandoc
$pandoc = Get-Command pandoc -ErrorAction SilentlyContinue
if (-not $pandoc) {
    Write-Error "Pandoc not found. Install: winget install JohnMacFarlane.Pandoc"
    exit 1
}

Write-Host "=== Converting Markdown to HTML ===" -ForegroundColor Cyan

# Find Edge
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $edge)) {
    $edge = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
}

# Convert PDF docs
$PdfDocs = Get-ChildItem "$DocDir\PDF\*.md"
foreach ($doc in $PdfDocs) {
    $baseName = $doc.BaseName
    $outHtml = "$DocDir\PDF\$baseName.html"
    $outPdf = "$DocDir\PDF\$baseName.pdf"
    
    # MD to HTML
    pandoc $doc.FullName -o $outHtml --css=../nova-style.css --standalone --from=markdown --to=html5 --metadata title="Nova AI Cofounder V3"
    Write-Host "  HTML: $baseName" -ForegroundColor Green
    
    # HTML to PDF via Edge
    if (Test-Path $edge) {
        $fileUrl = "file:///" + $outHtml.replace('\', '/')
        Start-Process $edge -ArgumentList "--headless","--print-to-pdf=$outPdf","--run-all-compositor-stages-before-draw","--virtual-time-budget=10000","$fileUrl" -Wait -WindowStyle Hidden
        if (Test-Path $outPdf) {
            Write-Host "  PDF:  $baseName" -ForegroundColor Green
        } else {
            Write-Host "  PDF failed: $baseName" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  PDF skipped: $baseName (Edge not found)" -ForegroundColor Yellow
    }
}

# Convert video scripts
Write-Host "`n=== Converting Video Scripts ===" -ForegroundColor Cyan
$VideoScripts = Get-ChildItem "$DocDir\video-scripts\*.md"
foreach ($script in $VideoScripts) {
    $baseName = $script.BaseName
    $outHtml = "$DocDir\video-scripts\$baseName.html"
    pandoc $script.FullName -o $outHtml --css=../nova-style.css --standalone --from=markdown --to=html5 --metadata title="Nova V3 Video Script"
    Write-Host "  HTML: $baseName" -ForegroundColor Green
}

Write-Host "`nDone. Check $DocDir" -ForegroundColor Cyan
