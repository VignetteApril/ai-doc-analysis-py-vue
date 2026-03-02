@echo off
REM AI Document Analysis System - Local Development Start Script (Windows)
REM Used to start both frontend and backend services

echo Starting AI Document Analysis System development environment
echo ===============================================

REM Check if in project root directory
if not exist "docker-compose.yml" (
    echo ERROR: Please run this script from the project root directory
    pause
    exit /b 1
)

REM Start backend service (Docker Compose)
echo Starting backend service...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ERROR: Backend service failed to start
    pause
    exit /b 1
)

echo Backend service started successfully (http://localhost:8000)

REM Start frontend service
echo Starting frontend service...
cd frontend
if %errorlevel% neq 0 (
    echo ERROR: Frontend directory not found
    cd ..
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
)

REM Start development server
echo Starting frontend development server...
start "Frontend Dev Server" cmd /c "npm run dev"

cd ..

echo Frontend service started successfully (http://localhost:5173 or other available port)
echo.
echo Service URLs:
echo    Backend API: http://localhost:8000
echo    Frontend UI: http://localhost:5173
echo.
echo Usage Instructions:
echo    - Close the frontend command window to stop frontend service
echo    - To stop backend service, run: docker-compose down
echo.

pause