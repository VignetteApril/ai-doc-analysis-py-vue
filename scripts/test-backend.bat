@echo off
REM AI Document Analysis System - Run Backend Tests (Windows)
REM This script runs all backend tests using pytest

echo Running AI Document Analysis System Backend Tests
echo ===============================================

REM Check if in project root directory
if not exist "backend\app" (
    echo ERROR: Please run this script from the project root directory
    pause
    exit /b 1
)

REM Change to backend directory
cd backend

REM Install dependencies if needed
echo Installing backend dependencies...
pip install -r requirements.txt

REM Run tests
echo Running tests...
python -m pytest tests/ -v

REM Return to original directory
cd ..

echo Tests completed!
pause