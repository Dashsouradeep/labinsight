@echo off
echo ========================================
echo Starting LabInsight Backend Server
echo ========================================
echo.
cd backend
python -m uvicorn main:app --reload --port 8000
