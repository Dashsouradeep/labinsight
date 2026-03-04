# Fix OCR Issue - Switch to Tesseract

## Problem
PaddleOCR has compatibility issues with Windows (oneDNN error). All uploaded reports are failing during OCR processing.

## Solution
We've switched to Tesseract OCR, which is more stable on Windows.

## Installation Steps

### 1. Install Tesseract OCR Software

1. Download Tesseract installer:
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download: `tesseract-ocr-w64-setup-5.3.3.20231005.exe` (or latest version)

2. Run the installer:
   - Install to default location: `C:\Program Files\Tesseract-OCR`
   - Make sure "English" language is selected
   - Complete installation

3. Add to System PATH:
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Go to "Advanced" tab → "Environment Variables"
   - Under "System variables", select "Path" → "Edit"
   - Click "New" and add: `C:\Program Files\Tesseract-OCR`
   - Click OK on all windows

4. Verify installation:
   - Open a NEW command prompt
   - Run: `tesseract --version`
   - You should see version info

### 2. Install Python Package

```cmd
cd E:\EHR_Reviewer
.venv\Scripts\activate
pip install pytesseract
```

### 3. Test Tesseract

```cmd
cd backend
python test_tesseract.py
```

You should see:
```
✓ Tesseract OCR found: version 5.3.3
✓ pytesseract package installed

Tesseract is ready to use!
```

### 4. Restart Backend

Stop your current backend (Ctrl+C) and restart:

```cmd
cd E:\EHR_Reviewer\backend
python -m uvicorn main:app --reload --port 8000
```

### 5. Test Upload

1. Go to http://localhost:3000/upload
2. Upload a JPG or PNG image of a lab report
3. Check backend logs - you should see successful OCR extraction
4. Go to dashboard - you should see the report with extracted parameters

## What Changed

- Replaced `backend/services/ocr_service.py` (PaddleOCR) with `backend/services/ocr_service_tesseract.py` (Tesseract)
- Updated `backend/services/processing_pipeline.py` to use new OCR service
- Updated `backend/requirements.txt` to use pytesseract instead of paddleocr
- Tesseract is more stable and widely used on Windows

## Troubleshooting

### "Tesseract not found" error
- Make sure Tesseract is installed at `C:\Program Files\Tesseract-OCR`
- Make sure you added it to PATH
- Restart your command prompt
- Restart backend server

### Still not working?
If PATH doesn't work, you can manually set the path in `backend/services/ocr_service_tesseract.py`:

Add this at the top after imports:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Next Steps

Once OCR is working:
1. Upload test images
2. Verify parameter extraction works
3. Check dashboard displays reports correctly
4. (Optional) Install Poppler for PDF support
