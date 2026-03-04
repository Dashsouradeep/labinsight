# Automated Tesseract OCR Installation Script for Windows
# Run this with: powershell -ExecutionPolicy Bypass -File install_tesseract.ps1

Write-Host "=== Tesseract OCR Installation ===" -ForegroundColor Cyan
Write-Host ""

# Check if already installed
$tesseractPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"
if (Test-Path $tesseractPath) {
    Write-Host "✓ Tesseract is already installed at: $tesseractPath" -ForegroundColor Green
    & $tesseractPath --version
    Write-Host ""
    Write-Host "Tesseract is ready to use!" -ForegroundColor Green
    exit 0
}

Write-Host "Downloading Tesseract OCR installer..." -ForegroundColor Yellow

# Download URL for Tesseract 5.3.3
$url = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
$output = "$env:TEMP\tesseract-installer.exe"

try {
    # Download installer
    Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
    Write-Host "✓ Downloaded installer" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Starting installation..." -ForegroundColor Yellow
    Write-Host "Please follow the installer prompts:" -ForegroundColor Yellow
    Write-Host "  1. Accept the license" -ForegroundColor White
    Write-Host "  2. Keep default installation path: C:\Program Files\Tesseract-OCR" -ForegroundColor White
    Write-Host "  3. Make sure 'English' language is selected" -ForegroundColor White
    Write-Host "  4. Complete the installation" -ForegroundColor White
    Write-Host ""
    
    # Run installer (will show GUI)
    Start-Process -FilePath $output -Wait
    
    # Check if installed
    if (Test-Path $tesseractPath) {
        Write-Host ""
        Write-Host "✓ Tesseract installed successfully!" -ForegroundColor Green
        
        # Add to PATH
        Write-Host ""
        Write-Host "Adding Tesseract to system PATH..." -ForegroundColor Yellow
        
        $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
        $tesseractDir = "C:\Program Files\Tesseract-OCR"
        
        if ($currentPath -notlike "*$tesseractDir*") {
            try {
                [Environment]::SetEnvironmentVariable(
                    "Path",
                    "$currentPath;$tesseractDir",
                    "Machine"
                )
                Write-Host "✓ Added to PATH" -ForegroundColor Green
                Write-Host ""
                Write-Host "IMPORTANT: Please restart your terminal/command prompt for PATH changes to take effect!" -ForegroundColor Yellow
            } catch {
                Write-Host "⚠ Could not add to PATH automatically (requires admin rights)" -ForegroundColor Yellow
                Write-Host "Please add manually: C:\Program Files\Tesseract-OCR" -ForegroundColor White
            }
        } else {
            Write-Host "✓ Already in PATH" -ForegroundColor Green
        }
        
        Write-Host ""
        Write-Host "Installation complete!" -ForegroundColor Green
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "  1. Restart your terminal/command prompt" -ForegroundColor White
        Write-Host "  2. Run: cd E:\EHR_Reviewer\backend" -ForegroundColor White
        Write-Host "  3. Run: python test_tesseract.py" -ForegroundColor White
        Write-Host "  4. Restart backend server" -ForegroundColor White
        
    } else {
        Write-Host "✗ Installation may have failed or was cancelled" -ForegroundColor Red
        Write-Host "Please install manually from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Yellow
    }
    
    # Cleanup
    Remove-Item $output -ErrorAction SilentlyContinue
    
} catch {
    Write-Host "✗ Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install manually:" -ForegroundColor Yellow
    Write-Host "  1. Go to: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor White
    Write-Host "  2. Download: tesseract-ocr-w64-setup-5.3.3.20231005.exe" -ForegroundColor White
    Write-Host "  3. Run installer and follow prompts" -ForegroundColor White
    Write-Host "  4. Add to PATH: C:\Program Files\Tesseract-OCR" -ForegroundColor White
}
