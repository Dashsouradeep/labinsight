# Install Tesseract OCR on Windows

Tesseract is required for OCR (text extraction from images). Follow these steps:

## Step 1: Download Tesseract

1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest installer (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)
3. Run the installer

## Step 2: Install Tesseract

1. During installation, note the installation path (default: `C:\Program Files\Tesseract-OCR`)
2. Make sure to select "English" language data during installation
3. Complete the installation

## Step 3: Add to System PATH

1. Open System Environment Variables:
   - Press `Win + R`
   - Type `sysdm.cpl` and press Enter
   - Go to "Advanced" tab
   - Click "Environment Variables"

2. Edit PATH variable:
   - Under "System variables", find and select "Path"
   - Click "Edit"
   - Click "New"
   - Add: `C:\Program Files\Tesseract-OCR`
   - Click "OK" on all windows

## Step 4: Verify Installation

Open a NEW command prompt and run:
```cmd
tesseract --version
```

You should see version information like:
```
tesseract 5.3.3
```

## Step 5: Install Python Package

In your project virtual environment:
```cmd
cd E:\EHR_Reviewer
.venv\Scripts\activate
pip install pytesseract
```

## Step 6: Restart Backend

After installation, restart your backend server:
```cmd
cd backend
python -m uvicorn main:app --reload --port 8000
```

## Troubleshooting

If you get "Tesseract not found" error:
1. Make sure Tesseract is installed at `C:\Program Files\Tesseract-OCR`
2. Make sure you added it to PATH
3. Restart your command prompt/terminal
4. Restart your backend server

If PATH doesn't work, you can set it manually in Python:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```
