@echo off
REM AI Document Analysis System - Run Backend Tests in Docker (Windows)
REM This script runs all backend tests inside the Docker container

echo Running AI Document Analysis System Backend Tests in Docker
echo =========================================================

REM Check if in project root directory
if not exist "docker-compose.yml" (
    echo ERROR: Please run this script from the project root directory
    pause
    exit /b 1
)

REM Check if Docker Compose services are running
echo Checking if Docker services are running...
docker-compose ps -q backend >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Docker services...
    docker-compose up -d
    if %errorlevel% neq 0 (
        echo ERROR: Failed to start Docker services
        pause
        exit /b 1
    )
    echo Waiting for services to be ready...
    timeout /t 10 /nobreak >nul
)

REM Run tests inside the Docker container
echo Running tests inside Docker container...
docker-compose exec backend python -m pytest tests/ -v

if %errorlevel% neq 0 (
    echo ERROR: Tests failed
    pause
    exit /b 1
)

echo Tests completed successfully!
pause