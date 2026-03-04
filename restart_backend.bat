@echo off
echo ========================================
echo Restarting Backend with Tesseract OCR
echo ========================================
echo.

cd /d E:\EHR_Reviewer\backend

echo Activating virtual environment...
call E:\EHR_Reviewer\.venv\Scripts\activate.bat

echo.
echo Starting backend server on port 8000...
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn main:app --reload --port 8000
