# Temporary Solution: Use Mock OCR

If you want to test the system immediately without installing Tesseract, you can temporarily use the mock OCR service.

## Quick Switch to Mock OCR

Run this command to switch to mock OCR:

```cmd
cd E:\EHR_Reviewer\backend
python switch_to_mock_ocr.py
```

This will:
1. Update `processing_pipeline.py` to use mock OCR
2. Let you test the full system flow
3. Show you how the dashboard looks with data

## What Mock OCR Does

The mock OCR service:
- Returns realistic sample lab report text
- Includes common parameters (glucose, cholesterol, etc.)
- Allows you to test the complete pipeline
- Shows you what the final system will look like

## Switch Back to Real OCR

Once you install Tesseract, run:

```cmd
cd E:\EHR_Reviewer\backend
python switch_to_real_ocr.py
```

## Install Real OCR Later

When you're ready for real OCR:

### Option 1: Automated (Recommended)
```powershell
powershell -ExecutionPolicy Bypass -File install_tesseract.ps1
```

### Option 2: Manual
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR`
3. Add to PATH
4. Restart terminal
5. Run: `python switch_to_real_ocr.py`
