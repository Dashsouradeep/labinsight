@echo off
REM LabInsight Startup Script for Windows
REM This script starts all services using Docker Compose

echo.
echo Starting LabInsight...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo Docker is running
echo.

REM Start services
echo Starting services with Docker Compose...
docker-compose up -d

REM Wait for services to be ready
echo.
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check service status
echo.
echo Service Status:
docker-compose ps

echo.
echo LabInsight is starting up!
echo.
echo Access the application:
echo    Frontend:  http://localhost:3000
echo    Backend:   http://localhost:8000
echo    API Docs:  http://localhost:8000/docs
echo.
echo To view logs:
echo    docker-compose logs -f
echo.
echo To stop all services:
echo    docker-compose down
echo.
pause
